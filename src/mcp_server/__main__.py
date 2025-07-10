"""
Main entry point for running the MCP server as a module.

This allows running the server with:
python -m src.mcp_server
"""

from .server import main

if __name__ == "__main__":
    main() 