# Copyright (c) 2023-2026 Datalayer, Inc.
#
# BSD 3-Clause License

"""The Earthdata extension: NASA Earthdata search and download, as one toolset.

A `reactor_mcp_server` extension. Installed beside any host of that foundation
— the ``reactor-mcp-server`` command, a hosted gateway — it is discovered on
the ``reactor.mcp.extensions`` entry-point group and served to a client that
asks for it by name (``/mcp?earthdata``). The ``earthdata-mcp-server`` command
serves it on its own, where it is on without asking.

Searching is anonymous. Downloading needs a NASA Earthdata Login, read from
``EARTHDATA_USERNAME`` and ``EARTHDATA_PASSWORD``.

@module earthdata_mcp_server.extension
"""

from __future__ import annotations

import functools
import logging
import pprint
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import anyio
import earthaccess
from mcp.types import ToolAnnotations
from reactor import PluginCompatibility, PluginManifest
from reactor_mcp_server import McpExtension, Toolset, on_toolset, tool

from earthdata_mcp_server.__version__ import __version__

logger = logging.getLogger(__name__)

#: The toolset a client names in its URL: ``/mcp?earthdata``.
TOOLSET = "earthdata"

#: The modes `download_earth_data_granules` understands.
DOWNLOAD_MODES = ("manifest", "download", "script")

# Base directory under which all downloads will be stored. User-supplied
# folder names are interpreted as subdirectories of this path.
BASE_DOWNLOAD_DIR = Path.cwd() / "earthdata_downloads"


def _annotations(title: str, *, read_only: bool) -> ToolAnnotations:
    # Every tool reads NASA's catalogue, which this server does not own, so all
    # three are open-world. Asking twice answers the same, and nothing here
    # deletes anything.
    return ToolAnnotations(
        title=title,
        read_only_hint=read_only,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=True,
    )


SEARCH_DATASETS_ANNOTATIONS = _annotations("Search Earthdata Datasets", read_only=True)
SEARCH_GRANULES_ANNOTATIONS = _annotations("Search Earthdata Granules", read_only=True)
# Not read-only: in `download` mode it writes files where the server runs.
DOWNLOAD_GRANULES_ANNOTATIONS = _annotations("Download Earthdata Granules", read_only=False)


def _get_safe_output_dir(folder_name: str) -> Path:
    """
    Return a filesystem path for downloads that is safely constrained under
    BASE_DOWNLOAD_DIR. Reject absolute paths and directory traversal.
    """
    base = BASE_DOWNLOAD_DIR.resolve()

    try:
        if folder_name:
            candidate = (base / folder_name).resolve()
        else:
            candidate = base
    except Exception as exc:  # Defensive: malformed paths, etc.
        raise ValueError("Invalid folder_name for download directory.") from exc

    # Ensure the resolved path is under the base directory.
    if candidate == base or base in candidate.parents:
        return candidate

    raise ValueError("Invalid folder_name: path traversal outside base directory is not allowed.")


def _build_search_params(
    short_name: str,
    count: int,
    temporal: tuple | None,
    bounding_box: tuple | None,
) -> dict[str, Any]:
    search_params: dict[str, Any] = {
        "short_name": short_name,
        "count": count,
        "cloud_hosted": True,
    }
    if temporal and len(temporal) == 2:
        search_params["temporal"] = tuple(temporal)
    if bounding_box and len(bounding_box) == 4:
        search_params["bounding_box"] = tuple(bounding_box)
    return search_params


def _granule_to_manifest_item(granule: Any, index: int) -> dict[str, Any]:
    if isinstance(granule, dict):
        title = granule.get("title") or granule.get("id") or "unknown"
        granule_id = granule.get("id") or granule.get("native-id") or f"granule-{index + 1}"
        links = granule.get("links") or []
    else:
        title = getattr(granule, "title", None) or str(granule)
        granule_id = getattr(granule, "id", None) or f"granule-{index + 1}"
        links = getattr(granule, "data_links", None) or []

    return {
        "index": index + 1,
        "id": str(granule_id),
        "title": str(title),
        "links": [str(link) for link in links[:5]],
    }


def _build_download_script(folder_name: str, search_params: dict[str, Any]) -> str:
    folder_name_literal = repr(folder_name)
    search_params_literal = pprint.pformat(search_params, indent=4)
    return f"""import os

import earthaccess

earthaccess.login(strategy=\"environment\")

search_params = {search_params_literal}
results = earthaccess.search_data(**search_params)

folder_name = {folder_name_literal}
os.makedirs(folder_name, exist_ok=True)
files = earthaccess.download(results, folder_name)
print(f\"Downloaded {{len(files)}} files to {{folder_name}}\")
"""


