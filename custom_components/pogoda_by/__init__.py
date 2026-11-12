"""Pogoda.by weather observations."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PogodaByClient
from .coordinator import PogodaByCoordinator

PLATFORMS = [Platform.SENSOR]
type PogodaByConfigEntry = ConfigEntry[PogodaByCoordinator]


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
