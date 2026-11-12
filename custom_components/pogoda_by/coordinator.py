"""One RSS request per station for all its sensors."""

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import CannotConnect, PogodaByClient
from .const import CONF_INTERVAL, CONF_STATION, DEFAULT_INTERVAL, DOMAIN
from .parser import InvalidData, Observation

_LOGGER = logging.getLogger(__name__)


class PogodaByCoordinator(DataUpdateCoordinator[Observation]):
    """Poll only the chosen station; metadata is persisted in the entry."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: PogodaByClient) -> None:
        super().__init__(
            hass, _LOGGER, name=f"{DOMAIN}_{entry.data[CONF_STATION]}",
            config_entry=entry,
            update_interval=timedelta(minutes=entry.options.get(CONF_INTERVAL, DEFAULT_INTERVAL)),
        )
        self.client = client
        self.station = entry.data

    async def _async_update_data(self) -> Observation:
        try:
            return await self.client.async_observation(self.station[CONF_STATION])
        except (CannotConnect, InvalidData) as err:
            raise UpdateFailed(str(err)) from err
