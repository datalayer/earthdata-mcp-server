"""Unit tests for Earthdata MCP Server download and tool composition behavior."""

from pathlib import Path

import pytest

from earthdata_mcp_server import server as earthdata_server


def test_tool_registration() -> None:
    tools = set(earthdata_server.mcp._tool_manager._tools.keys())
    expected_tools = {
        "search_earth_datasets",
        "search_earth_datagranules",
        "download_earth_data_granules",
    }
    assert expected_tools.issubset(tools)


def test_download_mode_validation_invalid_mode() -> None:
    with pytest.raises(ValueError, match="Invalid mode"):
        earthdata_server.download_earth_data_granules(
            folder_name="downloads/test",
            short_name="TEST",
            count=1,
            mode="invalid-mode",
        )


def test_download_mode_validation_manifest_limit() -> None:
    with pytest.raises(ValueError, match="max_manifest_items"):
        earthdata_server.download_earth_data_granules(
            folder_name="downloads/test",
            short_name="TEST",
            count=1,
            mode="manifest",
            max_manifest_items=0,
        )


def test_download_script_mode() -> None:
    result = earthdata_server.download_earth_data_granules(
        folder_name="downloads/test",
        short_name="TEST",
        count=2,
        mode="script",
    )
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

    monkeypatch.setattr(earthdata_server.earthaccess, "search_data", lambda **_: fake_results)

    result = earthdata_server.download_earth_data_granules(
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

    monkeypatch.setattr(earthdata_server.earthaccess, "search_data", lambda **_: fake_results)
    monkeypatch.setattr(earthdata_server.earthaccess, "login", lambda **_: object())
    monkeypatch.setattr(earthdata_server.earthaccess, "download", lambda *_: fake_files)

    folder_name = "unit-test-downloads"
    expected_out_dir = (earthdata_server.BASE_DOWNLOAD_DIR.resolve() / folder_name).resolve()
    result = earthdata_server.download_earth_data_granules(
        folder_name=folder_name,
        short_name="TEST",
        count=2,
        mode="download",
    )
    assert result["mode"] == "download"
    assert result["downloaded_count"] == 2
    assert result["output_dir"] == str(expected_out_dir)
    assert result["files"] == fake_files


def test_download_mode_auth_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(earthdata_server.earthaccess, "search_data", lambda **_: [{"id": "g1"}])

    def _raise_login(**_: object) -> None:
        raise RuntimeError("auth failed")

    monkeypatch.setattr(earthdata_server.earthaccess, "login", _raise_login)

    with pytest.raises(RuntimeError, match="Earthdata authentication failed"):
        earthdata_server.download_earth_data_granules(
            folder_name="downloads/test",
            short_name="TEST",
            count=1,
            mode="download",
        )
