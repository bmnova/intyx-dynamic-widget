"""Holidays MCP server — run with: python -m server.mcp.holidays"""

import asyncio

from server.mcp.holidays.server import main

if __name__ == "__main__":
    asyncio.run(main())
