"""Package entry point for ``python -m earthdata_mcp_server``."""

from .server import server


if __name__ == "__main__":
    server()
