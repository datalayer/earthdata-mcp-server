<!--
  ~ Copyright (c) 2023-2024 Datalayer, Inc.
  ~
  ~ BSD 3-Clause License
-->

[![Datalayer](https://assets.datalayer.tech/datalayer-25.svg)](https://datalayer.io)

[![Become a Sponsor](https://img.shields.io/static/v1?label=Become%20a%20Sponsor&message=%E2%9D%A4&logo=GitHub&style=flat&color=1ABC9C)](https://github.com/sponsors/datalayer)

# Earthdata MCP Server Examples

This directory contains examples demonstrating Earthdata-only capabilities.

## Example Files

### `workflow_example.py`

Demonstrates an Earth science workflow using Earthdata tools:

- **Dataset Discovery**: Search for NASA Earth science datasets using earthdata tools
- **Manifest-first downloads**: Inspect granules before retrieving files
- **Script generation**: Produce code for execution in an external composed runtime

#### Features Demonstrated

1. **Earthdata scope**: How discovery and granule retrieval work together
2. **Search Capabilities**: Finding datasets for sea level, temperature, and gravity studies
3. **Download Modes**: `manifest`, `download`, and `script`
4. **Composition Ready**: Script output can be run with `mcp-compose` and `jupyter-mcp-server`

#### Running the Example

```bash
# Run the integrated workflow example
python -m earthdata_mcp_server.examples.workflow_example
```

#### Expected Output

The example demonstrates:
- 🌍 Earthdata dataset search with various keywords
- 📋 Manifest previews before download
- 🧩 Script output that can be executed in a composed notebook stack
- 📊 Analysis-ready retrieval workflows

#### MCP Client Usage

In practice, these workflows would be executed by MCP clients like:
- Claude Desktop
- VS Code with MCP extensions
- Custom MCP client applications

The example shows the tool calls that would be made through the MCP protocol.
