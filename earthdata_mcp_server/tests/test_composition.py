#!/usr/bin/env python3
"""
Test script to verify that earthdata-mcp-server correctly composes 
jupyter-mcp-server tools and click options.
"""

import logging
import sys

# Set up basic logging
logging.basicConfig(level=logging.INFO)

def test_tool_composition():
    """Test that jupyter tools are correctly composed."""
    print("Testing tool composition...")
    
    try:
        from earthdata_mcp_server.server import mcp
        
        # Get all available tools
        tools = list(mcp._tool_manager._tools.keys())
        print(f"Available tools ({len(tools)}):")
        
        # Separate earthdata and jupyter tools
        earthdata_tools = [t for t in tools if not t.startswith('jupyter_')]
        jupyter_tools = [t for t in tools if t.startswith('jupyter_')]
        
        print("\nEarthdata tools:")
        for tool in earthdata_tools:
            print(f"  - {tool}")
        
        print(f"\nJupyter tools ({len(jupyter_tools)}):")
        for tool in jupyter_tools:
            print(f"  - {tool}")
        
        # Test that we have the expected tools
        expected_jupyter_tools = [
            'jupyter_append_markdown_cell',
            'jupyter_insert_markdown_cell', 
            'jupyter_overwrite_cell_source',
            'jupyter_append_execute_code_cell',
            'jupyter_insert_execute_code_cell',
            'jupyter_execute_cell_with_progress',
            'jupyter_execute_cell_simple_timeout',
            'jupyter_execute_cell_streaming',
            'jupyter_read_all_cells',
            'jupyter_read_cell',
            'jupyter_get_notebook_info',
            'jupyter_delete_cell'
        ]
        
        missing_tools = [tool for tool in expected_jupyter_tools if tool not in jupyter_tools]
        if missing_tools:
            print(f"\n❌ Missing expected jupyter tools: {missing_tools}")
            return False
        else:
            print(f"\n✅ All expected jupyter tools are available!")
        
        expected_earthdata_tools = [
            'search_earth_datasets',
            'search_earth_datagranules', 
            'download_earth_data_granules'
        ]
        
        missing_earthdata_tools = [tool for tool in expected_earthdata_tools if tool not in earthdata_tools]
        if missing_earthdata_tools:
            print(f"\n❌ Missing expected earthdata tools: {missing_earthdata_tools}")
            return False
        else:
            print(f"\n✅ All expected earthdata tools are available!")
            
        return True
        
    except Exception as e:
        print(f"❌ Error during tool composition test: {e}")
        return False


def test_click_commands():
    """Test that click commands are available."""
    print("\nTesting click commands...")
    
    try:
        from earthdata_mcp_server.server import server
        
        # Check that the command group is available
        commands = list(server.commands.keys())
        print(f"Available commands: {commands}")
        
        expected_commands = ['connect', 'start', 'stop']
        missing_commands = [cmd for cmd in expected_commands if cmd not in commands]
        
        if missing_commands:
            print(f"❌ Missing expected commands: {missing_commands}")
            return False
        else:
            print("✅ All expected commands are available!")
            
        return True
        
    except Exception as e:
        print(f"❌ Error during click commands test: {e}")
        return False


def test_global_variables():
    """Test that global variables are properly synchronized."""
    print("\nTesting global variables...")
    
    try:
        from earthdata_mcp_server import server as earthdata_server
        
        # Check that the global variables exist
        required_globals = [
            'TRANSPORT', 'PROVIDER', 'RUNTIME_URL', 'START_NEW_RUNTIME',
            'RUNTIME_ID', 'RUNTIME_TOKEN', 'DOCUMENT_URL', 'DOCUMENT_ID', 'DOCUMENT_TOKEN'
        ]
        
        missing_globals = []
        for var_name in required_globals:
            if not hasattr(earthdata_server, var_name):
                missing_globals.append(var_name)
        
        if missing_globals:
            print(f"❌ Missing global variables: {missing_globals}")
            return False
        else:
            print("✅ All global variables are available!")
            
        # Print current values
        print("\nCurrent global variable values:")
        for var_name in required_globals:
            value = getattr(earthdata_server, var_name)
            print(f"  {var_name}: {value}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error during global variables test: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("EARTHDATA-MCP-SERVER COMPOSITION TEST")
    print("="*60)
    
    tests = [
        test_tool_composition,
        test_click_commands,  
        test_global_variables
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    if all(results):
        print("🎉 All tests passed! Earthdata-MCP-Server composition is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
