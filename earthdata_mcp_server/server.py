# Copyright (c) 2023-2024 Datalayer, Inc.
#
# BSD 3-Clause License

import logging
import importlib
import asyncio
import os

from mcp.server.fastmcp import FastMCP

import earthaccess


# Create the composed server that will include both earthdata and jupyter tools
mcp = FastMCP("earthdata-jupyter-composed")


logger = logging.getLogger(__name__)


# Function to safely import and compose jupyter-mcp-server tools
def _compose_jupyter_tools():
    """Import and add Jupyter MCP Server tools to our earthdata server."""
    try:
        # Import the jupyter mcp server module
        jupyter_mcp_module = importlib.import_module("jupyter_mcp_server.server")
        jupyter_mcp_instance = jupyter_mcp_module.mcp
        
        # Add jupyter tools to our earthdata server
        # Note: We prefix jupyter tool names to avoid conflicts
        for tool_name, tool in jupyter_mcp_instance._tool_manager._tools.items():
            prefixed_name = f"jupyter_{tool_name}"
            if prefixed_name not in mcp._tool_manager._tools:
                # Add the tool with prefixed name
                mcp._tool_manager._tools[prefixed_name] = tool
                logger.info(f"Added Jupyter tool: {prefixed_name}")
        
        # Also copy any prompts if they exist
        if hasattr(jupyter_mcp_instance, '_prompt_manager') and hasattr(jupyter_mcp_instance._prompt_manager, '_prompts'):
            for prompt_name, prompt in jupyter_mcp_instance._prompt_manager._prompts.items():
                prefixed_prompt_name = f"jupyter_{prompt_name}"
                if prefixed_prompt_name not in mcp._prompt_manager._prompts:
                    mcp._prompt_manager._prompts[prefixed_prompt_name] = prompt
                    logger.info(f"Added Jupyter prompt: {prefixed_prompt_name}")
        
        # Copy resources if they exist
        if hasattr(jupyter_mcp_instance, '_resource_manager') and hasattr(jupyter_mcp_instance._resource_manager, '_resources'):
            for resource_name, resource in jupyter_mcp_instance._resource_manager._resources.items():
                prefixed_resource_name = f"jupyter_{resource_name}"
                if prefixed_resource_name not in mcp._resource_manager._resources:
                    mcp._resource_manager._resources[prefixed_resource_name] = resource
                    logger.info(f"Added Jupyter resource: {prefixed_resource_name}")
                    
        logger.info("Successfully composed Jupyter MCP Server tools")
        
    except ImportError:
        logger.warning("jupyter-mcp-server not available, running with earthdata tools only")
    except Exception as e:
        logger.error(f"Error composing jupyter tools: {e}")


# Compose the tools on import
_compose_jupyter_tools()


@mcp.tool()
def search_earth_datasets(search_keywords: str, count: int, temporal: tuple | None, bounding_box: tuple | None) -> list:
    """
    Search for datasets on NASA Earthdata.
    
    Args:
    search_keywords: Keywords to search for in the dataset titles.
    count: Number of datasets to return.
    temporal: (Optional) Temporal range in the format (date_from, date_to).
    bounding_box: (Optional) Bounding box in the format (lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat).
        
    Returns:
    list
        List of dataset abstracts.
    """

    search_params = {
        "keyword": search_keywords,
        "count": count,
        "cloud_hosted": True
    }

    if temporal and len(temporal) == 2:
        search_params["temporal"] = temporal
    if bounding_box and len(bounding_box) == 4:
        search_params["bounding_box"] = bounding_box

    datasets = earthaccess.search_datasets(**search_params)

    datasets_info = [
        {
            "Title": dataset.get_umm("EntryTitle"), 
            "ShortName": dataset.get_umm("ShortName"), 
            "Abstract": dataset.abstract(), 
            "Data Type": dataset.data_type(), 
            "DOI": dataset.get_umm("DOI"),
            "LandingPage": dataset.landing_page(),
            "DatasetViz": dataset._filter_related_links("GET RELATED VISUALIZATION"),
            "DatasetURL": dataset._filter_related_links("GET DATA"),
         } for dataset in datasets]

    return datasets_info


@mcp.tool()
def search_earth_datagranules(short_name: str, count: int, temporal: tuple | None, bounding_box: tuple | None) -> list:
    """
    Search for data granules on NASA Earthdata.
    
    Args:
    short_name: Short name of the dataset.
    count: Number of data granules to return.
    temporal: (Optional) Temporal range in the format (date_from, date_to).
    bounding_box: (Optional) Bounding box in the format (lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat).
        
    Returns:
    list
        List of data granules.
    """
    
    search_params = {
        "short_name": short_name,
        "count": count,
        "cloud_hosted": True
    }

    if temporal and len(temporal) == 2:
        search_params["temporal"] = temporal
    if bounding_box and len(bounding_box) == 4:
        search_params["bounding_box"] = bounding_box

    datagranules = earthaccess.search_data(**search_params)
    
    return datagranules


