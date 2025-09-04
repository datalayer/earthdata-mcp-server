<!--
  ~ Copyright (c) 2023-2024 Datalayer, Inc.
  ~
  ~ BSD 3-Clause License
-->

[![Datalayer](https://assets.datalayer.tech/datalayer-25.svg)](https://datalayer.io)

[![Become a Sponsor](https://img.shields.io/static/v1?label=Become%20a%20Sponsor&message=%E2%9D%A4&logo=GitHub&style=flat&color=1ABC9C)](https://github.com/sponsors/datalayer)

# Earthdata MCP Server Tests

This directory contains tests for the earthdata-mcp-server composition functionality.

## Test Files

### `test_composition.py`

Validates the integration of earthdata and jupyter MCP server tools through composition:

- **Server Composition**: Tests that the server correctly combines tools from both earthdata and jupyter-mcp-server
- **Tool Validation**: Verifies all expected tools are present with correct naming conventions  
- **CLI Integration**: Tests that all click commands and options from jupyter-mcp-server are available
- **Global Variable Sync**: Validates that configuration variables are properly synchronized between servers
- **Namespace Safety**: Ensures no naming conflicts between tool sets
- **Graceful Degradation**: Tests that the server works even if jupyter-mcp-server is unavailable

### `test_cli_options.py`

Validates the command-line interface integration from jupyter-mcp-server:

- **CLI Option Completeness**: Verifies all 10 jupyter CLI options are available in earthdata server
- **Command Availability**: Tests that all commands (`start`, `connect`, `stop`) are functional
- **Connect Command Options**: Validates specific options for the connect command
- **Environment Variable Support**: Confirms that global variables support environment-based configuration

#### Running the Tests

```bash
# Run the composition validation
python earthdata_mcp_server/tests/test_composition.py

# Run the CLI options validation  
python earthdata_mcp_server/tests/test_cli_options.py

# Run all tests
python earthdata_mcp_server/tests/test_composition.py && python earthdata_mcp_server/tests/test_cli_options.py

# Run with unittest (if converted to unittest format)
python -m unittest earthdata_mcp_server.tests.test_composition
```

#### Expected Results

**test_composition.py** should validate:
- ✅ 3 Earthdata tools: `search_earth_datasets`, `search_earth_datagranules`, `download_earth_data_granules`
- ✅ 12 Jupyter tools: All prefixed with `jupyter_`
- ✅ 3 Click commands: `start`, `connect`, `stop`
- ✅ 9 Global variables: All jupyter configuration options synchronized
- ✅ Total of 15 tools available in the composed server

**test_cli_options.py** should validate:
- ✅ 10 CLI options available in `start` command
- ✅ 3 commands available: `start`, `connect`, `stop`
- ✅ 8 CLI options available in `connect` command  
- ✅ Environment variable support through global variables

# 🪐 ✨ Earthdata MCP Server
