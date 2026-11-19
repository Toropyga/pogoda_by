"""One RSS request per station for all its sensors."""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import CannotConnect, PogodaByClient
from .const import (
    CONF_INTERVAL, CONF_MAX_OBSERVATION_AGE, CONF_STATION, DEFAULT_INTERVAL,
    DEFAULT_MAX_OBSERVATION_AGE, DOMAIN, FUTURE_TOLERANCE_SECONDS,
)
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
        self.max_observation_age = timedelta(hours=entry.options.get(
            CONF_MAX_OBSERVATION_AGE, DEFAULT_MAX_OBSERVATION_AGE,
        ))
        self.last_successful_fetch: datetime | None = None
        self._cancel_freshness_timer: Callable[[], None] | None = None
        entry.async_on_unload(self._async_cancel_freshness_timer)

    @property
    def freshness(self) -> str:
        """Describe the cached observation, independently of request success."""
        if self.data is None or self.last_successful_fetch is None:
            return "unknown"
        observed = self.data.values.get("observation_time")
        if not isinstance(observed, datetime) or observed.tzinfo is None:
            return "unknown"
        # Judge clock skew at reception: merely waiting does not validate a bad date.
        if observed > self.last_successful_fetch + timedelta(seconds=FUTURE_TOLERANCE_SECONDS):
            return "unknown"
        return "stale" if dt_util.utcnow() - observed > self.max_observation_age else "fresh"

    @callback
    def _async_cancel_freshness_timer(self) -> None:
        """Cancel the deadline when replaced or when the entry is unloaded."""
        if self._cancel_freshness_timer is not None:
            self._cancel_freshness_timer()
            self._cancel_freshness_timer = None

    @callback
    def _async_schedule_freshness_timer(self, observation: Observation) -> None:
        """Notify entities at expiry without changing request status or fetching RSS."""
        self._async_cancel_freshness_timer()
        observed = observation.values.get("observation_time")
        received = self.last_successful_fetch
        if not isinstance(observed, datetime) or observed.tzinfo is None or received is None:
            return
        if observed > received + timedelta(seconds=FUTURE_TOLERANCE_SECONDS):
            return
        # Equality is still fresh; schedule the first instant beyond the threshold.
        # Avoid datetime overflow for extreme but syntactically valid RSS dates.
        if datetime.max.replace(tzinfo=UTC) - observed <= self.max_observation_age:
            return
        expires = observed + self.max_observation_age + timedelta(microseconds=1)
        if expires > dt_util.utcnow():
            self._cancel_freshness_timer = async_track_point_in_utc_time(
                self.hass, self._async_freshness_expired, expires,
            )

    @callback
    def _async_freshness_expired(self, now: datetime) -> None:
        """Write changed availability even between polls or during an outage."""
        self._cancel_freshness_timer = None
        self.async_update_listeners()

    async def _async_update_data(self) -> Observation:
        try:
            observation = await self.client.async_observation(self.station[CONF_STATION])
        except (CannotConnect, InvalidData) as err:
            raise UpdateFailed(str(err)) from err
        self.last_successful_fetch = dt_util.utcnow()
        self._async_schedule_freshness_timer(observation)
        return observation
