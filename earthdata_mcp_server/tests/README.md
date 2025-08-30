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
- **Namespace Safety**: Ensures no naming conflicts between tool sets
- **Graceful Degradation**: Tests that the server works even if jupyter-mcp-server is unavailable

#### Running the Tests

```bash
# Run the composition validation
python -m earthdata_mcp_server.tests.test_composition

# Run with unittest
python -m unittest earthdata_mcp_server.tests.test_composition
```

#### Expected Results

The test should validate:
- ✅ 2 Earthdata tools: `search_earth_datasets`, `search_earth_datagranules`
- ✅ 12 Jupyter tools: All prefixed with `jupyter_`
- ✅ 2 Prompts: `sealevel_rise_dataset`, `ask_datasets_format`  
- ✅ Total of 14 tools available in the composed server

# 🪐 ✨ Earthdata MCP Server
