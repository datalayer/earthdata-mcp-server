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
[![smithery badge](https://smithery.ai/badge/@datalayer/earthdata-mcp-server)](https://smithery.ai/server/@datalayer/earthdata-mcp-server)

Earthdata MCP Server is a [Model Context Protocol](https://modelcontextprotocol.io/introduction) (MCP) server implementation that provides tools to interact with [NASA Earth Data](https://www.earthdata.nasa.gov/). It enables efficient dataset discovery and retrieval for Geospatial analysis.

🚀 **NEW**: This server now includes all [Jupyter MCP Server](https://github.com/datalayer/jupyter-mcp-server) tools through composition, providing a unified interface for both Earth data discovery and Jupyter notebook manipulation.

The following demo uses this MCP server to search for datasets and data granules on NASA Earthdata, the [jupyter-earth-mcp-server](https://github.com/datalayer/jupyter-earth-mcp-server) to download the data in Jupyter and the [jupyter-mcp-server](https://github.com/datalayer/jupyter-mcp-server) to run further analysis.

<div>
  <a href="https://www.loom.com/share/c2b5b05f548d4f1492d5c107f0c48dbc">
    <p>Analyzing Sea Level Rise with AI-Powered Geospatial Tools and Jupyter - Watch Video</p>
  </a>
  <a href="https://www.loom.com/share/c2b5b05f548d4f1492d5c107f0c48dbc">
    <img style="max-width:100%;" src="https://cdn.loom.com/sessions/thumbnails/c2b5b05f548d4f1492d5c107f0c48dbc-598a84f02de7e74e-full-play.gif">
  </a>
</div>

## Use with Claude Desktop

To use this with Claude Desktop, add the following to your `claude_desktop_config.json`.

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

If you are using Linux, start Claude with the following command.

```bash
make claude-linux
```

## Tools

The server offers **15 tools total**: 3 Earthdata-specific tools plus 12 Jupyter notebook manipulation tools (prefixed with `jupyter_`).

### Earthdata Tools

#### `search_earth_datasets`

- Search for datasets on NASA Earthdata.
- Input:
  - search_keywords (str): Keywords to search for in the dataset titles.
  - count (int): Number of datasets to return.
  - temporal (tuple): (Optional) Temporal range in the format (date_from, date_to).
  - bounding_box (tuple): (Optional) Bounding box in the format (lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat).
- Returns: List of dataset abstracts.

#### `search_earth_datagranules`

- Search for data granules on NASA Earthdata.
- Input:
  - short_name (str): Short name of the dataset.
  - count (int): Number of data granules to return.
  - temporal (tuple): (Optional) Temporal range in the format (date_from, date_to).
  - bounding_box (tuple): (Optional) Bounding box in the format (lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat).
- Returns: List of data granules.

#### `download_earth_data_granules` 🆕

- Download Earth data granules from NASA Earth Data and integrate with Jupyter notebooks.
- This tool combines earthdata search capabilities with jupyter notebook manipulation to create a seamless download workflow.
- Input:
  - folder_name (str): Local folder name to save the data.
  - short_name (str): Short name of the Earth dataset to download.
  - count (int): Number of data granules to download.
  - temporal (tuple): (Optional) Temporal range in the format (date_from, date_to).
  - bounding_box (tuple): (Optional) Bounding box in the format (lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat).
- Returns: Success message with download code preparation details.
- **Integration**: Uses composed jupyter tools to add download code to notebooks for interactive execution.

### Jupyter Tools (Composed)

The following Jupyter notebook manipulation tools are available with the `jupyter_` prefix:

- **`jupyter_append_markdown_cell`**: Add markdown cells to notebooks
- **`jupyter_insert_markdown_cell`**: Insert markdown cells at specific positions
- **`jupyter_overwrite_cell_source`**: Modify existing cell content
- **`jupyter_append_execute_code_cell`**: Add and execute code cells
- **`jupyter_insert_execute_code_cell`**: Insert and execute code cells at specific positions
- **`jupyter_execute_cell_with_progress`**: Execute cells with progress monitoring
- **`jupyter_execute_cell_simple_timeout`**: Execute cells with timeout
- **`jupyter_execute_cell_streaming`**: Execute cells with streaming output
- **`jupyter_read_all_cells`**: Read all notebook cells
- **`jupyter_read_cell`**: Read specific notebook cells
- **`jupyter_get_notebook_info`**: Get notebook metadata
- **`jupyter_delete_cell`**: Delete notebook cells

For detailed documentation of the Jupyter tools, see the [Jupyter MCP Server documentation](https://github.com/datalayer/jupyter-mcp-server).

## Architecture: Server Composition

This server uses a **composition pattern** to combine tools from multiple MCP servers into a single unified interface. The implementation:

1. **Imports the Jupyter MCP Server** at runtime
2. **Merges tool definitions** from the Jupyter server into the Earthdata server
3. **Prefixes Jupyter tools** with `jupyter_` to avoid naming conflicts
4. **Preserves all functionality** from both servers

This approach provides several benefits:
- ✅ **Unified Interface**: Single MCP server for both Earth data and Jupyter operations
- ✅ **No Duplication**: Reuses existing Jupyter MCP Server code without copying
- ✅ **Namespace Safety**: Prefixed tools prevent naming conflicts  
- ✅ **Graceful Degradation**: Falls back to Earthdata-only if Jupyter server unavailable
- ✅ **Maintainability**: Changes to Jupyter MCP Server are automatically included

### Implementation Details

The composition is implemented in the `_compose_jupyter_tools()` function, which:

```python
# Simplified version of the composition logic
def _compose_jupyter_tools():
    jupyter_mcp_module = importlib.import_module("jupyter_mcp_server.server")
    jupyter_mcp_instance = jupyter_mcp_module.mcp
    
    # Add jupyter tools with prefixed names
    for tool_name, tool in jupyter_mcp_instance._tool_manager._tools.items():
        prefixed_name = f"jupyter_{tool_name}"
        mcp._tool_manager._tools[prefixed_name] = tool
```

This pattern can be extended to compose additional MCP servers as needed.

## Prompts

1. `download_analyze_global_sea_level` 🆕
   - Generate a comprehensive workflow for downloading and analyzing Global Mean Sea Level Trend dataset.
   - Uses both earthdata download tools and jupyter analysis capabilities.
   - Returns: Detailed prompt for complete sea level analysis workflow.

2. `sealevel_rise_dataset`
   - Search for datasets related to sea level rise worldwide.
   - Input:
     - `start_year` (int): Start year to consider.
      - `end_year` (int): End year to consider.
   - Returns: Prompt correctly formatted.

3. `ask_datasets_format`
    - To ask about the format of the datasets.
    - Returns: Prompt correctly formatted.

## Building

```bash
# or run `docker build -t datalayer/earthdata-mcp-server .`
make build-docker
```

If you prefer, you can pull the prebuilt images.

```bash
make pull-docker
```
