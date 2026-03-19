# Copyright (c) 2023-2024 Datalayer, Inc.
#
# BSD 3-Clause License

import logging
from pathlib import Path
from typing import Any

import click
import uvicorn
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware

import earthaccess


###############################################################################


class FastMCPWithCORS(FastMCP):
    def streamable_http_app(self) -> Starlette:
        """Return StreamableHTTP server app with CORS middleware
        See: https://github.com/modelcontextprotocol/python-sdk/issues/187
        """
        # Get the original Starlette app
        app = super().streamable_http_app()
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, should set specific domains
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )        
        return app
    
    def sse_app(self, mount_path: str | None = None) -> Starlette:
        """Return SSE server app with CORS middleware"""
        # Get the original Starlette app
        app = super().sse_app(mount_path)
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, should set specific domains
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )        
        return app


# Keep this server focused on Earthdata only.
# If users need notebook/runtime tools they should compose with jupyter-mcp-server via mcp-compose.
mcp = FastMCPWithCORS("earthdata")

logger = logging.getLogger(__name__)


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
        search_params["temporal"] = temporal
    if bounding_box and len(bounding_box) == 4:
        search_params["bounding_box"] = bounding_box
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
    return f"""import os

import earthaccess

earthaccess.login(strategy=\"environment\")

search_params = {search_params}
results = earthaccess.search_data(**search_params)

os.makedirs(\"{folder_name}\", exist_ok=True)
files = earthaccess.download(results, \"{folder_name}\")
print(f\"Downloaded {{len(files)}} files to {folder_name}\")
"""


@mcp.tool()
def search_earth_datasets(search_keywords: str, count: int, temporal: tuple | None, bounding_box: tuple | None) -> list:
    """
    Search for datasets on NASA Earthdata.
    
    Args:
    search_keywords: Keywords to search for in the dataset titles.
    count: Number of datasets to return.
    temporal: (Optional) Temporal range in the format (date_from, date_to).
    bounding_box: (Optional) Bounding box in the format (lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat).
        
    Returns:
    list
        List of dataset abstracts.
    """

    search_params = {
        "keyword": search_keywords,
        "count": count,
        "cloud_hosted": True
    }

    if temporal and len(temporal) == 2:
        search_params["temporal"] = temporal
    if bounding_box and len(bounding_box) == 4:
        search_params["bounding_box"] = bounding_box

    datasets = earthaccess.search_datasets(**search_params)  # type: ignore[arg-type]

    datasets_info = [
        {
            "Title": dataset.get_umm("EntryTitle"), 
            "ShortName": dataset.get_umm("ShortName"), 
            "Abstract": dataset.abstract(), 
            "Data Type": dataset.data_type(), 
            "DOI": dataset.get_umm("DOI"),
            "LandingPage": dataset.landing_page(),
            "DatasetViz": dataset._filter_related_links("GET RELATED VISUALIZATION"),
            "DatasetURL": dataset._filter_related_links("GET DATA"),
         } for dataset in datasets]

    return datasets_info


@mcp.tool()
def search_earth_datagranules(short_name: str, count: int, temporal: tuple | None, bounding_box: tuple | None) -> list:
    """
    Search for data granules on NASA Earthdata.
    
    Args:
    short_name: Short name of the dataset.
    count: Number of data granules to return.
    temporal: (Optional) Temporal range in the format (date_from, date_to).
    bounding_box: (Optional) Bounding box in the format (lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat).
        
    Returns:
    list
        List of data granules.
    """
    
    search_params = {
        "short_name": short_name,
        "count": count,
        "cloud_hosted": True
    }

    if temporal and len(temporal) == 2:
        search_params["temporal"] = temporal
    if bounding_box and len(bounding_box) == 4:
        search_params["bounding_box"] = bounding_box

    datagranules = earthaccess.search_data(**search_params)  # type: ignore[arg-type]
    
    return datagranules


@mcp.tool()
def download_earth_data_granules(
    folder_name: str,
    short_name: str,
    count: int,
    temporal: tuple | None = None,
    bounding_box: tuple | None = None,
    mode: str = "manifest",
    max_manifest_items: int = 20,
) -> dict[str, Any]:
    """Search and optionally download Earthdata granules.

    Modes:
    - manifest: return searchable granule metadata, no download performed.
    - download: download files immediately to folder_name on this server.
    - script: return a Python script that can be executed by a composed runtime.
    """
    allowed_modes = {"manifest", "download", "script"}
    if mode not in allowed_modes:
        raise ValueError(
            f"Invalid mode '{mode}'. Use one of: {sorted(allowed_modes)}."
        )
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
            "hint": "Use this script with jupyter-mcp-server through mcp-compose for notebook-driven downloads.",
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
            "items": [_granule_to_manifest_item(granule, idx) for idx, granule in enumerate(limited)],
            "truncated": total_found > max_manifest_items,
            "download_folder": folder_name,
        }

    output_dir = Path(folder_name)
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

@mcp.prompt()
def download_analyze_global_sea_level() -> str:
    """Generate a prompt for downloading and analyzing Global Mean Sea Level Trend dataset."""
    return (
        "I want to analyze the Global Mean Sea Level Trend dataset. "
        "First call download_earth_data_granules with mode='script' to generate a reproducible script, "
        "then execute it in a notebook runtime composed via mcp-compose with jupyter-mcp-server. "
        "After the data is available, produce a concise trend analysis with at least one visualization."
    )


@mcp.prompt()
def sealevel_rise_dataset(start_year: int, end_year: int) -> str:
    return f"I’m interested in datasets about sealevel rise worldwide from {start_year} to {end_year}. Can you list relevant datasets?"


@mcp.prompt()
def ask_datasets_format() -> str:
    return "What are the data formats of those datasets?"


###############################################################################
# Commands.


@click.group()
def server():
    """Manages Earthdata MCP Server."""
    pass


@server.command("start")
@click.option(
    "--transport",
    envvar="TRANSPORT",
    type=click.Choice(["stdio", "streamable-http"]),
    default="stdio",
    help="The transport to use for the MCP server. Defaults to 'stdio'.",
)
@click.option(
    "--port",
    envvar="PORT",
    type=click.INT,
    default=4040,
    help="The port to use for the Streamable HTTP transport. Ignored for stdio transport.",
)
def start_command(
    transport: str,
    port: int,
) -> None:
    """Start the Earthdata MCP server with a transport."""

    logger.info("Starting Earthdata MCP Server with transport: %s", transport)
    logger.info("Available tools: %s", list(mcp._tool_manager._tools.keys()))

    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "streamable-http":
        uvicorn.run(mcp.streamable_http_app(), host="0.0.0.0", port=port)  # noqa: S104
    else:
        raise Exception("Transport should be `stdio` or `streamable-http`.")


###############################################################################
# Main.


if __name__ == "__main__":
    server()
