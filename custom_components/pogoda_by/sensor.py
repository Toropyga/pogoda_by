"""Weather sensors backed by one coordinated RSS response."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass,
)
from homeassistant.const import (
    EntityCategory, PERCENTAGE, UnitOfLength, UnitOfPressure, UnitOfSpeed, UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import PogodaByConfigEntry
from .const import CONF_COUNTRY, CONF_STATION, DOMAIN
from .coordinator import PogodaByCoordinator

PARALLEL_UPDATES = 0

SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="temperature", translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="pressure", translation_key="pressure",
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        native_unit_of_measurement=UnitOfPressure.HPA,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="pressure_trend", translation_key="pressure_trend", icon="mdi:trending-up",
    ),
    SensorEntityDescription(
        key="wind_speed", translation_key="wind_speed", device_class=SensorDeviceClass.WIND_SPEED,
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="wind_direction", translation_key="wind_direction", icon="mdi:compass",
    ),
    SensorEntityDescription(key="condition", translation_key="condition", icon="mdi:weather-partly-cloudy"),
    SensorEntityDescription(
        key="observation_time", translation_key="observation_time",
        device_class=SensorDeviceClass.TIMESTAMP, entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="station", translation_key="station", icon="mdi:map-marker",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="humidity", translation_key="humidity", device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="wind_gust", translation_key="wind_gust", device_class=SensorDeviceClass.WIND_SPEED,
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="visibility", translation_key="visibility", device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: PogodaByConfigEntry, async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    added: set[str] = set()

    @callback
    def async_add_available() -> None:
        if not coordinator.last_update_success:
            return
        entities = []
        for description in SENSORS:
            key = description.key
            if key not in added and (key == "station" or key in coordinator.data.values):
                added.add(key)
                entities.append(PogodaBySensor(coordinator, description))
        if entities:
            async_add_entities(entities)

    async_add_available()
    # Optional fields may appear in a later observation.
    entry.async_on_unload(coordinator.async_add_listener(async_add_available))


class PogodaBySensor(CoordinatorEntity[PogodaByCoordinator], SensorEntity):
    """One field; missing values never become false zero measurements."""

    _attr_has_entity_name = True
    _attr_attribution = "Данные предоставлены Белгидрометом (pogoda.by)"

    def __init__(self, coordinator: PogodaByCoordinator, description: SensorEntityDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        station = coordinator.station
        identity = f"{station[CONF_COUNTRY]}_{station[CONF_STATION]}"
        self._attr_unique_id = f"{identity}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, identity)},
            name=f"Pogoda.by {station['name']}",
            manufacturer="Белгидромет",
            model="Weather observation station",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=f"https://pogoda.by/observation/meteo-observation/{station[CONF_STATION]}",
        )

    @property
    def available(self) -> bool:
        if self.entity_description.key == "station":
            return True
        return super().available and self.coordinator.data.values.get(self.entity_description.key) is not None

    @property
    def native_value(self):
        if self.entity_description.key == "station":
            return self.coordinator.station["name"][:255]
        value = self.coordinator.data.values.get(self.entity_description.key)
        return value[:255] if isinstance(value, str) else value

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        station = self.coordinator.station
        key = self.entity_description.key
        if key == "station":
            return {**station, "observation_url": self._attr_device_info["configuration_url"]}
        data = self.coordinator.data
        attributes: dict[str, Any] = {"station_id": station[CONF_STATION]}
        if key == "pressure":
            attributes["status"] = data.values.get("pressure_trend")
        elif key == "wind_speed":
            attributes["direction"] = data.values.get("wind_direction")
            speed = data.values.get("wind_speed")
            attributes["speed_kmh"] = round(speed * 3.6, 2) if speed is not None else None
        elif key == "condition":
            attributes["description"] = data.values.get("condition")
            attributes["raw_description"] = data.description
        elif key == "observation_time":
            attributes["published"] = data.published
        return attributes
