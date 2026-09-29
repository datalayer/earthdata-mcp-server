#!/usr/bin/env python3
# Copyright (c) 2023-2026 Datalayer, Inc.
#
# BSD 3-Clause License

"""Earthdata MCP Server workflow example.

This script calls the extension's tools directly, without a server:
1. Discover datasets
2. Inspect granules in manifest mode
3. Generate a download script to run in a notebook or a code sandbox
"""

import asyncio

from earthdata_mcp_server import EarthdataExtension

SHORT_NAME = "TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.4"


async def main() -> None:
    earthdata = EarthdataExtension()
    print("== Earthdata MCP Example ==")

    datasets = await earthdata.search_earth_datasets(
        search_keywords="sea level",
        count=3,
        temporal=("2020-01-01", "2025-01-01"),
    )
    print(f"Found datasets: {len(datasets)}")

    manifest = await earthdata.download_earth_data_granules(
        folder_name="downloads/sea_level",
        short_name=SHORT_NAME,
        count=5,
        mode="manifest",
        max_manifest_items=3,
    )
    print(f"Manifest results: {manifest['returned']} / {manifest['total_found']}")

    script_result = await earthdata.download_earth_data_granules(
        folder_name="downloads/sea_level",
        short_name=SHORT_NAME,
        count=5,
        mode="script",
    )
    print("Generated script preview:")
    print("-" * 60)
    print("\n".join(script_result["script"].splitlines()[:12]))
    print("...")


if __name__ == "__main__":
    asyncio.run(main())
