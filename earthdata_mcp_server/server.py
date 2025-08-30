# Copyright (c) 2023-2024 Datalayer, Inc.
#
# BSD 3-Clause License

import logging
import importlib

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


@mcp.prompt()
def sealevel_rise_dataset(start_year: int, end_year: int) -> str:
    return f"I’m interested in datasets about sealevel rise worldwide from {start_year} to {end_year}. Can you list relevant datasets?"


@mcp.prompt()
def ask_datasets_format() -> str:
    return "What are the data formats of those datasets?"


if __name__ == "__main__":
    mcp.run(transport='stdio')
