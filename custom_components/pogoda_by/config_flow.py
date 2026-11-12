"""Country -> station setup and polling options."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import selector

from .api import CannotConnect, PogodaByClient
from .const import (
    CONF_COUNTRY, CONF_INTERVAL, CONF_STATION, DEFAULT_INTERVAL, DOMAIN,
    MAX_INTERVAL, MIN_INTERVAL,
)
from .parser import InvalidData, Station

class PogodaByConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Allow multiple stations, while preventing duplicate station entries."""

    VERSION = 1

    def __init__(self) -> None:
        self._catalog: dict[str, dict[str, Station]] | None = None
        self._country: str | None = None

    def _client(self) -> PogodaByClient:
        return PogodaByClient(async_get_clientsession(self.hass))

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if self._catalog is None:
            try:
                self._catalog = await self._client().async_catalog()
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidData:
                errors["base"] = "invalid_data"
        if self._catalog is None:
            # An empty form provides a Submit button to retry catalogue retrieval.
            return self.async_show_form(step_id="user", data_schema=vol.Schema({}), errors=errors)
        if user_input is not None and CONF_COUNTRY in user_input:
            country = user_input[CONF_COUNTRY]
            if country in self._catalog:
                self._country = country
                return await self.async_step_station()
            errors[CONF_COUNTRY] = "invalid_country"
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_COUNTRY): selector.CountrySelector(
                selector.CountrySelectorConfig(countries=sorted(self._catalog))
            )}),
            errors=errors,
        )

    async def async_step_station(self, user_input: dict[str, Any] | None = None):
        if self._catalog is None or self._country not in self._catalog:
            return await self.async_step_user()
        stations = self._catalog[self._country]
        errors: dict[str, str] = {}
        if user_input is not None:
            station_id = user_input.get(CONF_STATION)
            if station_id not in stations:
                errors[CONF_STATION] = "invalid_station"
            else:
                station = stations[station_id]
                await self.async_set_unique_id(f"{station.country}_{station.station_id}")
                self._abort_if_unique_id_configured()
                try:
                    await self._client().async_observation(station.station_id)
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                except InvalidData:
                    errors["base"] = "no_weather"
                else:
                    return self.async_create_entry(
                        title=f"{station.name} ({station.country}, {station.station_id})",
                        data=station.as_dict(),
                    )
        choices = [
            selector.SelectOptionDict(value=station.station_id, label=f"{station.name} [{station.station_id}]")
            for station in sorted(stations.values(), key=lambda row: (row.name.casefold(), row.station_id))
        ]
        return self.async_show_form(
            step_id="station",
            data_schema=vol.Schema({vol.Required(CONF_STATION): selector.SelectSelector(
                selector.SelectSelectorConfig(options=choices, mode=selector.SelectSelectorMode.DROPDOWN)
            )}),
            errors=errors,
            description_placeholders={"country": self._country},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return PogodaByOptionsFlow()


class PogodaByOptionsFlow(config_entries.OptionsFlow):
    """Change the interval without editing YAML."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_INTERVAL, default=self.config_entry.options.get(CONF_INTERVAL, DEFAULT_INTERVAL)):
                    vol.All(vol.Coerce(int), vol.Range(min=MIN_INTERVAL, max=MAX_INTERVAL)),
            }),
        )
