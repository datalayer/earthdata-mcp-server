# Architecture: Server Composition

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
