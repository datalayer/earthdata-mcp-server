[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/datalayer-earthdata-mcp-server-badge.png)](https://mseep.ai/app/datalayer-earthdata-mcp-server)

<!--
  ~ Copyright (c) 2023-2024 Datalayer, Inc.
  ~
  ~ BSD 3-Clause License
-->

[![Datalayer](https://assets.datalayer.tech/datalayer-25.svg)](https://datalayer.io)

[![Become a Sponsor](https://img.shields.io/static/v1?label=Become%20a%20Sponsor&message=%E2%9D%A4&logo=GitHub&style=flat&color=1ABC9C)](https://github.com/sponsors/datalayer)

# 🪐 ✨ Earthdata MCP Server

[![PyPI - Version](https://img.shields.io/pypi/v/earthdata-mcp-server)](https://pypi.org/project/earthdata-mcp-server)
[![smithery badge](https://smithery.ai/badge/@datalayer/earthdata-mcp-server)](https://smithery.ai/server/@datalayer/earthdata-mcp-server)

Earthdata MCP Server is a [Model Context Protocol](https://modelcontextprotocol.io/introduction) (MCP) server implementation that provides tools to interact with [NASA Earth Data](https://www.earthdata.nasa.gov/). It enables efficient dataset discovery, retrieval and analysis for Geospatial analysis.

🚀 **NEW**: This server now includes all [Jupyter MCP Server](https://github.com/datalayer/jupyter-mcp-server) tools through composition, providing a unified interface for both Earth data discovery and analysis in Jupyter Notebooks.

## 🚀 Key Features

- **Efficient Data Retrieval**: Search and download Earthdata datasets
- **Unified Interface**: Combines Earthdata research and Jupyter notebook manipulation tools for analysis

The following demo uses this MCP server to search for datasets and data granules on NASA Earthdata, download the data in Jupyter and run further analysis.

<div>
  <a href="https://www.loom.com/share/c2b5b05f548d4f1492d5c107f0c48dbc">
    <p>Analyzing Sea Level Rise with AI-Powered Geospatial Tools and Jupyter - Watch Video</p>
  </a>
  <a href="https://www.loom.com/share/c2b5b05f548d4f1492d5c107f0c48dbc">
    <img style="max-width:100%;" src="https://cdn.loom.com/sessions/thumbnails/c2b5b05f548d4f1492d5c107f0c48dbc-598a84f02de7e74e-full-play.gif">
  </a>
</div>

## 🏁 Getting Started

For comprehensive setup instructions—including `Streamable HTTP` transport and advanced configuration—check out [the Jupyter MCP Server documentation](https://jupyter-mcp-server.datalayer.tech/). Or, get started quickly with `JupyterLab` and `stdio` transport here below.

### 1. Set Up Your Environment

```bash
pip install jupyterlab==4.4.1 jupyter-collaboration==4.0.2 ipykernel
pip uninstall -y pycrdt datalayer_pycrdt
pip install datalayer_pycrdt==0.12.17
```

### 2. Start JupyterLab

```bash
# make jupyterlab
jupyter lab --port 8888 --IdentityProvider.token MY_TOKEN --ip 0.0.0.0
```

### 3. Configure Your Preferred MCP Client

> [!NOTE]
>
> Ensure the `port` of the `DOCUMENT_URL` and `RUNTIME_URL` match those used in the `jupyter lab` command.
>
> The `DOCUMENT_ID` which is the path to the notebook you want to connect to, should be relative to the directory where JupyterLab was started.
>
> In a basic setup, `DOCUMENT_URL` and `RUNTIME_URL` are the same. `DOCUMENT_TOKEN`, and `RUNTIME_TOKEN` are also the same and is actually the Jupyter Token.

> [!NOTE]
> 
> The `EARTHDATA_USERNAME` and `EARTHDATA_PASSWORD` environment variables are used for NASA Earthdata authentication to download datasets via the `earthaccess` library. See [NASA Earthdata Authentication](./docs/authentication.md) for more details.

#### MacOS and Windows

```json
{
  "mcpServers": {
    "earthdata": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "DOCUMENT_URL",
        "-e",
        "DOCUMENT_TOKEN",
        "-e",
        "DOCUMENT_ID",
        "-e",
        "RUNTIME_URL",
        "-e",
        "RUNTIME_TOKEN",
        "datalayer/earthdata-mcp-server:latest"
      ],
      "env": {
        "DOCUMENT_URL": "http://host.docker.internal:8888",
        "DOCUMENT_TOKEN": "MY_TOKEN",
        "DOCUMENT_ID": "notebook.ipynb",
        "RUNTIME_URL": "http://host.docker.internal:8888",
        "RUNTIME_TOKEN": "MY_TOKEN",
        "EARTHDATA_USERNAME": "your_username",
        "EARTHDATA_PASSWORD": "your_password"
      }
    }
  }
}
```

#### Linux

```json
{
  "mcpServers": {
    "earthdata": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "DOCUMENT_URL",
        "-e",
        "DOCUMENT_TOKEN",
        "-e",
        "DOCUMENT_ID",
        "-e",
        "RUNTIME_URL",
        "-e",
        "RUNTIME_TOKEN",
        "--network=host",
        "datalayer/earthdata-mcp-server:latest"
      ],
      "env": {
        "DOCUMENT_URL": "http://localhost:8888",
        "DOCUMENT_TOKEN": "MY_TOKEN",
        "DOCUMENT_ID": "notebook.ipynb",
        "RUNTIME_URL": "http://localhost:8888",
        "RUNTIME_TOKEN": "MY_TOKEN",
        "EARTHDATA_USERNAME": "your_username",
        "EARTHDATA_PASSWORD": "your_password"
      }
    }
  }
}
```

## Tools

The server offers **15 tools total**: 3 Earthdata-specific tools plus 12 Jupyter notebook manipulation tools.

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

#### `download_earth_data_granules`

- Download Earth data granules from NASA Earth Data and integrate with Jupyter notebooks.
- This tool combines earthdata search capabilities with jupyter notebook manipulation to create a seamless download workflow.
- **Authentication**: Requires NASA Earthdata Login credentials (see [Authentication section](#nasa-earthdata-authentication))
- Input:
  - folder_name (str): Local folder name to save the data.
  - short_name (str): Short name of the Earth dataset to download.
  - count (int): Number of data granules to download.
  - temporal (tuple): (Optional) Temporal range in the format (date_from, date_to).
  - bounding_box (tuple): (Optional) Bounding box in the format (lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat).
- Returns: Success message with download code preparation details.

### Jupyter Tools (Composed)

The following Jupyter notebook manipulation tools are available:

- **`append_markdown_cell`**: Add markdown cells to notebooks
- **`insert_markdown_cell`**: Insert markdown cells at specific positions
- **`overwrite_cell_source`**: Modify existing cell content
- **`append_execute_code_cell`**: Add and execute code cells
- **`insert_execute_code_cell`**: Insert and execute code cells at specific positions
- **`execute_cell_with_progress`**: Execute cells with progress monitoring
- **`execute_cell_simple_timeout`**: Execute cells with timeout
- **`execute_cell_streaming`**: Execute cells with streaming output
- **`read_all_cells`**: Read all notebook cells
- **`read_cell`**: Read specific notebook cells
- **`get_notebook_info`**: Get notebook metadata
- **`delete_cell`**: Delete notebook cells

For detailed documentation of the Jupyter tools, see the [Jupyter MCP Server documentation](https://github.com/datalayer/jupyter-mcp-server).

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
