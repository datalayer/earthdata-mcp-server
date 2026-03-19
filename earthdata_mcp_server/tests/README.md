<!--
  ~ Copyright (c) 2023-2024 Datalayer, Inc.
  ~
  ~ BSD 3-Clause License
-->

[![Datalayer](https://assets.datalayer.tech/datalayer-25.svg)](https://datalayer.io)

[![Become a Sponsor](https://img.shields.io/static/v1?label=Become%20a%20Sponsor&message=%E2%9D%A4&logo=GitHub&style=flat&color=1ABC9C)](https://github.com/sponsors/datalayer)

# Earthdata MCP Server Tests

This directory contains smoke tests for Earthdata MCP Server.

## Test Files

### `test_composition.py`

Validates Earthdata server tool registration and download mode validation:

- **Tool Validation**: Verifies expected Earthdata tools are registered.
- **Input Validation**: Verifies invalid download modes are rejected.

### `test_cli_options.py`

Validates Earthdata command-line interface:

- **Command Availability**: Verifies `start` command is available.
- **Option Availability**: Verifies `--transport` and `--port` on `start`.

#### Running the Tests

```bash
# Run tool and mode validation
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
- ✅ Invalid download mode raises an error

**test_cli_options.py** should validate:
- ✅ `start` command is present
- ✅ `--transport` and `--port` are present in `start --help`

# 🪐 ✨ Earthdata MCP Server
