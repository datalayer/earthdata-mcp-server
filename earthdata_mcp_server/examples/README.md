<!--
  ~ Copyright (c) 2023-2024 Datalayer, Inc.
  ~
  ~ BSD 3-Clause License
-->

[![Datalayer](https://assets.datalayer.tech/datalayer-25.svg)](https://datalayer.io)

[![Become a Sponsor](https://img.shields.io/static/v1?label=Become%20a%20Sponsor&message=%E2%9D%A4&logo=GitHub&style=flat&color=1ABC9C)](https://github.com/sponsors/datalayer)

# Earthdata MCP Server Examples

This directory contains examples demonstrating the integrated capabilities of the earthdata-mcp-server composition.

## Example Files

### `workflow_example.py`

Demonstrates a complete Earth science analysis workflow using both Earthdata and Jupyter tools:

- **Dataset Discovery**: Search for NASA Earth science datasets using earthdata tools
- **Notebook Generation**: Create analysis notebooks using jupyter tools  
- **Integrated Workflow**: Show how both tool sets work together for complete analysis pipelines

#### Features Demonstrated

1. **Tool Composition**: How 14 total tools (2 Earthdata + 12 Jupyter) work together
2. **Search Capabilities**: Finding datasets for sea level, temperature, and gravity studies
3. **Notebook Creation**: Generating markdown and code cells programmatically
4. **Analysis Workflows**: Complete pipelines from data discovery to visualization

#### Running the Example

```bash
# Run the integrated workflow example
python -m earthdata_mcp_server.examples.workflow_example
```

#### Expected Output

The example demonstrates:
- 🌍 Earthdata dataset search with various keywords
- 📓 Jupyter notebook cell generation and execution simulation  
- 🔄 Integration workflows showing the power of composition
- 📊 Analysis pipelines for different Earth science domains

#### MCP Client Usage

In practice, these workflows would be executed by MCP clients like:
- Claude Desktop
- VS Code with MCP extensions
- Custom MCP client applications

The example shows the tool calls that would be made through the MCP protocol.