#: What `script` mode says to do with its script.
SCRIPT_HINT = (
    "Run this script where the data should land: a notebook or a code sandbox "
    "reached through another MCP server, for example jupyter-mcp-server "
    "composed with this one through mcp-compose."
)


def search_datasets(
    search_keywords: str,
    count: int,
    temporal: tuple | None = None,
    bounding_box: tuple | None = None,
) -> list[dict[str, Any]]:
    """Search NASA Earthdata for datasets, blocking."""
    search_params: dict[str, Any] = {
        "keyword": search_keywords,
        "count": count,
        "cloud_hosted": True,
    }
    if temporal and len(temporal) == 2:
        search_params["temporal"] = tuple(temporal)
    if bounding_box and len(bounding_box) == 4:
        search_params["bounding_box"] = tuple(bounding_box)

    datasets = earthaccess.search_datasets(**search_params)
    return [
        {
            "Title": dataset.get_umm("EntryTitle"),
            "ShortName": dataset.get_umm("ShortName"),
            "Abstract": dataset.abstract(),
            "Data Type": dataset.data_type(),
            "DOI": dataset.get_umm("DOI"),
            "LandingPage": dataset.landing_page(),
            "DatasetViz": dataset._filter_related_links("GET RELATED VISUALIZATION"),
            "DatasetURL": dataset._filter_related_links("GET DATA"),
        }
        for dataset in datasets
    ]


def search_granules(
    short_name: str,
    count: int,
    temporal: tuple | None = None,
    bounding_box: tuple | None = None,
) -> list[Any]:
    """Search NASA Earthdata for a dataset's granules, blocking."""
    search_params = _build_search_params(short_name, count, temporal, bounding_box)
    return list(earthaccess.search_data(**search_params))


def download_granules(
    folder_name: str,
    short_name: str,
    count: int,
    temporal: tuple | None = None,
    bounding_box: tuple | None = None,
    mode: str = "manifest",
    max_manifest_items: int = 20,
) -> dict[str, Any]:
    """Search, then describe, download or script the granules found, blocking."""
    if mode not in DOWNLOAD_MODES:
        raise ValueError(f"Invalid mode '{mode}'. Use one of: {sorted(DOWNLOAD_MODES)}.")
    if max_manifest_items < 1:
        raise ValueError("max_manifest_items must be >= 1.")

    logger.info("Preparing Earthdata granule operation for '%s' in mode '%s'", short_name, mode)
    search_params = _build_search_params(short_name, count, temporal, bounding_box)

    if mode == "script":
        return {
            "mode": mode,
            "search_params": search_params,
            "folder_name": folder_name,
            "script": _build_download_script(folder_name, search_params),
            "hint": SCRIPT_HINT,
        }

    results = earthaccess.search_data(**search_params)
    total_found = len(results)

    if mode == "manifest":
        limited = results[:max_manifest_items]
        return {
            "mode": mode,
            "search_params": search_params,
            "total_found": total_found,
            "returned": len(limited),
            "items": [
                _granule_to_manifest_item(granule, idx) for idx, granule in enumerate(limited)
            ],
            "truncated": total_found > max_manifest_items,
            "download_folder": folder_name,
        }

    output_dir = _get_safe_output_dir(folder_name)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Prefer environment credentials for non-interactive server contexts.
        earthaccess.login(strategy="environment")
    except Exception as exc:
        raise RuntimeError(
            "Earthdata authentication failed. Set EARTHDATA_USERNAME and EARTHDATA_PASSWORD."
        ) from exc

    files = earthaccess.download(results, str(output_dir))
    return {
        "mode": mode,
        "search_params": search_params,
        "total_found": total_found,
        "downloaded_count": len(files),
        "output_dir": str(output_dir),
        "files": [str(Path(file_path)) for file_path in files],
    }


async def _off_the_loop(function: Callable[..., Any], /, **arguments: Any) -> Any:
    # earthaccess is synchronous and talks to NASA over the network: run on the
    # event loop, one slow search would stall every other session this server
    # holds.
    return await anyio.to_thread.run_sync(functools.partial(function, **arguments))


# --- Prompts ----------------------------------------------------------------


def download_analyze_global_sea_level() -> str:
    """Generate a prompt for downloading and analyzing Global Mean Sea Level Trend dataset."""
    return (
        "I want to analyze the Global Mean Sea Level Trend dataset. "
        "First call download_earth_data_granules with mode='script' to generate a "
        "reproducible script, then execute it in a notebook or a code sandbox. "
        "After the data is available, produce a concise trend analysis with at least "
        "one visualization."
    )


def sealevel_rise_dataset(start_year: int, end_year: int) -> str:
    """Ask for datasets about sea level rise worldwide between two years."""
    return (
        "I'm interested in datasets about sealevel rise worldwide "
        f"from {start_year} to {end_year}. Can you list relevant datasets?"
    )


