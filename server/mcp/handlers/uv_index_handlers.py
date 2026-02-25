"""UV index tool handlers."""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from server.data_sources.uv_index_source import UVIndexSource


async def get_uv_index(arguments: dict[str, Any]) -> list[TextContent]:
    data = UVIndexSource.fetch_by_coords(
        lat=arguments["lat"],
        lon=arguments["lon"],
    )
    return [TextContent(type="text", text=json.dumps(data))]
