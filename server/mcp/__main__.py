"""Entry point for running the MCP server: python -m server.mcp"""

import asyncio

from server.mcp.server import main

if __name__ == "__main__":
    asyncio.run(main())
