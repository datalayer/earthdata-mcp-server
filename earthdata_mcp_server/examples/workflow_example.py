#!/usr/bin/env python3
"""
Example demonstrating the integrated use of Earthdata and Jupyter MCP tools.

This example shows how the composed earthdata-mcp-server can be used to:
1. Search for Earth science datasets using earthdata tools
2. Create and manipulate Jupyter notebooks using jupyter tools
3. Execute analysis workflows combining both capabilities

Note: This is a conceptual example showing the tool integration.
In practice, you would use an MCP client (like Claude Desktop, Cline, etc.)
to call these tools through the MCP protocol.
"""

import sys
import os
import json
import asyncio
from typing import List, Dict, Any

# Add the jupyter-mcp-server to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../jupyter-mcp-server'))

try:
    import earthdata_mcp_server.server as earthdata_server
    COMPOSITION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Composition not available: {e}")
    COMPOSITION_AVAILABLE = False


class EarthdataJupyterWorkflow:
    """
    Example workflow class demonstrating integrated Earth science analysis.
    
    This class shows how Earthdata search capabilities can be combined
    with Jupyter notebook manipulation for complete analysis workflows.
    """
    
    def __init__(self):
        """Initialize the workflow with access to the composed MCP server."""
        if not COMPOSITION_AVAILABLE:
            raise RuntimeError("Earthdata-Jupyter composition not available")
        
        self.mcp_server = earthdata_server.mcp
        self.available_tools = list(self.mcp_server._tool_manager._tools.keys())
    
    def get_tool_summary(self) -> Dict[str, Any]:
        """Get a summary of available tools."""
        earthdata_tools = [t for t in self.available_tools if not t.startswith('jupyter_')]
        jupyter_tools = [t for t in self.available_tools if t.startswith('jupyter_')]
        
        return {
            "total_tools": len(self.available_tools),
            "earthdata_tools": {
                "count": len(earthdata_tools),
                "tools": earthdata_tools
            },
            "jupyter_tools": {
                "count": len(jupyter_tools),
                "tools": jupyter_tools
            }
        }
    
    def simulate_earthdata_search(self, keywords: str, count: int = 3) -> List[Dict[str, str]]:
        """
        Simulate searching for Earth science datasets.
        
        In a real MCP client, this would be:
        await client.call_tool("search_earth_datasets", {
            "search_keywords": keywords,
            "count": count,
            "temporal": None,
            "bounding_box": None
        })
        """
        # Simulated results for demonstration
        simulated_datasets = [
            {
                "Title": "MODIS Aqua Sea Surface Temperature",
                "ShortName": "MODIS_A_SST",
                "Abstract": "Daily sea surface temperature from MODIS Aqua satellite...",
                "DataType": "Science",
                "DOI": "10.5067/MODIS-AQUA-SST"
            },
            {
                "Title": "TOPEX/Poseidon Altimeter Sea Level",
                "ShortName": "TOPEX_L2_OST",
                "Abstract": "Precise altimeter measurements of sea surface height...",
                "DataType": "Science", 
                "DOI": "10.5067/TOPEX-L2-OST"
            },
            {
                "Title": "GRACE Gravity Field Solutions",
                "ShortName": "GRACE_L2_GRAV",
                "Abstract": "Monthly gravity field solutions from GRACE mission...",
                "DataType": "Science",
                "DOI": "10.5067/GRACE-L2-GRAV"
            }
        ]
        
        # Filter and limit results based on keywords
        filtered = [d for d in simulated_datasets if keywords.lower() in d["Title"].lower()]
        return filtered[:count]
    
    def generate_analysis_notebook(self, datasets: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Generate notebook cells for analyzing the discovered datasets.
        
        In a real MCP client, each cell would be created using:
        await client.call_tool("jupyter_append_markdown_cell", {"cell_source": content})
        await client.call_tool("jupyter_append_execute_code_cell", {"cell_source": code})
        """
        notebook_cells = []
        
        # Title cell
        title_content = f"# Earth Science Data Analysis\n\nAnalyzing {len(datasets)} datasets from NASA Earthdata"
        notebook_cells.append({
            "type": "markdown",
            "tool": "jupyter_append_markdown_cell",
            "content": title_content
        })
        
        # Dataset overview cell
        overview_content = "## Dataset Overview\n\n"
        for i, dataset in enumerate(datasets, 1):
            overview_content += f"{i}. **{dataset['Title']}** ({dataset['ShortName']})\n"
            overview_content += f"   - {dataset['Abstract'][:100]}...\n\n"
        
        notebook_cells.append({
            "type": "markdown", 
            "tool": "jupyter_append_markdown_cell",
            "content": overview_content
        })
        
        # Import libraries cell
        imports_code = """
# Import required libraries for Earth science analysis
import earthaccess
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

# Configure matplotlib for inline plotting
%matplotlib inline
plt.style.use('seaborn-v0_8')

print("✅ Libraries imported successfully")
"""
        notebook_cells.append({
            "type": "code",
            "tool": "jupyter_append_execute_code_cell", 
            "content": imports_code
        })
        
        # Authentication cell
        auth_code = """
# Authenticate with NASA Earthdata
auth = earthaccess.login()
if auth:
    print("🔐 Successfully authenticated with NASA Earthdata")
else:
    print("❌ Authentication failed - check credentials")
"""
        notebook_cells.append({
            "type": "code",
            "tool": "jupyter_append_execute_code_cell",
            "content": auth_code
        })
        
        # Dataset-specific analysis for each dataset
        for dataset in datasets:
            analysis_code = f"""
# Analysis for {dataset['Title']}
print("📊 Analyzing: {dataset['Title']}")

# Search for recent data granules
granules = earthaccess.search_data(
    short_name="{dataset['ShortName']}",
    count=10,
    temporal=("2023-01-01", "2023-12-31")
)

print(f"Found {{len(granules)}} data granules")
if granules:
    print(f"Latest granule: {{granules[0].get('title', 'Unknown')}}")
    
    # Download and analyze (simulated)
    # files = earthaccess.download(granules[:1], local_path="./data")
    print("📥 Data download simulation complete")
"""
            notebook_cells.append({
                "type": "code",
                "tool": "jupyter_append_execute_code_cell",
                "content": analysis_code
            })
        
        # Visualization cell
        viz_code = """
# Create summary visualization
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle('Earth Science Data Analysis Summary', fontsize=16)

# Placeholder plots (would use real data in practice)
x = np.linspace(0, 365, 100)

# Sea surface temperature trend
axes[0,0].plot(x, 20 + 5*np.sin(2*np.pi*x/365) + np.random.normal(0, 0.5, 100))
axes[0,0].set_title('Sea Surface Temperature')
axes[0,0].set_ylabel('Temperature (°C)')

# Sea level variations  
axes[0,1].plot(x, np.cumsum(np.random.normal(0, 0.1, 100)))
axes[0,1].set_title('Sea Level Anomaly')
axes[0,1].set_ylabel('Height (cm)')

# Gravity field changes
axes[1,0].plot(x, np.sin(4*np.pi*x/365) + np.random.normal(0, 0.1, 100))
axes[1,0].set_title('Gravity Field Variation')
axes[1,0].set_ylabel('Anomaly (mGal)')

# Data availability
datasets_names = [d['ShortName'] for d in datasets][:4]  # Limit to 4 for display
data_counts = np.random.randint(50, 200, len(datasets_names))
axes[1,1].bar(range(len(datasets_names)), data_counts)
axes[1,1].set_title('Data Granule Availability')
axes[1,1].set_ylabel('Count')
axes[1,1].set_xticks(range(len(datasets_names)))
axes[1,1].set_xticklabels(datasets_names, rotation=45)

plt.tight_layout()
plt.show()

print("📈 Analysis visualization complete")
"""
        notebook_cells.append({
            "type": "code", 
            "tool": "jupyter_append_execute_code_cell",
            "content": viz_code
        })
        
        return notebook_cells
    
    async def run_example_workflow(self, search_keywords: str = "sea level"):
        """
        Run a complete example workflow combining Earthdata search and Jupyter analysis.
        
        Args:
            search_keywords: Keywords to search for in dataset titles
        """
        print("🌍 Starting Integrated Earthdata-Jupyter Workflow")
        print("=" * 60)
        
        # Step 1: Search for datasets
        print(f"\n1️⃣ Searching for datasets with keywords: '{search_keywords}'")
        datasets = self.simulate_earthdata_search(search_keywords, count=3)
        
        print(f"   📊 Found {len(datasets)} relevant datasets:")
        for i, dataset in enumerate(datasets, 1):
            print(f"      {i}. {dataset['Title']}")
        
        # Step 2: Generate notebook structure
        print(f"\n2️⃣ Generating analysis notebook...")
        notebook_cells = self.generate_analysis_notebook(datasets)
        
        print(f"   📝 Created {len(notebook_cells)} notebook cells:")
        for i, cell in enumerate(notebook_cells, 1):
            cell_type = cell['type']
            char_count = len(cell['content'])
            print(f"      Cell {i}: {cell_type} ({char_count} chars) - {cell['tool']}")
        
        # Step 3: Simulate execution
        print(f"\n3️⃣ Simulating notebook execution...")
        code_cells = [cell for cell in notebook_cells if cell['type'] == 'code']
        
        for i, cell in enumerate(code_cells, 1):
            # In practice, this would be:
            # result = await client.call_tool("jupyter_execute_cell_with_progress", {
            #     "cell_index": cell_index,
            #     "timeout_seconds": 120
            # })
            print(f"   ⚡ Executing code cell {i}/{len(code_cells)}...")
            await asyncio.sleep(0.1)  # Simulate execution time
        
        print(f"   ✅ All {len(code_cells)} code cells executed successfully")
        
        # Step 4: Summary
        print(f"\n4️⃣ Workflow Summary:")
        print(f"   🔍 Datasets analyzed: {len(datasets)}")
        print(f"   📄 Notebook cells created: {len(notebook_cells)}")
        print(f"   🧮 Code cells executed: {len(code_cells)}")
        print(f"   🚀 Integration successful!")
        
        return {
            "datasets": datasets,
            "notebook_cells": notebook_cells,
            "execution_summary": {
                "total_cells": len(notebook_cells),
                "code_cells": len(code_cells),
                "markdown_cells": len(notebook_cells) - len(code_cells)
            }
        }


def demonstrate_tool_capabilities():
    """Demonstrate the capabilities of the composed server."""
    if not COMPOSITION_AVAILABLE:
        print("❌ Cannot demonstrate - composition not available")
        return
    
    workflow = EarthdataJupyterWorkflow()
    tool_summary = workflow.get_tool_summary()
    
    print("🔧 Earthdata-Jupyter MCP Server Capabilities")
    print("=" * 50)
    print(f"📊 Total Tools Available: {tool_summary['total_tools']}")
    
    print(f"\n🌍 Earthdata Tools ({tool_summary['earthdata_tools']['count']}):")
    for tool in tool_summary['earthdata_tools']['tools']:
        print(f"   ✓ {tool}")
    
    print(f"\n📓 Jupyter Tools ({tool_summary['jupyter_tools']['count']}):")
    # Show first few jupyter tools
    jupyter_tools = tool_summary['jupyter_tools']['tools']
    for tool in jupyter_tools[:6]:
        print(f"   ✓ {tool}")
    if len(jupyter_tools) > 6:
        print(f"   ... and {len(jupyter_tools) - 6} more jupyter tools")


async def main():
    """Main function to run the example."""
    demonstrate_tool_capabilities()
    
    if COMPOSITION_AVAILABLE:
        print("\n" + "="*60)
        workflow = EarthdataJupyterWorkflow()
        
        # Demonstrate the new download tool
        print("\n🆕 NEW FEATURE DEMONSTRATION")
        print("="*60)
        
        # Simulate using the download_earth_data_granules tool
        print("📥 Demonstrating download_earth_data_granules tool:")
        print("   This tool combines earthdata search with jupyter notebook integration")
        print("   It creates download code and uses jupyter tools for execution")   
        # Example download tool usage
        download_example = {
            "tool": "download_earth_data_granules",
            "params": {
                "folder_name": "global_sea_level_data",
                "short_name": "TOPEX_L2_OST_GDR_C", 
                "count": 15,
                "temporal": ("2020-01-01", "2020-12-31"),
                "bounding_box": None
            },
            "expected_result": "Download code added to notebook + execution"
        }
        
        print(f"   📊 Example call: {download_example['tool']}")
        for key, value in download_example['params'].items():
            print(f"      {key}: {value}")
        print(f"   ✅ Result: {download_example['expected_result']}")
        
        print(f"\n🔗 Integration with jupyter tools:")
        print(f"   1. download_earth_data_granules → Prepares download code")
        print(f"   2. jupyter_append_execute_code_cell → Adds code to notebook")  
        print(f"   3. jupyter_execute_cell_with_progress → Runs download")
        print(f"   4. jupyter_read_cell → Checks results")
        
        # Run example workflows with different search terms
        search_terms = ["sea level", "temperature"]
        
        for term in search_terms:
            print(f"\n{'='*60}")
            result = await workflow.run_example_workflow(term)
            print(f"🎯 Workflow for '{term}' completed successfully!")
            
            if term != search_terms[-1]:  # Add separator except for last
                await asyncio.sleep(1)  # Brief pause between workflows


if __name__ == "__main__":
    print("🚀 Earthdata-Jupyter MCP Server Integration Example")
    print("This example demonstrates the composed server capabilities.\n")
    
    asyncio.run(main())
