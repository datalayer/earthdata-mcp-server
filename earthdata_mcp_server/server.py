# Copyright (c) 2023-2024 Datalayer, Inc.
#
# BSD 3-Clause License

import logging
import importlib

import click
import httpx
import uvicorn
from fastapi import Request
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP

import earthaccess


###############################################################################


class FastMCPWithCORS(FastMCP):
    def streamable_http_app(self) -> Starlette:
        """Return StreamableHTTP server app with CORS middleware
        See: https://github.com/modelcontextprotocol/python-sdk/issues/187
        """
        # Get the original Starlette app
        app = super().streamable_http_app()
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, should set specific domains
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )        
        return app
    
    def sse_app(self, mount_path: str | None = None) -> Starlette:
        """Return SSE server app with CORS middleware"""
        # Get the original Starlette app
        app = super().sse_app(mount_path)
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, should set specific domains
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )        
        return app


# Create the composed server that will include both earthdata and jupyter tools
mcp = FastMCPWithCORS("earthdata-jupyter-composed")

logger = logging.getLogger(__name__)

# Reference to jupyter server module
jupyter_mcp_module = None


# Function to safely import and compose jupyter-mcp-server tools
def _compose_jupyter_tools():
    """Import and add Jupyter MCP Server tools to our earthdata server."""
    global jupyter_mcp_module
    try:
        # Import the jupyter mcp server module
        jupyter_mcp_module = importlib.import_module("jupyter_mcp_server.server")
        jupyter_mcp_instance = jupyter_mcp_module.mcp
        
        # Log original jupyter tools before composition
        if hasattr(jupyter_mcp_instance, '_tool_manager') and hasattr(jupyter_mcp_instance._tool_manager, '_tools'):
            original_tools = list(jupyter_mcp_instance._tool_manager._tools.keys())
            logger.info(f"Original Jupyter tools found: {original_tools}")
            
            # Track how many tools were added/updated
            added_count = 0
            updated_count = 0
            
            # Add jupyter tools to our earthdata server without prefix
            for tool_name, tool in jupyter_mcp_instance._tool_manager._tools.items():
                if tool_name not in mcp._tool_manager._tools:
                    # Add the tool with original name
                    mcp._tool_manager._tools[tool_name] = tool
                    logger.info(f"Added Jupyter tool: {tool_name}")
                    added_count += 1
                else:
                    # Update existing tool (in case authentication config changed)
                    mcp._tool_manager._tools[tool_name] = tool
                    logger.info(f"Updated Jupyter tool: {tool_name}")
                    updated_count += 1
            
            logger.info(f"Tool composition summary: {added_count} added, {updated_count} updated")
        else:
            logger.warning("Jupyter MCP instance does not have tool manager")
        
        # Also copy any prompts if they exist
        if hasattr(jupyter_mcp_instance, '_prompt_manager') and hasattr(jupyter_mcp_instance._prompt_manager, '_prompts'):
            for prompt_name, prompt in jupyter_mcp_instance._prompt_manager._prompts.items():
                if prompt_name not in mcp._prompt_manager._prompts:
                    mcp._prompt_manager._prompts[prompt_name] = prompt
                    logger.info(f"Added Jupyter prompt: {prompt_name}")
                else:
                    mcp._prompt_manager._prompts[prompt_name] = prompt
                    logger.info(f"Updated Jupyter prompt: {prompt_name}")
        
        # Copy resources if they exist
        if hasattr(jupyter_mcp_instance, '_resource_manager') and hasattr(jupyter_mcp_instance._resource_manager, '_resources'):
            for resource_name, resource in jupyter_mcp_instance._resource_manager._resources.items():
                if resource_name not in mcp._resource_manager._resources:
                    mcp._resource_manager._resources[resource_name] = resource
                    logger.info(f"Added Jupyter resource: {resource_name}")
                else:
                    mcp._resource_manager._resources[resource_name] = resource
                    logger.info(f"Updated Jupyter resource: {resource_name}")
        
        # Log all available tools after composition
        all_tools = list(mcp._tool_manager._tools.keys())
        logger.info(f"All tools available after composition ({len(all_tools)}): {all_tools}")
        logger.info("Successfully composed Jupyter MCP Server tools")
        
    except ImportError as e:
        logger.warning(f"jupyter-mcp-server not available: {e}, running with earthdata tools only")
        # Log earthdata-only tools
        earthdata_tools = list(mcp._tool_manager._tools.keys())
        logger.info(f"Earthdata-only tools available: {earthdata_tools}")
    except Exception as e:
        logger.error(f"Error composing jupyter tools: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Log current tools even if composition failed
        current_tools = list(mcp._tool_manager._tools.keys())
        logger.info(f"Tools available after failed composition: {current_tools}")


# Compose the tools on import - wrapped in try/except to prevent startup failure
try:
    _compose_jupyter_tools()
except Exception as e:
    logger.error(f"Failed to compose jupyter tools during import: {e}")
    # Log current earthdata tools
    earthdata_tools = list(mcp._tool_manager._tools.keys())
    logger.info(f"Continuing with earthdata-only tools: {earthdata_tools}")


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
) -> list:
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
        result: Result of the jupyter tool call to add and execute the code cell.
    """
    logger.info(f"Preparing to download Earth data granules: {short_name}")

    # Build search parameters
    search_params = {"short_name": short_name, "count": count, "cloud_hosted": True}

    if temporal and len(temporal) == 2:
        search_params["temporal"] = temporal
    if bounding_box and len(bounding_box) == 4:
        search_params["bounding_box"] = bounding_box

    # Create the download code cell content
    cell_content = f'''
import earthaccess
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
        # Execute the jupyter tool to add and run the download code
        logger.info("Adding download code cell to notebook using composed jupyter tools")

        result = await mcp.call_tool("append_execute_code_cell", {
            "cell_source": cell_content,
        })

        if result:
            logger.info("Download code cell added and executed successfully")
        else:
            logger.warning("Failed to add and execute download code cell")

    except Exception as e:
        logger.error(f"Error adding download code cell: {e}")

    return result

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


###############################################################################
# Custom Routes (delegated to jupyter-mcp-server when available).


@mcp.custom_route("/api/connect", ["PUT"])
async def connect(request: Request):
    """Connect to a document and a runtime from the Earthdata MCP server."""
    if jupyter_mcp_module and hasattr(jupyter_mcp_module, 'connect'):
        return await jupyter_mcp_module.connect(request)
    else:
        return JSONResponse({"success": False, "error": "Jupyter MCP Server not available"}, status_code=503)


@mcp.custom_route("/api/stop", ["DELETE"])
async def stop(request: Request):
    """Stop the jupyter kernel."""
    if jupyter_mcp_module and hasattr(jupyter_mcp_module, 'stop'):
        return await jupyter_mcp_module.stop(request)
    else:
        return JSONResponse({"success": False, "error": "Jupyter MCP Server not available"}, status_code=503)


@mcp.custom_route("/api/healthz", ["GET"])
async def health_check(request: Request):
    """Custom health check endpoint for earthdata-jupyter-composed server"""
    kernel_status = "unknown"
    jupyter_available = jupyter_mcp_module is not None
    
    if jupyter_available:
        try:
            # Try to get kernel status from jupyter module
            kernel = getattr(jupyter_mcp_module, 'kernel', None)
            if kernel:
                kernel_status = "alive" if hasattr(kernel, 'is_alive') and kernel.is_alive() else "dead"
            else:
                kernel_status = "not_initialized"
        except Exception:
            kernel_status = "error"
    
    return JSONResponse(
        {
            "success": True,
            "service": "earthdata-jupyter-composed-mcp-server",
            "message": "Earthdata-Jupyter Composed MCP Server is running.",
            "status": "healthy",
            "jupyter_available": jupyter_available,
            "kernel_status": kernel_status,
        }
    )


###############################################################################
# Commands.


@click.group()
def server():
    """Manages Earthdata-Jupyter Composed MCP Server."""
    pass


@server.command("connect")
@click.option(
    "--provider",
    envvar="PROVIDER",
    type=click.Choice(["jupyter", "datalayer"]),
    default="jupyter",
    help="The provider to use for the document and runtime. Defaults to 'jupyter'.",
)
@click.option(
    "--runtime-url",
    envvar="RUNTIME_URL",
    type=click.STRING,
    default="http://localhost:8888",
    help="The runtime URL to use. For the jupyter provider, this is the Jupyter server URL. For the datalayer provider, this is the Datalayer runtime URL.",
)
@click.option(
    "--runtime-id",
    envvar="RUNTIME_ID",
    type=click.STRING,
    default=None,
    help="The kernel ID to use. If not provided, a new kernel should be started.",
)
@click.option(
    "--runtime-token",
    envvar="RUNTIME_TOKEN",
    type=click.STRING,
    default=None,
    help="The runtime token to use for authentication with the provider.  For the jupyter provider, this is the jupyter token. For the datalayer provider, this is the datalayer token. If not provided, the provider should accept anonymous requests.",
)
@click.option(
    "--document-url",
    envvar="DOCUMENT_URL",
    type=click.STRING,
    default="http://localhost:8888",
    help="The document URL to use. For the jupyter provider, this is the Jupyter server URL. For the datalayer provider, this is the Datalayer document URL.",
)
@click.option(
    "--document-id",
    envvar="DOCUMENT_ID",
    type=click.STRING,
    default="notebook.ipynb",
    help="The document id to use. For the jupyter provider, this is the notebook path. For the datalayer provider, this is the notebook path.",
)
@click.option(
    "--document-token",
    envvar="DOCUMENT_TOKEN",
    type=click.STRING,
    default=None,
    help="The document token to use for authentication with the provider. For the jupyter provider, this is the jupyter token. For the datalayer provider, this is the datalayer token. If not provided, the provider should accept anonymous requests.",
)
@click.option(
    "--earthdata-mcp-server-url",
    envvar="EARTHDATA_MCP_SERVER_URL",
    type=click.STRING,
    default="http://localhost:4040",
    help="The URL of the Earthdata MCP Server to connect to. Defaults to 'http://localhost:4040'.",
)
def connect_command(
    earthdata_mcp_server_url: str,
    runtime_url: str,
    runtime_id: str,
    runtime_token: str,
    document_url: str,
    document_id: str,
    document_token: str,
    provider: str,
):
    """Command to connect an Earthdata MCP Server to a document and a runtime."""
    
    # Set configuration through jupyter module if available
    if jupyter_mcp_module:
        try:
            # Import the config module from jupyter-mcp-server
            config_module = importlib.import_module("jupyter_mcp_server.config")
            
            # Set configuration using the singleton
            config_module.set_config(
                provider=provider,
                runtime_url=runtime_url,
                runtime_id=runtime_id,
                runtime_token=runtime_token,
                document_url=document_url,
                document_id=document_id,
                document_token=document_token
            )
            
            config = config_module.get_config()
            
        except Exception as e:
            logger.error(f"Error setting configuration through jupyter module: {e}")
            raise click.ClickException(f"Failed to set configuration: {e}")
    else:
        logger.error("jupyter-mcp-server not available, cannot connect")
        raise click.ClickException("jupyter-mcp-server module not available")

    try:
        from jupyter_mcp_server.models import DocumentRuntime
        document_runtime = DocumentRuntime(
            provider=config.provider,
            runtime_url=config.runtime_url,
            runtime_id=config.runtime_id,
            runtime_token=config.runtime_token,
            document_url=config.document_url,
            document_id=config.document_id,
            document_token=config.document_token,
        )

        r = httpx.put(
            f"{earthdata_mcp_server_url}/api/connect",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            content=document_runtime.model_dump_json(),
        )
        r.raise_for_status()
    except ImportError:
        logger.error("jupyter-mcp-server not available, cannot connect")
        raise click.ClickException("jupyter-mcp-server module not available")


@server.command("stop")
@click.option(
    "--earthdata-mcp-server-url",
    envvar="EARTHDATA_MCP_SERVER_URL",
    type=click.STRING,
    default="http://localhost:4040",
    help="The URL of the Earthdata MCP Server to stop. Defaults to 'http://localhost:4040'.",
)
def stop_command(earthdata_mcp_server_url: str):
    """Stop the earthdata MCP server."""
    r = httpx.delete(
        f"{earthdata_mcp_server_url}/api/stop",
    )
    r.raise_for_status()


@server.command("start")
@click.option(
    "--transport",
    envvar="TRANSPORT",
    type=click.Choice(["stdio", "streamable-http"]),
    default="stdio",
    help="The transport to use for the MCP server. Defaults to 'stdio'.",
)
@click.option(
    "--provider",
    envvar="PROVIDER",
    type=click.Choice(["jupyter", "datalayer"]),
    default="jupyter",
    help="The provider to use for the document and runtime. Defaults to 'jupyter'.",
)
@click.option(
    "--runtime-url",
    envvar="RUNTIME_URL",
    type=click.STRING,
    default="http://localhost:8888",
    help="The runtime URL to use. For the jupyter provider, this is the Jupyter server URL. For the datalayer provider, this is the Datalayer runtime URL.",
)
@click.option(
    "--start-new-runtime",
    envvar="START_NEW_RUNTIME",
    type=click.BOOL,
    default=True,
    help="Start a new runtime or use an existing one.",
)
@click.option(
    "--runtime-id",
    envvar="RUNTIME_ID",
    type=click.STRING,
    default=None,
    help="The kernel ID to use. If not provided, a new kernel should be started.",
)
@click.option(
    "--runtime-token",
    envvar="RUNTIME_TOKEN",
    type=click.STRING,
    default=None,
    help="The runtime token to use for authentication with the provider. If not provided, the provider should accept anonymous requests.",
)
@click.option(
    "--document-url",
    envvar="DOCUMENT_URL",
    type=click.STRING,
    default="http://localhost:8888",
    help="The document URL to use. For the jupyter provider, this is the Jupyter server URL. For the datalayer provider, this is the Datalayer document URL.",
)
@click.option(
    "--document-id",
    envvar="DOCUMENT_ID",
    type=click.STRING,
    default="notebook.ipynb",
    help="The document id to use. For the jupyter provider, this is the notebook path. For the datalayer provider, this is the notebook path.",
)
@click.option(
    "--document-token",
    envvar="DOCUMENT_TOKEN",
    type=click.STRING,
    default=None,
    help="The document token to use for authentication with the provider. If not provided, the provider should accept anonymous requests.",
)
@click.option(
    "--port",
    envvar="PORT",
    type=click.INT,
    default=4040,
    help="The port to use for the Streamable HTTP transport. Ignored for stdio transport.",
)
def start_command(
    transport: str,
    start_new_runtime: bool,
    runtime_url: str,
    runtime_id: str,
    runtime_token: str,
    document_url: str,
    document_id: str,
    document_token: str,
    port: int,
    provider: str,
):
    """Start the Earthdata-Jupyter Composed MCP server with a transport."""

    # Set configuration through jupyter module if available
    if jupyter_mcp_module:
        try:
            # Import the config module from jupyter-mcp-server
            config_module = importlib.import_module("jupyter_mcp_server.config")
            
            # Set configuration using the singleton
            config_module.set_config(
                transport=transport,
                provider=provider,
                runtime_url=runtime_url,
                start_new_runtime=start_new_runtime,
                runtime_id=runtime_id,
                runtime_token=runtime_token,
                document_url=document_url,
                document_id=document_id,
                document_token=document_token,
                port=port
            )
            
            logger.info("Configuration updated through jupyter-mcp-server config")
            
            # Re-compose tools with updated configuration
            logger.info("Re-syncing jupyter tools with updated configuration...")
            _compose_jupyter_tools()
            
        except Exception as e:
            logger.error(f"Error setting configuration through jupyter module: {e}")

    # Initialize jupyter kernel if specified and jupyter module is available
    config = None
    if jupyter_mcp_module:
        try:
            config_module = importlib.import_module("jupyter_mcp_server.config")
            config = config_module.get_config()
        except Exception:
            pass
            
    if config and (config.start_new_runtime or config.runtime_id) and jupyter_mcp_module:
        try:
            # Try different ways to access the kernel start function
            if hasattr(jupyter_mcp_module, '__start_kernel'):
                jupyter_mcp_module.__start_kernel()
            elif hasattr(jupyter_mcp_module, '_start_kernel'):
                jupyter_mcp_module._start_kernel()
            else:
                logger.warning("Jupyter kernel start function not found")
        except Exception as e:
            logger.error(f"Failed to start kernel on startup: {e}")

    logger.info(f"Starting Earthdata-Jupyter Composed MCP Server with transport: {transport}")
    
    # Log all available tools at startup
    all_tools = list(mcp._tool_manager._tools.keys())
    logger.info(f"Server starting with {len(all_tools)} tools available: {all_tools}")

    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "streamable-http":
        uvicorn.run(mcp.streamable_http_app(), host="0.0.0.0", port=port)  # noqa: S104
    else:
        raise Exception("Transport should be `stdio` or `streamable-http`.")


###############################################################################
# Main.


if __name__ == "__main__":
    server()
