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

🚀 **NEW**: This server now includes all [Jupyter MCP Server](https://github.com/datalayer/jupyter-mcp-server) tools through composition, providing a unified interface for both Earth data discovery and Jupyter notebook manipulation. All Jupyter MCP Server command-line options are also available for seamless integration.

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

## NASA Earthdata Authentication

To access NASA Earthdata resources, you need to authenticate with NASA's Earthdata Login system. The tools in this server handle authentication automatically, but you'll need to provide credentials when prompted.

### Getting a NASA Earthdata Account

1. **Create an Account**: Visit [https://urs.earthdata.nasa.gov/](https://urs.earthdata.nasa.gov/) and click "Register"
2. **Fill out the registration form** with your information
3. **Verify your email** address by clicking the link in the confirmation email
4. **Log in** to your account at [https://urs.earthdata.nasa.gov/](https://urs.earthdata.nasa.gov/)

### Authentication Methods

The earthaccess library (used by this server) supports several authentication methods:

#### 1. Interactive Login (Recommended for Development)
When using the server, the first time you access NASA data, you'll be prompted to log in:

```python
# This happens automatically when using download_earth_data_granules
# or when the earthaccess library is first used
auth = earthaccess.login()
```

The system will prompt you for:
- **Username**: Your NASA Earthdata username  
- **Password**: Your NASA Earthdata password

#### 2. Environment Variables (Recommended for Production)
Set these environment variables to avoid interactive prompts:

```bash
export EARTHDATA_USERNAME="your_username"
export EARTHDATA_PASSWORD="your_password"
```

#### 3. .netrc File (Alternative Method)
Create a `.netrc` file in your home directory:

```bash
# ~/.netrc
machine urs.earthdata.nasa.gov
login your_username
password your_password
```

**Important**: Make sure the `.netrc` file has proper permissions:
```bash
chmod 600 ~/.netrc
```

### Testing Your Authentication

You can test your authentication by running a simple earthaccess command:

```python
import earthaccess

# Test authentication
auth = earthaccess.login()
if auth:
    print("✅ Authentication successful!")
    
    # Test data access
    results = earthaccess.search_datasets(keyword="sea level", count=1)
    print(f"Found {len(results)} datasets")
else:
    print("❌ Authentication failed")
```

### Security Best Practices

- **Never commit credentials** to version control
- **Use environment variables** in production environments
- **Keep your .netrc file private** with proper file permissions
- **Regularly update your password** for security

### Troubleshooting Authentication

If you encounter authentication issues:

1. **Verify your credentials** at [https://urs.earthdata.nasa.gov/](https://urs.earthdata.nasa.gov/)
2. **Check for account suspension** - NASA may temporarily suspend accounts for security reasons
3. **Clear cached credentials** by deleting `~/.earthaccess_config` if it exists
4. **Try interactive login** even if using environment variables to debug the issue

For more details, see the [earthaccess authentication documentation](https://earthaccess.readthedocs.io/en/latest/quick-start/#authentication).

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
- **Authentication**: Requires NASA Earthdata Login credentials (see [Authentication section](#nasa-earthdata-authentication))
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

## Command-Line Interface

The Earthdata MCP Server includes all command-line options from the Jupyter MCP Server, enabling full configuration of Jupyter integration alongside Earthdata capabilities.

### Available Commands

#### `start` - Start the Server

Start the Earthdata-Jupyter Composed MCP server with full configuration options:

```bash
python -m earthdata_mcp_server.server start [OPTIONS]
```

**Key Options:**
- `--transport [stdio|streamable-http]`: Server transport method (default: stdio)
- `--provider [jupyter|datalayer]`: Jupyter provider type (default: jupyter)
- `--runtime-url TEXT`: Jupyter server URL (default: http://localhost:8888)
- `--runtime-token TEXT`: Authentication token for Jupyter server
- `--document-url TEXT`: Document server URL (default: http://localhost:8888)
- `--document-id TEXT`: Notebook path (default: notebook.ipynb)
- `--document-token TEXT`: Authentication token for document server
- `--port INTEGER`: Port for streamable-http transport (default: 4040)
- `--start-new-runtime BOOLEAN`: Start new kernel vs. use existing (default: True)
- `--runtime-id TEXT`: Specific kernel ID to use

**Examples:**

```bash
# Start with stdio transport (for MCP clients)
python -m earthdata_mcp_server.server start

# Start with HTTP transport for testing
python -m earthdata_mcp_server.server start --transport streamable-http --port 5050

# Connect to specific Jupyter server with authentication
python -m earthdata_mcp_server.server start \
  --runtime-url http://my-jupyter:8888 \
  --runtime-token my-token \
  --document-id "analysis/sea-level.ipynb"

# Use Datalayer provider
python -m earthdata_mcp_server.server start \
  --provider datalayer \
  --runtime-url http://datalayer-runtime:8000
```

#### `connect` - Connect to Jupyter

Connect to an existing Jupyter document and runtime:

```bash
python -m earthdata_mcp_server.server connect [OPTIONS]
```

**Options:** Same as `start` command, plus:
- `--earthdata-mcp-server-url TEXT`: URL of running Earthdata MCP Server (default: http://localhost:4040)

#### `stop` - Stop the Server

Stop a running Earthdata MCP Server:

```bash
python -m earthdata_mcp_server.server stop [OPTIONS]
```

### Environment Variables

All command-line options can be set via environment variables:

```bash
export PROVIDER="jupyter"
export RUNTIME_URL="http://localhost:8888"
export RUNTIME_TOKEN="my-jupyter-token"
export DOCUMENT_URL="http://localhost:8888"
export DOCUMENT_ID="notebook.ipynb"
export DOCUMENT_TOKEN="my-document-token"
export TRANSPORT="stdio"
export PORT="4040"

# Start with environment configuration
python -m earthdata_mcp_server.server start
```

### Integration Testing

Verify that the composition is working correctly:

```bash
# Run composition tests (tool integration and global variables)
python earthdata_mcp_server/tests/test_composition.py

# Run CLI options tests (command-line interface integration)
python earthdata_mcp_server/tests/test_cli_options.py

# Run all tests
python earthdata_mcp_server/tests/test_composition.py && python earthdata_mcp_server/tests/test_cli_options.py
```

**test_composition.py** verifies:
- ✅ All 15 tools are available (3 Earthdata + 12 Jupyter)
- ✅ All command-line options are functional
- ✅ Global variable synchronization works
- ✅ Tool composition is successful

**test_cli_options.py** verifies:
- ✅ All CLI options from jupyter-mcp-server are available
- ✅ All commands work correctly
- ✅ Environment variable support is functional

## Architecture: Server Composition

This server uses a **composition pattern** to combine tools from multiple MCP servers into a single unified interface. The implementation:

1. **Imports the Jupyter MCP Server** at runtime
2. **Merges tool definitions** from the Jupyter server into the Earthdata server
3. **Prefixes Jupyter tools** with `jupyter_` to avoid naming conflicts
4. **Preserves all functionality** from both servers
5. **Reuses command-line interface** with all Jupyter MCP Server options available
6. **Synchronizes global variables** between server instances for seamless operation

This approach provides several benefits:
- ✅ **Unified Interface**: Single MCP server for both Earth data and Jupyter operations
- ✅ **Complete CLI Integration**: All Jupyter server options available for configuration
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
    
    # Synchronize global variables for consistent configuration
    _sync_jupyter_globals()
    
    # Add jupyter tools with prefixed names
    for tool_name, tool in jupyter_mcp_instance._tool_manager._tools.items():
        prefixed_name = f"jupyter_{tool_name}"
        mcp._tool_manager._tools[prefixed_name] = tool

def _sync_jupyter_globals():
    """Bidirectional synchronization of global variables between servers"""
    # Synchronize configuration variables like:
    # RUNTIME_URL, DOCUMENT_URL, PROVIDER, TRANSPORT, etc.
```

**Global Variable Synchronization**: The servers share configuration through synchronized global variables, ensuring that:
- Jupyter tools use the same connection parameters as specified in Earthdata server commands
- Configuration changes in one server are reflected in the other
- Both servers maintain consistent state throughout operation

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
