"""Weather MCP server — run with: python -m server.mcp.weather"""

import asyncio

from server.mcp.weather.server import main

if __name__ == "__main__":
    asyncio.run(main())