def ask_datasets_format() -> str:
    """Ask for the data formats of the datasets found."""
    return "What are the data formats of those datasets?"


PROMPTS = (download_analyze_global_sea_level, sealevel_rise_dataset, ask_datasets_format)


def register_prompts(server: Any) -> None:
    """Put the Earthdata prompts on a server."""
    for prompt in PROMPTS:
        server.prompt(name=prompt.__name__)(prompt)


# --- The extension ------------------------------------------------------------


class EarthdataExtension(McpExtension):
    """NASA Earthdata search and download, as the ``earthdata`` toolset.

    ``default`` says whether a client that names no toolset gets it. A host
    shared with other extensions leaves it off, so a client that did not ask
    for Earthdata does not read three more tool descriptions, and the
    extension is only woken by a URL that names it. A server that is nothing
    but Earthdata turns it on.
    """

    def __init__(self, *, default: bool = False) -> None:
        self._default = default

    def manifest(self) -> PluginManifest:
        return PluginManifest(
            name="earthdata",
            version=__version__,
            description="Search NASA Earthdata for datasets and granules, and download them.",
            author="Datalayer",
            tags=["earthdata", "nasa", "earth-science", "datasets"],
            # Opt-in: registered, but not woken until a URL names the toolset.
            activation_events=[] if self._default else [on_toolset(TOOLSET)],
            compatibility=PluginCompatibility(api_version="v1"),
        )

    def toolsets(self) -> Sequence[Toolset]:
        return (
            Toolset(
                name=TOOLSET,
                description="Search NASA Earthdata for datasets and granules, and download them.",
                default=self._default,
            ),
        )

    def prompts(self) -> Sequence[Any]:
        return (register_prompts,)

    @tool(annotations=SEARCH_DATASETS_ANNOTATIONS)
    async def search_earth_datasets(
        self,
        search_keywords: str,
        count: int,
        temporal: tuple[str, str] | None = None,
        bounding_box: tuple[float, float, float, float] | None = None,
    ) -> list[dict[str, Any]]:
        """Search for datasets on NASA Earthdata.

        Args:
            search_keywords: Keywords to search for in the dataset titles.
            count: Number of datasets to return.
            temporal: (Optional) Temporal range in the format (date_from, date_to).
            bounding_box: (Optional) Bounding box in the format
                (lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat).

        Returns:
            The datasets found: title, short name, abstract, data type, DOI,
            landing page, visualization and data links.
        """
        return await _off_the_loop(
            search_datasets,
            search_keywords=search_keywords,
            count=count,
            temporal=temporal,
            bounding_box=bounding_box,
        )

    @tool(annotations=SEARCH_GRANULES_ANNOTATIONS)
    async def search_earth_datagranules(
        self,
        short_name: str,
        count: int,
        temporal: tuple[str, str] | None = None,
        bounding_box: tuple[float, float, float, float] | None = None,
    ) -> list[Any]:
        """Search for data granules on NASA Earthdata.

        Args:
            short_name: Short name of the dataset.
            count: Number of data granules to return.
            temporal: (Optional) Temporal range in the format (date_from, date_to).
            bounding_box: (Optional) Bounding box in the format
                (lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat).

        Returns:
            The data granules found.
        """
        return await _off_the_loop(
            search_granules,
            short_name=short_name,
            count=count,
            temporal=temporal,
            bounding_box=bounding_box,
        )

    @tool(annotations=DOWNLOAD_GRANULES_ANNOTATIONS)
    async def download_earth_data_granules(
        self,
        folder_name: str,
        short_name: str,
        count: int,
        temporal: tuple[str, str] | None = None,
        bounding_box: tuple[float, float, float, float] | None = None,
        mode: str = "manifest",
        max_manifest_items: int = 20,
    ) -> dict[str, Any]:
        """Search Earthdata granules, then describe, download or script them.

        Modes:
        - manifest: return searchable granule metadata, no download performed.
        - download: download files immediately to folder_name on this server.
          Needs EARTHDATA_USERNAME and EARTHDATA_PASSWORD where the server runs.
        - script: return a Python script that performs the same search and
          download, to run in a notebook or a code sandbox.

        Start with manifest to check what a query matches before downloading.
        """
        return await _off_the_loop(
            download_granules,
            folder_name=folder_name,
            short_name=short_name,
            count=count,
            temporal=temporal,
            bounding_box=bounding_box,
            mode=mode,
            max_manifest_items=max_manifest_items,
        )


def extension() -> EarthdataExtension:
    """The entry point ``reactor.mcp.extensions`` loads: opt-in, ``/mcp?earthdata``."""
    return EarthdataExtension()
