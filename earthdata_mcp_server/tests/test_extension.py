# Copyright (c) 2023-2026 Datalayer, Inc.
#
# BSD 3-Clause License

"""The Earthdata extension, on a reactor_mcp_server host and called directly."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import earthaccess
import pytest
from reactor_mcp_server import build_host, parse_selection

from earthdata_mcp_server import extension as earthdata
from earthdata_mcp_server.extension import TOOLSET, EarthdataExtension

TOOLS = {
    "search_earth_datasets",
    "search_earth_datagranules",
    "download_earth_data_granules",
}


def download(**arguments: Any) -> dict[str, Any]:
    return asyncio.run(EarthdataExtension().download_earth_data_granules(**arguments))


# --- On a host --------------------------------------------------------------


def test_the_toolset_is_opt_in_on_a_shared_host() -> None:
    host = build_host([earthdata.extension()], name="tests")
    assert not set(host.build().tool_names) & TOOLS
    assert set(host.build(parse_selection(TOOLSET)).tool_names) == TOOLS


def test_the_toolset_is_on_when_served_alone() -> None:
    host = build_host([EarthdataExtension(default=True)], name="tests")
    assert set(host.build().tool_names) == TOOLS


def test_every_tool_says_how_it_behaves() -> None:
    host = build_host([EarthdataExtension(default=True)], name="tests")
    for spec in host.build().tools:
        annotations = spec.annotations
        assert spec.documentation, spec.name
        assert annotations.open_world_hint is True, spec.name
        assert annotations.destructive_hint is False, spec.name
        assert annotations.idempotent_hint is True, spec.name
        assert annotations.read_only_hint is (spec.name != "download_earth_data_granules")


def test_the_prompts_are_served_with_the_toolset() -> None:
    host = build_host([EarthdataExtension(default=True)], name="tests")
    prompts = asyncio.run(host.build().server.list_prompts())
    assert {prompt.name for prompt in prompts} == {
        "download_analyze_global_sea_level",
        "sealevel_rise_dataset",
        "ask_datasets_format",
    }


def test_no_prompts_without_the_toolset() -> None:
    host = build_host([earthdata.extension()], name="tests")
    assert asyncio.run(host.build().server.list_prompts()) == []


# --- Called directly --------------------------------------------------------


def test_download_mode_validation_invalid_mode() -> None:
    with pytest.raises(ValueError, match="Invalid mode"):
        download(folder_name="downloads/test", short_name="TEST", count=1, mode="invalid-mode")


def test_download_mode_validation_manifest_limit() -> None:
    with pytest.raises(ValueError, match="max_manifest_items"):
        download(
            folder_name="downloads/test",
            short_name="TEST",
            count=1,
            mode="manifest",
            max_manifest_items=0,
        )


def test_download_script_mode() -> None:
    result = download(folder_name="downloads/test", short_name="TEST", count=2, mode="script")
    assert result["mode"] == "script"
    assert "earthaccess.search_data" in result["script"]
    assert "downloads/test" in result["script"]
    assert "mcp-compose" in result["hint"]


def test_download_manifest_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_results = [
        {"id": "g1", "title": "Granule 1", "links": ["https://example.com/1"]},
        {"id": "g2", "title": "Granule 2", "links": ["https://example.com/2"]},
        {"id": "g3", "title": "Granule 3", "links": ["https://example.com/3"]},
    ]
    monkeypatch.setattr(earthaccess, "search_data", lambda **_: fake_results)

    result = download(
        folder_name="downloads/test",
        short_name="TEST",
        count=10,
        mode="manifest",
        max_manifest_items=2,
    )
    assert result["mode"] == "manifest"
    assert result["total_found"] == 3
    assert result["returned"] == 2
    assert result["truncated"] is True
    assert result["items"][0]["id"] == "g1"


def test_download_mode_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    fake_results = [{"id": "g1"}, {"id": "g2"}]
    fake_files = [str(tmp_path / "a.nc"), str(tmp_path / "b.nc")]
    monkeypatch.setattr(earthdata, "BASE_DOWNLOAD_DIR", tmp_path / "earthdata_downloads")
    monkeypatch.setattr(earthaccess, "search_data", lambda **_: fake_results)
    monkeypatch.setattr(earthaccess, "login", lambda **_: object())
    monkeypatch.setattr(earthaccess, "download", lambda *_: fake_files)

    folder_name = "unit-test-downloads"
    result = download(folder_name=folder_name, short_name="TEST", count=2, mode="download")
    assert result["mode"] == "download"
    assert result["downloaded_count"] == 2
    assert result["output_dir"] == str((tmp_path / "earthdata_downloads" / folder_name).resolve())
    assert result["files"] == fake_files


def test_download_refuses_a_folder_outside_its_base(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(earthdata, "BASE_DOWNLOAD_DIR", tmp_path / "earthdata_downloads")
    monkeypatch.setattr(earthaccess, "search_data", lambda **_: [{"id": "g1"}])
    with pytest.raises(ValueError, match="path traversal"):
        download(folder_name="../elsewhere", short_name="TEST", count=1, mode="download")


def test_download_mode_auth_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(earthdata, "BASE_DOWNLOAD_DIR", tmp_path / "earthdata_downloads")
    monkeypatch.setattr(earthaccess, "search_data", lambda **_: [{"id": "g1"}])

    def _raise_login(**_: object) -> None:
        raise RuntimeError("auth failed")

    monkeypatch.setattr(earthaccess, "login", _raise_login)

    with pytest.raises(RuntimeError, match="Earthdata authentication failed"):
        download(folder_name="downloads/test", short_name="TEST", count=1, mode="download")


def test_search_passes_filters_as_tuples(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, Any] = {}

    def _search(**params: Any) -> list[Any]:
        seen.update(params)
        return []

    monkeypatch.setattr(earthaccess, "search_data", _search)
    found = asyncio.run(
        EarthdataExtension().search_earth_datagranules(
            short_name="TEST",
            count=3,
            temporal=("2020-01-01", "2020-12-31"),
            bounding_box=(0, 0, 1, 1),
        )
    )
    assert found == []
    assert seen["temporal"] == ("2020-01-01", "2020-12-31")
    assert seen["bounding_box"] == (0, 0, 1, 1)
