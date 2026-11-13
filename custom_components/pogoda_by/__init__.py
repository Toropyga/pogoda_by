"""Pogoda.by weather observations."""

from __future__ import annotations

import logging
from typing import TypeAlias

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .api import PogodaByClient
from .const import DOMAIN
from .coordinator import PogodaByCoordinator
from .dashboard import async_setup_card

_LOGGER = logging.getLogger(__name__)
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
PLATFORMS = [Platform.SENSOR]
PogodaByConfigEntry: TypeAlias = ConfigEntry[PogodaByCoordinator]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the shared dashboard module before station updates begin."""
    try:
        await async_setup_card(hass)
    except Exception:  # A dashboard problem must not disable weather sensors.
        _LOGGER.exception(
            "Could not register Pogoda.by Card. Weather sensors can still load. "
            "Restart Home Assistant to retry, or follow docs/CARD.md"
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: PogodaByConfigEntry) -> bool:
    """Retry automatically if the first observation cannot be fetched."""
    coordinator = PogodaByCoordinator(hass, entry, PogodaByClient(async_get_clientsession(hass)))
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_options))
    return True


async def _async_update_options(hass: HomeAssistant, entry: PogodaByConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: PogodaByConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
