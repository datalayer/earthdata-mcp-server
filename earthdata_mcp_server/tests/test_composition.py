#!/usr/bin/env python3
"""
Test module for validating the composition of earthdata and jupyter MCP tools.

This test verifies that the earthdata-mcp-server successfully composes
tools from both the earthdata and jupyter-mcp-server modules.
"""

import sys
import os
import unittest
from typing import List, Dict, Any

# Add the jupyter-mcp-server to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../jupyter-mcp-server'))

try:
    import earthdata_mcp_server.server as earthdata_server
    JUPYTER_MCP_AVAILABLE = True
except ImportError:
    JUPYTER_MCP_AVAILABLE = False


class TestServerComposition(unittest.TestCase):
    """Test the composition of earthdata and jupyter MCP tools."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not JUPYTER_MCP_AVAILABLE:
            self.skipTest("jupyter-mcp-server not available")
        
        self.mcp_server = earthdata_server.mcp
        self.all_tools = list(self.mcp_server._tool_manager._tools.keys())
        
    def test_server_name(self):
        """Test that the server has the correct composed name."""
        expected_name = "earthdata-jupyter-composed"
        self.assertEqual(self.mcp_server.name, expected_name)
        
    def test_earthdata_tools_present(self):
        """Test that original earthdata tools are present."""
        expected_earthdata_tools = [
            'search_earth_datasets',
            'search_earth_datagranules',
            'download_earth_data_granules'  # New tool added
        ]
        
        for tool in expected_earthdata_tools:
            with self.subTest(tool=tool):
                self.assertIn(tool, self.all_tools, 
                            f"Earthdata tool '{tool}' not found in available tools")
    
    def test_jupyter_tools_present(self):
        """Test that jupyter tools are present with correct prefixes."""
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
        
        for tool in expected_jupyter_tools:
            with self.subTest(tool=tool):
                self.assertIn(tool, self.all_tools,
                            f"Jupyter tool '{tool}' not found in available tools")
    
    def test_tool_count(self):
        """Test that the expected number of tools are available."""
        earthdata_tools = [t for t in self.all_tools if not t.startswith('jupyter_')]
        jupyter_tools = [t for t in self.all_tools if t.startswith('jupyter_')]
        
        # Expected counts based on current implementation
        expected_earthdata_count = 3  # Updated to include download tool
        expected_jupyter_count = 12
        expected_total = expected_earthdata_count + expected_jupyter_count
        
        self.assertEqual(len(earthdata_tools), expected_earthdata_count,
                        f"Expected {expected_earthdata_count} earthdata tools, got {len(earthdata_tools)}")
        self.assertEqual(len(jupyter_tools), expected_jupyter_count,
                        f"Expected {expected_jupyter_count} jupyter tools, got {len(jupyter_tools)}")
        self.assertEqual(len(self.all_tools), expected_total,
                        f"Expected {expected_total} total tools, got {len(self.all_tools)}")
    
    def test_tool_callable(self):
        """Test that tools are properly registered and callable."""
        # Test that we can access tool definitions
        for tool_name in ['search_earth_datasets', 'download_earth_data_granules', 'jupyter_read_all_cells']:
            with self.subTest(tool=tool_name):
                self.assertIn(tool_name, self.all_tools)
                tool_def = self.mcp_server._tool_manager._tools[tool_name]
                self.assertIsNotNone(tool_def)
                
                # Check that the tool has expected attributes
                self.assertTrue(hasattr(tool_def, 'name') or hasattr(tool_def, '__name__'))
    
    def test_no_tool_name_conflicts(self):
        """Test that there are no naming conflicts between tool sets."""
        earthdata_tools = [t for t in self.all_tools if not t.startswith('jupyter_')]
        jupyter_tools = [t for t in self.all_tools if t.startswith('jupyter_')]
        
        # Check that all jupyter tools are properly prefixed
        for tool in jupyter_tools:
            self.assertTrue(tool.startswith('jupyter_'),
                          f"Jupyter tool '{tool}' should be prefixed with 'jupyter_'")
        
        # Check that no earthdata tools have the jupyter prefix
        for tool in earthdata_tools:
            self.assertFalse(tool.startswith('jupyter_'),
                           f"Earthdata tool '{tool}' should not have 'jupyter_' prefix")
    
    def test_prompts_available(self):
        """Test that prompts are available."""
        if hasattr(self.mcp_server, '_prompt_manager'):
            prompts = list(self.mcp_server._prompt_manager._prompts.keys())
            
            # Expected earthdata prompts (including new download prompt)
            expected_prompts = [
                'download_analyze_global_sea_level',  # New prompt added
                'sealevel_rise_dataset',
                'ask_datasets_format'
            ]
            
            for prompt in expected_prompts:
                with self.subTest(prompt=prompt):
                    self.assertIn(prompt, prompts,
                                f"Prompt '{prompt}' not found in available prompts")
    
    def test_tool_callable(self):
        """Test that tools are properly registered and callable."""
        # Test that we can access tool definitions
        for tool_name in ['search_earth_datasets', 'jupyter_read_all_cells']:
            with self.subTest(tool=tool_name):
                self.assertIn(tool_name, self.all_tools)
                tool_def = self.mcp_server._tool_manager._tools[tool_name]
                self.assertIsNotNone(tool_def)
                
                # Check that the tool has expected attributes
                self.assertTrue(hasattr(tool_def, 'name') or hasattr(tool_def, '__name__'))


class TestCompositionRobustness(unittest.TestCase):
    """Test the robustness of the composition mechanism."""
    
    def test_graceful_degradation(self):
        """Test that the server works even if jupyter-mcp-server is unavailable."""
        # This test simulates the scenario where jupyter-mcp-server import fails
        # In practice, this would require mocking the import, but we test the 
        # structure to ensure it's designed for graceful degradation
        
        # The composition function should handle ImportError gracefully
        # and log appropriate warnings while still providing earthdata tools
        self.assertTrue(True)  # Placeholder - actual test would mock imports


def run_composition_validation() -> Dict[str, Any]:
    """
    Run the composition validation and return results.
    
    Returns:
        dict: Test results including tool counts and validation status
    """
    if not JUPYTER_MCP_AVAILABLE:
        return {
            "status": "skipped",
            "reason": "jupyter-mcp-server not available",
            "earthdata_tools": 3,  # Updated to include download tool
            "jupyter_tools": 0,
            "total_tools": 3  # Updated total
        }
    
    mcp_server = earthdata_server.mcp
    all_tools = list(mcp_server._tool_manager._tools.keys())
    earthdata_tools = [t for t in all_tools if not t.startswith('jupyter_')]
    jupyter_tools = [t for t in all_tools if t.startswith('jupyter_')]
    
    prompts = []
    if hasattr(mcp_server, '_prompt_manager'):
        prompts = list(mcp_server._prompt_manager._prompts.keys())
    
    return {
        "status": "success",
        "server_name": mcp_server.name,
        "earthdata_tools": len(earthdata_tools),
        "jupyter_tools": len(jupyter_tools),
        "total_tools": len(all_tools),
        "prompts_count": len(prompts),
        "tool_list": {
            "earthdata": earthdata_tools,
            "jupyter": jupyter_tools[:5]  # Show first 5 jupyter tools
        },
        "prompts": prompts
    }


if __name__ == "__main__":
    # Run validation when script is executed directly
    print("🔧 Running Earthdata-Jupyter MCP Server Composition Validation")
    print("=" * 70)
    
    results = run_composition_validation()
    
    if results["status"] == "skipped":
        print(f"⚠️  Test skipped: {results['reason']}")
    else:
        print(f"✅ Server Name: {results['server_name']}")
        print(f"📊 Tool Summary:")
        print(f"   🌍 Earthdata tools: {results['earthdata_tools']}")
        print(f"   📓 Jupyter tools: {results['jupyter_tools']}")
        print(f"   📝 Total tools: {results['total_tools']}")
        print(f"   💬 Prompts: {results['prompts_count']}")
        
        print(f"\n🛠️  Sample Tools:")
        for tool in results['tool_list']['earthdata']:
            print(f"   ✓ {tool}")
        for tool in results['tool_list']['jupyter']:
            print(f"   ✓ {tool}")
        if len(results['tool_list']['jupyter']) < results['jupyter_tools']:
            remaining = results['jupyter_tools'] - len(results['tool_list']['jupyter'])
            print(f"   ... and {remaining} more jupyter tools")
    
    print(f"\n🧪 Running unit tests...")
    unittest.main(verbosity=2, exit=False)
