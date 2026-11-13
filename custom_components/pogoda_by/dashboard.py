"""Serve the bundled card and register it in Lovelace's resource collection."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
import logging
from pathlib import Path
from urllib.parse import urlsplit

from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.core import HomeAssistant

from .const import DOMAIN, VERSION

_LOGGER = logging.getLogger(__name__)
CARD_PATH = Path(__file__).parent / "frontend" / "pogoda-by-card.js"
CARD_BASE_URL = f"/{DOMAIN}/pogoda-by-card.js"
CARD_URL = f"{CARD_BASE_URL}?v={VERSION}"
LEGACY_CARD_URL = "/local/pogoda-by-card.js"
_DATA_CARD = f"{DOMAIN}_dashboard"


@dataclass
class CardRegistration:
    """One HTTP route per HA instance, including concurrent config entries."""

    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    static_registered: bool = False


def _is_card_resource(url: str) -> bool:
    """Match only our same-origin canonical and previous manual URLs."""
    parts = urlsplit(url)
    return (
        not parts.scheme
        and not parts.netloc
        and parts.path in (CARD_BASE_URL, LEGACY_CARD_URL)
    )


async def async_setup_card(hass: HomeAssistant) -> None:
    """Register once, safely loading existing resources before any mutation.

    HTTP routes live for the lifetime of HA and are shared between stations.
    YAML resources are user-owned; we serve the file but do not edit their YAML.
    """
    state = hass.data.setdefault(_DATA_CARD, CardRegistration())
    async with state.lock:
        if not state.static_registered:
            await hass.http.async_register_static_paths(
                [StaticPathConfig(CARD_BASE_URL, str(CARD_PATH), False)]
            )
            state.static_registered = True

        lovelace = hass.data.get("lovelace")
        # Prefer the current LovelaceData attribute; retain older dict support.
        resources = (
            lovelace.get("resources")
            if isinstance(lovelace, dict)
            else getattr(lovelace, "resources", None)
        )
        if not isinstance(resources, ResourceStorageCollection):
            _LOGGER.warning(
                "Pogoda.by Card is available at %s, but automatic resource "
                "registration requires Lovelace storage resources. If resources "
                "are managed in YAML, add this URL with type: module; see "
                "docs/CARD.ru.md (or docs/CARD.md)",
                CARD_URL,
            )
            return

        # In older HA releases the resource collection is lazy-loaded. Creating
        # an item before this load could overwrite unrelated dashboard resources.
        if not resources.loaded:
            await resources.async_load()

        existing = [
            item for item in resources.async_items()
            if _is_card_resource(item["url"])
        ]
        # Keep a canonical record if present, otherwise migrate the manual one.
        existing.sort(key=lambda item: urlsplit(item["url"]).path != CARD_BASE_URL)
        if existing:
            item = existing[0]
            if item["url"] != CARD_URL or item["type"] != "module":
                await resources.async_update_item(
                    item["id"], {"url": CARD_URL, "res_type": "module"}
                )
            for duplicate in existing[1:]:
                await resources.async_delete_item(duplicate["id"])
        else:
            await resources.async_create_item(
                {"url": CARD_URL, "res_type": "module"}
            )
        _LOGGER.debug("Pogoda.by Card resource registered: %s", CARD_URL)
