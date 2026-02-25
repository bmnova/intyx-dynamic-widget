"""IP geolocation tool handlers."""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from server.data_sources.ip_geo_source import IPGeoSource


async def geolocate_ip(arguments: dict[str, Any]) -> list[TextContent]:
    data = IPGeoSource.fetch(ip_address=arguments.get("ip_address"))
    return [TextContent(type="text", text=json.dumps(data))]
