# Copyright (c) 2023-2024 Datalayer, Inc.
#
# BSD 3-Clause License

import logging

from mcp.server.fastmcp import FastMCP

import earthaccess


mcp = FastMCP("earthdata")


logger = logging.getLogger(__name__)


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


if __name__ == "__main__":
    mcp.run(transport='stdio')
