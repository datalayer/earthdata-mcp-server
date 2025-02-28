<!--
  ~ Copyright (c) 2023-2024 Datalayer, Inc.
  ~
  ~ BSD 3-Clause License
-->

[![Datalayer](https://assets.datalayer.tech/datalayer-25.svg)](https://datalayer.io)

[![Become a Sponsor](https://img.shields.io/static/v1?label=Become%20a%20Sponsor&message=%E2%9D%A4&logo=GitHub&style=flat&color=1ABC9C)](https://github.com/sponsors/datalayer)

# 🪐 ✨ Earthdata MCP Server

[![Github Actions Status](https://github.com/datalayer/earthdata-mcp-server/workflows/Build/badge.svg)](https://github.com/datalayer/earthdata-mcp-server/actions/workflows/build.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/earthdata-mcp-server)](https://pypi.org/project/earthdata-mcp-server)

Earthdata MCP Server is a [Model Context Protocol](https://modelcontextprotocol.io/introduction) (MCP) server implementation that provides tools to interact with [NASA Earth Data](https://www.earthdata.nasa.gov/). It enables efficient dataset discovery and retrieval for Geospatial analysis.

<div style="position: relative; padding-bottom: 56.25%; height: 0;"><iframe src="https://www.loom.com/embed/c2b5b05f548d4f1492d5c107f0c48dbc?sid=eef010ce-6be8-4a1b-b3ba-5c2e6a5bf8d0" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe></div>

## Usage with Claude Desktop

To use this with Claude Desktop, add the following to your claude_desktop_config.json:

```json
{
  "mcpServers": {
    "earthdata": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "datalayer/earthdata-mcp-server:latest"
      ]
    }
  }
}
```

## Components

### Tools

The server currently offers 2 tools:

1. `search_earth_datasets`
- Search for datasets on NASA Earthdata.
- Input:
  - search_keywords (str): Keywords to search for in the dataset titles.
  - count (int): Number of datasets to return.
  - temporal (tuple): (Optional) Temporal range in the format (date_from, date_to).
  - bounding_box (tuple): (Optional) Bounding box in the format (lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat).
- Returns: List of dataset abstracts.

2. `search_earth_datagranules`
- Search for data granules on NASA Earthdata.
- Input:
  - short_name (str): Short name of the dataset.
  - count (int): Number of data granules to return.
  - temporal (tuple): (Optional) Temporal range in the format (date_from, date_to).
  - bounding_box (tuple): (Optional) Bounding box in the format (lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat).
- Returns: List of data granules.
        
## Building from Source

```bash
docker build -t datalayer/earthdata-mcp-server .
```