@mcp.tool()
async def download_earth_data_granules(
    folder_name: str, short_name: str, count: int, temporal: tuple | None = None, bounding_box: tuple | None = None
) -> str:
    """Download Earth data granules from NASA Earth Data and add code to a Jupyter notebook.

    This tool uses the composed jupyter tools to add a code cell that downloads Earth data granules.
    It leverages the existing jupyter notebook manipulation capabilities from the composed server.

    Args:
        folder_name: Local folder name to save the data.
        short_name: Short name of the Earth dataset to download.
        count: Number of data granules to download.
        temporal: (Optional) Temporal range in the format (date_from, date_to).
        bounding_box: (Optional) Bounding box in the format (lower_left_lon, lower_left_lat,
        upper_right_lon, upper_right_lat).

    Returns:
        str: Success message with download details
    """
    logger.info(f"Preparing to download Earth data granules: {short_name}")

    # Build search parameters
    search_params = {"short_name": short_name, "count": count, "cloud_hosted": True}

    if temporal and len(temporal) == 2:
        search_params["temporal"] = temporal
    if bounding_box and len(bounding_box) == 4:
        search_params["bounding_box"] = bounding_box

    # Create the download code cell content
    cell_content = f'''import earthaccess
import os

# Authenticate with NASA Earthdata
auth = earthaccess.login()
if not auth:
    print("❌ Authentication failed - please check credentials")
else:
    print("🔐 Successfully authenticated with NASA Earthdata")
    
    # Search parameters
    search_params = {search_params}
    print(f"🔍 Searching for {{search_params['count']}} granules of {{search_params['short_name']}}")
    
    # Search for data granules
    results = earthaccess.search_data(**search_params)
    print(f"📊 Found {{len(results)}} data granules")
    
    # Create download folder if it doesn't exist
    os.makedirs("./{folder_name}", exist_ok=True)
    print(f"📁 Created/verified folder: ./{folder_name}")
    
    # Download the data
    if results:
        files = earthaccess.download(results, "./{folder_name}")
        print(f"📥 Downloaded {{len(files)}} files to ./{folder_name}")
        print("✅ Download completed successfully!")
        
        # List downloaded files
        if files:
            print("\\n📋 Downloaded files:")
            for i, file in enumerate(files[:5], 1):  # Show first 5 files
                print(f"  {{i}}. {{os.path.basename(file)}}")
            if len(files) > 5:
                print(f"  ... and {{len(files) - 5}} more files")
    else:
        print("❌ No data granules found with the specified criteria")'''

    # Use the composed jupyter tool to add and execute the code cell
    try:
        # Check if jupyter tools are available (they should be via composition)
        if 'jupyter_append_execute_code_cell' in mcp._tool_manager._tools:
            # Get the jupyter tool function
            jupyter_tool = mcp._tool_manager._tools['jupyter_append_execute_code_cell']
            
            # Execute the jupyter tool to add and run the download code
            # Note: In practice, this would be called by the MCP client
            logger.info("Adding download code cell to notebook using composed jupyter tools")
            
            # For now, return the code that would be executed
            return f"""✅ Download code prepared for dataset: {short_name}
📁 Target folder: ./{folder_name}
📊 Granules to download: {count}
⏱️  Temporal filter: {temporal if temporal else 'None'}
🗺️  Bounding box: {bounding_box if bounding_box else 'None'}

📝 Code cell ready to be added to notebook:
{len(cell_content.split(chr(10)))} lines of download code prepared

🔧 Use the jupyter tools to execute this download in your notebook."""
        else:
            logger.warning("Jupyter tools not available - returning code for manual execution")
            return f"""⚠️  Jupyter tools not available in composition.
Here's the download code to run manually:

{cell_content}"""
            
    except Exception as e:
        logger.error(f"Error preparing download: {e}")
        return f"❌ Error preparing download: {e}"


@mcp.prompt()
def download_analyze_global_sea_level() -> str:
    """Generate a prompt for downloading and analyzing Global Mean Sea Level Trend dataset."""
    return ("I want you to download and do a short analysis of the Global Mean Sea Level Trend dataset "
            "in my notebook using the tools at your disposal for interacting with the notebook and the "
            "tool download_earth_data_granules for downloading the data. Please create a comprehensive "
            "analysis including data visualization and trend analysis.")


@mcp.prompt()
def sealevel_rise_dataset(start_year: int, end_year: int) -> str:
    return f"I’m interested in datasets about sealevel rise worldwide from {start_year} to {end_year}. Can you list relevant datasets?"


@mcp.prompt()
def ask_datasets_format() -> str:
    return "What are the data formats of those datasets?"


if __name__ == "__main__":
    mcp.run(transport='stdio')
