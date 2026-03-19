#!/usr/bin/env python3
"""Earthdata MCP Server workflow example.

This script demonstrates Earthdata-only usage patterns:
1. Discover datasets
2. Inspect granules in manifest mode
3. Generate a download script for composed runtimes (mcp-compose + jupyter-mcp-server)
"""

from earthdata_mcp_server import server as earthdata_server


def main() -> None:
    print("== Earthdata MCP Example ==")

    datasets = earthdata_server.search_earth_datasets(
        search_keywords="sea level",
        count=3,
        temporal=("2020-01-01", "2025-01-01"),
        bounding_box=None,
    )
    print(f"Found datasets: {len(datasets)}")

    manifest = earthdata_server.download_earth_data_granules(
        folder_name="downloads/sea_level",
        short_name="TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.4",
        count=5,
        mode="manifest",
        max_manifest_items=3,
    )
    print(f"Manifest results: {manifest['returned']} / {manifest['total_found']}")

    script_result = earthdata_server.download_earth_data_granules(
        folder_name="downloads/sea_level",
        short_name="TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.4",
        count=5,
        mode="script",
    )
    print("Generated script preview:")
    print("-" * 60)
    print("\n".join(script_result["script"].splitlines()[:12]))
    print("...")


if __name__ == "__main__":
    main()
