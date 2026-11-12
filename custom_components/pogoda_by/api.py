"""Asynchronous, bounded HTTP access to Pogoda.by."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import aiohttp

from .const import CATALOG_URL, MAX_RESPONSE_BYTES, REQUEST_TIMEOUT, RSS_URL
from .parser import InvalidData, Observation, Station, normalize_catalog, parse_rss


class CannotConnect(Exception):
    """Network, timeout, HTTP or response encoding error."""


class PogodaByClient:
    """Use Home Assistant's shared session; do not create or close a session."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    async def _get(self, url: str, params: dict[str, str] | None = None) -> str:
        try:
            async with self._session.get(
                url,
                params=params,
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
                headers={"Accept": "application/json, application/rss+xml, application/xml, text/xml"},
            ) as response:
                response.raise_for_status()
                body = bytearray()
                async for chunk in response.content.iter_chunked(65536):
                    body.extend(chunk)
                    if len(body) > MAX_RESPONSE_BYTES:
                        raise InvalidData("Response exceeds the maximum size")
                return body.decode(response.charset or "utf-8-sig")
        except (aiohttp.ClientError, asyncio.TimeoutError, UnicodeError, LookupError) as err:
            raise CannotConnect("Unable to retrieve Pogoda.by data") from err

    async def async_catalog(self) -> dict[str, dict[str, Station]]:
        text = await self._get(CATALOG_URL)
        try:
            payload: Any = json.loads(text.lstrip("\ufeff"))
        except ValueError as err:
            raise InvalidData("Catalogue is not JSON") from err
        return normalize_catalog(payload)

    async def async_observation(self, station_id: str) -> Observation:
        return parse_rss(await self._get(RSS_URL, {"station": station_id}))
