# Tools

The server offers **15 tools total**: 3 Earthdata-specific tools plus 12 Jupyter notebook manipulation tools (prefixed with `jupyter_`).

### Earthdata Tools

#### `search_earth_datasets`

- Search for datasets on NASA Earthdata.
- Input:
  - search_keywords (str): Keywords to search for in the dataset titles.
  - count (int): Number of datasets to return.
  - temporal (tuple): (Optional) Temporal range in the format (date_from, date_to).
  - bounding_box (tuple): (Optional) Bounding box in the format (lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat).
- Returns: List of dataset abstracts.

#### `search_earth_datagranules`

- Search for data granules on NASA Earthdata.
- Input:
  - short_name (str): Short name of the dataset.
  - count (int): Number of data granules to return.
  - temporal (tuple): (Optional) Temporal range in the format (date_from, date_to).
  - bounding_box (tuple): (Optional) Bounding box in the format (lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat).
- Returns: List of data granules.

#### `download_earth_data_granules` 🆕

- Download Earth data granules from NASA Earth Data and integrate with Jupyter notebooks.
- This tool combines earthdata search capabilities with jupyter notebook manipulation to create a seamless download workflow.
- **Authentication**: Requires NASA Earthdata Login credentials (see [Authentication section](./authentication.md))
- Input:
  - folder_name (str): Local folder name to save the data.
  - short_name (str): Short name of the Earth dataset to download.
  - count (int): Number of data granules to download.
  - temporal (tuple): (Optional) Temporal range in the format (date_from, date_to).
  - bounding_box (tuple): (Optional) Bounding box in the format (lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat).
- Returns: Success message with download code preparation details.
- **Integration**: Uses composed jupyter tools to add download code to notebooks for interactive execution.

### Jupyter Tools (Composed)

The following Jupyter notebook manipulation tools are available with the `jupyter_` prefix:

- **`jupyter_append_markdown_cell`**: Add markdown cells to notebooks
- **`jupyter_insert_markdown_cell`**: Insert markdown cells at specific positions
- **`jupyter_overwrite_cell_source`**: Modify existing cell content
- **`jupyter_append_execute_code_cell`**: Add and execute code cells
- **`jupyter_insert_execute_code_cell`**: Insert and execute code cells at specific positions
- **`jupyter_execute_cell_with_progress`**: Execute cells with progress monitoring
- **`jupyter_execute_cell_simple_timeout`**: Execute cells with timeout
- **`jupyter_execute_cell_streaming`**: Execute cells with streaming output
- **`jupyter_read_all_cells`**: Read all notebook cells
- **`jupyter_read_cell`**: Read specific notebook cells
- **`jupyter_get_notebook_info`**: Get notebook metadata
- **`jupyter_delete_cell`**: Delete notebook cells

For detailed documentation of the Jupyter tools, see the [Jupyter MCP Server documentation](https://github.com/datalayer/jupyter-mcp-server).
