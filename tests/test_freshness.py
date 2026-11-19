"""Controlled-clock tests of production coordinator/sensors/options with HA API doubles.

These tests do not start Home Assistant, use its event loop/state machine, or
validate voluptuous/HA frontend form serialization. RSS parsing is real.
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

COMPONENT = Path(__file__).resolve().parents[1] / "custom_components/pogoda_by"


class UpdateFailed(Exception):
    pass


class CannotConnect(Exception):
    pass


class CoordinatorDouble:
    """Only the base API used by the integration; refresh state is driven by tests."""

    def __class_getitem__(cls, item):
        return cls

    def __init__(self, hass, logger, *, name, config_entry, update_interval):
        self.hass = hass
        self.update_interval = update_interval
        self.data = None
        self.last_update_success = True
        self.listeners = []

    def async_add_listener(self, listener):
        self.listeners.append(listener)
        return lambda: self.listeners.remove(listener)

    def async_update_listeners(self):
        for listener in list(self.listeners):
            listener()


class EntityDouble:
    def __class_getitem__(cls, item):
        return cls

    def __init__(self, coordinator):
        self.coordinator = coordinator

    @property
    def available(self):
        return self.coordinator.last_update_success


@dataclass(frozen=True)
class DescriptionDouble:
    key: str
    translation_key: str
    device_class: str | None = None
    native_unit_of_measurement: str | None = None
    state_class: str | None = None
    entity_category: str | None = None
    icon: str | None = None
    options: list[str] | None = None


class FlowDouble:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()

    def async_show_form(self, **kwargs):
        return {"type": "form", **kwargs}

    def async_create_entry(self, **kwargs):
        return {"type": "create_entry", **kwargs}


class RequiredDouble:
    def __init__(self, key, default):
        self.key = key
        self.default = default


def load_modules():
    names = (
        "homeassistant", "homeassistant.config_entries", "homeassistant.core",
        "homeassistant.helpers", "homeassistant.helpers.event",
        "homeassistant.helpers.update_coordinator", "homeassistant.helpers.device_registry",
        "homeassistant.helpers.entity_platform", "homeassistant.helpers.aiohttp_client",
        "homeassistant.helpers.selector", "homeassistant.util", "homeassistant.util.dt",
        "homeassistant.components", "homeassistant.components.sensor", "homeassistant.const",
        "voluptuous", "_freshness_pogoda", "_freshness_pogoda.api",
    )
    modules = {name: ModuleType(name) for name in names}
    package = modules["_freshness_pogoda"]
    package.__path__ = [str(COMPONENT)]
    package.PogodaByConfigEntry = SimpleNamespace
    ha = modules["homeassistant"]
    ha.config_entries = modules["homeassistant.config_entries"]
    ha.config_entries.ConfigEntry = SimpleNamespace
    ha.config_entries.ConfigFlow = FlowDouble
    ha.config_entries.OptionsFlow = FlowDouble
    core = modules["homeassistant.core"]
    core.HomeAssistant = SimpleNamespace
    core.callback = lambda fn: fn
    coordinator_api = modules["homeassistant.helpers.update_coordinator"]
    coordinator_api.DataUpdateCoordinator = CoordinatorDouble
    coordinator_api.CoordinatorEntity = EntityDouble
    coordinator_api.UpdateFailed = UpdateFailed
    modules["homeassistant.helpers.event"].async_track_point_in_utc_time = Mock()
    modules["homeassistant.util"].dt = modules["homeassistant.util.dt"]
    modules["homeassistant.util.dt"].utcnow = Mock()
    device = modules["homeassistant.helpers.device_registry"]
    device.DeviceInfo = dict
    device.DeviceEntryType = SimpleNamespace(SERVICE="service")
    modules["homeassistant.helpers.entity_platform"].AddEntitiesCallback = object
    modules["homeassistant.helpers.aiohttp_client"].async_get_clientsession = Mock()
    sensor_api = modules["homeassistant.components.sensor"]
    sensor_api.SensorEntity = type("SensorEntity", (), {})
    sensor_api.SensorEntityDescription = DescriptionDouble
    sensor_api.SensorDeviceClass = SimpleNamespace(**{key: key.lower() for key in (
        "TEMPERATURE", "ATMOSPHERIC_PRESSURE", "WIND_SPEED", "TIMESTAMP", "HUMIDITY", "DISTANCE", "ENUM",
    )})
    sensor_api.SensorStateClass = SimpleNamespace(MEASUREMENT="measurement")
    const = modules["homeassistant.const"]
    const.EntityCategory = SimpleNamespace(DIAGNOSTIC="diagnostic")
    const.PERCENTAGE = "%"
    for name, key, value in (
        ("UnitOfLength", "KILOMETERS", "km"), ("UnitOfPressure", "HPA", "hPa"),
        ("UnitOfSpeed", "METERS_PER_SECOND", "m/s"), ("UnitOfTemperature", "CELSIUS", "°C"),
    ):
        setattr(const, name, SimpleNamespace(**{key: value}))
    api = modules["_freshness_pogoda.api"]
    api.CannotConnect = CannotConnect
    api.PogodaByClient = object
    vol = modules["voluptuous"]
    vol.Required = RequiredDouble
    vol.Schema = lambda schema: schema
    vol.All = lambda *validators: validators
    vol.Range = lambda **kwargs: kwargs
    loaded = {}
    with patch.dict(sys.modules, modules):
        for name in ("const", "parser", "coordinator", "sensor", "config_flow"):
            spec = importlib.util.spec_from_file_location(f"_freshness_pogoda.{name}", COMPONENT / f"{name}.py")
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            loaded[name] = module
    return SimpleNamespace(**loaded)


integration = load_modules()
coordinator = integration.coordinator
sensor = integration.sensor
const = integration.const
parser = integration.parser


def observation(date, description="Температура -2°C | Ветер 0 м/с"):
    date_xml = "" if date is None else f"<pubDate>{date}</pubDate>"
    return parser.parse_rss(
        f"<rss><channel><item>{date_xml}<description><![CDATA[{description}]]></description>"
        "</item></channel></rss>"
    )


class Clock:
    def __init__(self):
        self.now = datetime(2026, 11, 19, 12, tzinfo=UTC)
        self.events = []

    def schedule(self, hass, callback, when):
        event = {"callback": callback, "when": when, "active": True}
        self.events.append(event)
        def cancel():
            event["active"] = False
        return cancel

    def advance(self, delta):
        self.now += delta
        for event in list(self.events):
            if event["active"] and event["when"] <= self.now:
                event["active"] = False
                event["callback"](self.now)

    @property
    def active(self):
        return [event for event in self.events if event["active"]]


def run(coroutine):
    # These AsyncMock-backed methods never suspend and need no OS/network loop.
    try:
        coroutine.send(None)
    except StopIteration as result:
        return result.value
    finally:
        coroutine.close()
    raise AssertionError("Test unexpectedly needs an actual event loop")


class FreshnessTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.addCleanup(patch.stopall)
        patch.object(coordinator.dt_util, "utcnow", side_effect=lambda: self.clock.now).start()
        patch.object(coordinator, "async_track_point_in_utc_time", side_effect=self.clock.schedule).start()
        self.unload = []
        self.entry = SimpleNamespace(
            data={"country": "BY", "station_id": "26851", "name": "Минск", "timezone": "Europe/Minsk"},
            options={"update_interval": 17}, async_on_unload=self.unload.append,
        )
        self.client = SimpleNamespace(async_observation=AsyncMock())
        self.hass = SimpleNamespace()
        self.coordinator = coordinator.PogodaByCoordinator(self.hass, self.entry, self.client)
        self.entities = {
            description.key: sensor.PogodaBySensor(self.coordinator, description)
            for description in sensor.SENSORS
        }

    def fetch(self, date, description="Температура -2°C | Ветер 0 м/с"):
        self.client.async_observation.return_value = observation(date, description)
        self.coordinator.data = run(self.coordinator._async_update_data())
        self.coordinator.last_update_success = True
        self.coordinator.async_update_listeners()

    def fail(self, error):
        self.client.async_observation.side_effect = error
        with self.assertRaises(UpdateFailed):
            run(self.coordinator._async_update_data())
        self.coordinator.last_update_success = False
        self.coordinator.async_update_listeners()
        self.client.async_observation.side_effect = None

    def test_old_entry_defaults_preserve_station_interval_and_options(self):
        self.assertEqual(self.coordinator.max_observation_age, timedelta(hours=6))
        self.assertEqual(self.coordinator.update_interval, timedelta(minutes=17))
        self.assertIs(self.coordinator.station, self.entry.data)
        self.assertEqual(self.entry.options, {"update_interval": 17})

    def test_custom_threshold_controls_expiry(self):
        self.entry.options[const.CONF_MAX_OBSERVATION_AGE] = 2
        self.coordinator = coordinator.PogodaByCoordinator(self.hass, self.entry, self.client)
        self.fetch("2026-11-19T09:59:59Z")
        self.assertEqual(self.coordinator.freshness, "stale")

    def test_fresh_real_zero_and_absent_field(self):
        self.fetch("2026-11-19T11:00:00Z")
        self.assertEqual(self.coordinator.freshness, "fresh")
        self.assertTrue(self.entities["temperature"].available)
        self.assertEqual(self.entities["temperature"].native_value, -2)
        self.assertTrue(self.entities["wind_speed"].available)
        self.assertEqual(self.entities["wind_speed"].native_value, 0)
        self.assertFalse(self.entities["pressure"].available)
        self.assertIsNone(self.entities["pressure"].native_value)
        self.assertEqual(self.entities["observation_time"].native_value, datetime(2026, 11, 19, 11, tzinfo=UTC))

    def test_empty_or_absent_weather_text_is_available_and_created(self):
        base = "Температура +10.7°C | Давление 983.9 гПа, падает | Ветер 1.8 м/с, Западный"
        for description in (base + " | Погода: ", base):
            with self.subTest(description=description):
                self.fetch("2026-11-19T11:00:00Z", description)
                # The standalone parser still leaves an absent field absent.
                self.assertNotIn("condition", self.coordinator.data.values)
                self.entry.runtime_data = self.coordinator
                created = []
                run(sensor.async_setup_entry(self.hass, self.entry, created.extend))
                condition = next(e for e in created if e.entity_description.key == "condition")
                self.assertTrue(condition.available)
                self.assertEqual(condition.native_value, "")
                self.assertEqual(condition.extra_state_attributes["description"], "")
                self.assertEqual(condition._attr_unique_id, "BY_26851_condition")
                self.assertEqual(self.entities["temperature"].native_value, 10.7)
                self.assertTrue(self.entities["temperature"].available)

    def test_weather_text_can_appear_and_disappear_without_duplicate_entities(self):
        self.fetch("2026-11-19T11:00:00Z")
        self.entry.runtime_data = self.coordinator
        created = []
        run(sensor.async_setup_entry(self.hass, self.entry, created.extend))
        condition = next(e for e in created if e.entity_description.key == "condition")
        for description, expected in (
            ("Температура 1°C | Погода: Дождь, слабый", "Дождь, слабый"),
            ("Температура 1°C | Погода: ", ""),
            ("Температура 1°C", ""),
            ("Температура 1°C | Погода: Ясно", "Ясно"),
        ):
            with self.subTest(description=description):
                self.fetch("2026-11-19T11:00:00Z", description)
                self.assertTrue(condition.available)
                self.assertEqual(condition.native_value, expected)
                self.assertEqual(condition.extra_state_attributes["description"], expected)
        self.assertEqual(sum(e.entity_description.key == "condition" for e in created), 1)

    def test_empty_weather_text_still_requires_fresh_successful_observation(self):
        condition = self.entities["condition"]
        for date in (None, "bad", "2001-01-01T00:00:00Z", "2026-11-19T12:06:00Z"):
            with self.subTest(date=date):
                self.fetch(date)
                self.assertEqual(condition.native_value, "")
                self.assertFalse(condition.available)
        self.fetch("2026-11-19T11:00:00Z")
        self.assertTrue(condition.available)
        self.fail(CannotConnect("offline"))
        self.assertFalse(condition.available)
        self.assertEqual(condition.native_value, "")
        self.fetch("2026-11-19T11:00:00Z")
        self.assertTrue(condition.available)
        self.clock.advance(timedelta(hours=5, microseconds=1))
        self.assertFalse(condition.available)

    def test_ancient_rss_is_successful_but_unavailable(self):
        self.fetch("Mon, 01 Jan 2001 00:00:00 +0000")
        self.assertTrue(self.coordinator.last_update_success)
        self.assertEqual(self.coordinator.freshness, "stale")
        self.assertFalse(self.entities["temperature"].available)
        self.assertEqual(self.entities["temperature"].native_value, -2)
        self.assertEqual(self.entities["last_successful_fetch"].native_value, self.clock.now)
        self.assertEqual(self.clock.active, [])

    def test_cross_threshold_without_poll_notifies_entities(self):
        self.fetch("2026-11-19T06:00:01Z")
        states = []
        self.coordinator.async_add_listener(lambda: states.append((
            self.entities["temperature"].available, self.entities["freshness"].native_value,
        )))
        self.clock.advance(timedelta(seconds=1))
        self.assertEqual(self.coordinator.freshness, "fresh")  # exactly six hours
        self.assertEqual(states, [])
        self.clock.advance(timedelta(microseconds=1))
        self.assertEqual(states, [(False, "stale")])
        self.assertTrue(self.coordinator.last_update_success)
        self.assertEqual(self.client.async_observation.await_count, 1)

    def test_repeated_identical_rss_does_not_extend_deadline(self):
        date = "2026-11-19T07:00:00Z"
        self.fetch(date)
        deadline = self.clock.active[0]["when"]
        self.clock.advance(timedelta(minutes=30))
        self.fetch(date)
        self.assertEqual(len(self.clock.active), 1)
        self.assertEqual(self.clock.active[0]["when"], deadline)
        self.clock.advance(timedelta(minutes=30, microseconds=1))
        self.assertEqual(self.coordinator.freshness, "stale")
        self.assertEqual(self.client.async_observation.await_count, 2)

    def test_repeated_old_rss_updates_reception_not_observation(self):
        self.fetch("2001-01-01T00:00:00Z")
        observed = self.entities["observation_time"].native_value
        received = self.coordinator.last_successful_fetch
        self.clock.advance(timedelta(minutes=17))
        self.fetch("2001-01-01T00:00:00Z")
        self.assertGreater(self.coordinator.last_successful_fetch, received)
        self.assertEqual(self.entities["observation_time"].native_value, observed)
        self.assertEqual(self.coordinator.freshness, "stale")

    def test_missing_invalid_naive_and_overflow_dates_are_unknown(self):
        for date in (None, "bad", "2026-02-30T00:00:00Z", "2026-11-19T11:00:00",
                     "0001-01-01T00:00:00+03:00", "9999-12-31T23:59:59-03:00"):
            with self.subTest(date=date):
                self.fetch(date)
                self.assertEqual(self.coordinator.freshness, "unknown")
                self.assertFalse(self.entities["temperature"].available)
                self.assertTrue(self.entities["observation_time"].available)
                self.assertIsNone(self.entities["observation_time"].native_value)
                self.assertEqual(self.coordinator.last_successful_fetch, self.clock.now)
                self.assertEqual(self.clock.active, [])

    def test_future_beyond_tolerance_is_unknown_until_new_response(self):
        self.fetch("2026-11-19T12:05:01Z")
        self.assertEqual(self.coordinator.freshness, "unknown")
        self.assertFalse(self.entities["temperature"].available)
        self.assertIsNotNone(self.entities["observation_time"].native_value)
        self.assertEqual(self.clock.active, [])
        self.clock.advance(timedelta(minutes=6))
        self.assertEqual(self.coordinator.freshness, "unknown")
        self.fetch("2026-11-19T12:05:01Z")
        self.assertEqual(self.coordinator.freshness, "fresh")

    def test_small_future_clock_skew_is_tolerated(self):
        self.fetch("2026-11-19T12:05:00Z")
        self.assertEqual(self.coordinator.freshness, "fresh")
        self.assertEqual(self.clock.active[0]["when"], datetime(2026, 11, 19, 18, 5, 0, 1, tzinfo=UTC))

    def test_extreme_future_date_does_not_overflow_coordinator(self):
        self.fetch("9999-12-31T23:59:59Z")
        self.assertEqual(self.coordinator.freshness, "unknown")
        self.assertEqual(self.clock.active, [])

    def test_timezone_offsets_produce_identical_age(self):
        for date in ("2026-11-19T11:00:00Z", "2026-11-19T14:00:00+03:00", "2026-11-19T06:00:00-05:00"):
            with self.subTest(date=date):
                self.fetch(date)
                self.assertEqual(self.coordinator.freshness, "fresh")
                self.assertEqual(self.entities["observation_time"].native_value.hour, 11)
                self.assertEqual(self.entities["observation_time"].native_value.utcoffset(), timedelta(0))

    def test_failure_retains_diagnostics_and_timer_then_recovery(self):
        self.fetch("2026-11-19T06:00:01Z")
        received = self.coordinator.last_successful_fetch
        observed = self.entities["observation_time"].native_value
        self.fail(CannotConnect("offline"))
        self.assertFalse(self.entities["temperature"].available)
        self.assertEqual(self.entities["freshness"].native_value, "fresh")
        self.assertFalse(self.entities["freshness"].extra_state_attributes["last_request_success"])
        self.assertEqual(self.coordinator.last_successful_fetch, received)
        self.assertEqual(self.entities["observation_time"].native_value, observed)
        for key in ("station", "observation_time", "freshness", "last_successful_fetch"):
            self.assertTrue(self.entities[key].available)
        listener = Mock()
        self.coordinator.async_add_listener(listener)
        self.clock.advance(timedelta(seconds=2))
        listener.assert_called_once()
        self.assertEqual(self.coordinator.freshness, "stale")
        self.assertFalse(self.coordinator.last_update_success)
        self.fetch("2026-11-19T12:00:00Z")
        self.assertTrue(self.entities["temperature"].available)
        self.assertGreater(self.coordinator.last_successful_fetch, received)
        self.assertTrue(self.entities["freshness"].extra_state_attributes["last_request_success"])

    def test_failure_then_stale_recovery_stays_unavailable(self):
        self.fetch("2026-11-19T11:00:00Z")
        self.fail(CannotConnect("offline"))
        self.clock.advance(timedelta(hours=1))
        self.fetch("2001-01-01T00:00:00Z")
        self.assertTrue(self.coordinator.last_update_success)
        self.assertEqual(self.coordinator.freshness, "stale")
        self.assertFalse(self.entities["temperature"].available)
        self.assertEqual(self.entities["last_successful_fetch"].native_value, self.clock.now)

    def test_failed_first_fetch_does_not_invent_reception(self):
        self.fail(CannotConnect("offline"))
        self.assertIsNone(self.coordinator.last_successful_fetch)
        self.assertEqual(self.coordinator.freshness, "unknown")
        self.assertIsNone(self.entities["last_successful_fetch"].native_value)
        self.assertFalse(self.entities["temperature"].available)

    def test_invalid_rss_failure_does_not_update_reception(self):
        self.fetch("2026-11-19T11:00:00Z")
        received = self.coordinator.last_successful_fetch
        self.clock.advance(timedelta(minutes=10))
        self.fail(parser.InvalidData("invalid RSS"))
        self.assertEqual(self.coordinator.last_successful_fetch, received)
        self.assertFalse(self.entities["temperature"].available)

    def test_new_undated_response_replaces_old_date_and_cancels_timer(self):
        self.fetch("2026-11-19T11:00:00Z")
        self.assertEqual(len(self.clock.active), 1)
        self.fetch(None)
        self.assertEqual(self.clock.active, [])
        self.assertEqual(self.coordinator.freshness, "unknown")
        self.assertIsNone(self.entities["observation_time"].native_value)

    def test_unload_cancels_timer(self):
        self.fetch("2026-11-19T11:00:00Z")
        for callback in self.unload:
            callback()
        self.assertEqual(self.clock.active, [])
        self.assertIsNone(self.coordinator._cancel_freshness_timer)

    def test_before_first_response_has_no_invented_diagnostics(self):
        self.assertEqual(self.entities["freshness"].native_value, "unknown")
        self.assertIsNone(self.entities["last_successful_fetch"].native_value)
        self.assertIsNone(self.entities["observation_time"].native_value)
        self.assertFalse(self.entities["temperature"].available)
        self.assertEqual(self.entities["condition"].extra_state_attributes, {"station_id": "26851"})

    def test_existing_unique_ids_and_device_identity_are_unchanged(self):
        old_keys = {"temperature", "pressure", "pressure_trend", "wind_speed", "wind_direction", "condition",
                    "observation_time", "station", "humidity", "wind_gust", "visibility"}
        self.assertEqual(set(self.entities), old_keys | {"freshness", "last_successful_fetch"})
        for key, entity in self.entities.items():
            self.assertEqual(entity._attr_unique_id, f"BY_26851_{key}")
            self.assertEqual(entity._attr_device_info["identifiers"], {("pogoda_by", "BY_26851")})

    def test_diagnostics_created_for_undated_rss_and_optional_fields_added_later(self):
        self.fetch(None)
        self.entry.runtime_data = self.coordinator
        created = []
        run(sensor.async_setup_entry(self.hass, self.entry, created.extend))
        keys = [entity.entity_description.key for entity in created]
        for key in ("station", "observation_time", "freshness", "last_successful_fetch"):
            self.assertIn(key, keys)
        self.assertNotIn("humidity", keys)
        self.coordinator.data.values["humidity"] = 70
        self.coordinator.async_update_listeners()
        self.coordinator.async_update_listeners()
        self.assertEqual([e.entity_description.key for e in created].count("humidity"), 1)
        self.assertEqual(len(created), len({e._attr_unique_id for e in created}))
        self.assertEqual(self.client.async_observation.await_count, 1)


class OptionsTests(unittest.TestCase):
    def setUp(self):
        self.flow = integration.config_flow.PogodaByOptionsFlow()
        self.entry = SimpleNamespace(options={"update_interval": 17, "other_option": "retained"})
        self.flow.config_entry = self.entry

    def test_old_entry_displays_six_hours_and_existing_interval(self):
        result = run(self.flow.async_step_init())
        defaults = {marker.key: marker.default for marker in result["data_schema"]}
        self.assertEqual(defaults, {"update_interval": 17, "max_observation_age": 6})
        self.assertEqual(self.entry.options, {"update_interval": 17, "other_option": "retained"})

    def test_valid_limits_saved_without_losing_other_options(self):
        for hours in (1, 6, 168):
            with self.subTest(hours=hours):
                result = run(self.flow.async_step_init({"update_interval": 17, "max_observation_age": hours}))
                self.assertEqual(result["type"], "create_entry")
                self.assertEqual(result["data"], {"update_interval": 17, "max_observation_age": hours, "other_option": "retained"})

    def test_bad_threshold_is_rejected_by_flow(self):
        for hours in (None, 0, -1, 169, 6.5, True, "six", "6", float("nan"), float("inf")):
            with self.subTest(hours=hours):
                result = run(self.flow.async_step_init({"update_interval": 17, "max_observation_age": hours}))
                self.assertEqual(result["type"], "form")
                self.assertEqual(result["errors"], {"max_observation_age": "invalid_max_observation_age"})

    def test_interval_limits_are_still_enforced(self):
        for minutes in (0, 4, 181, True, 6.5):
            result = run(self.flow.async_step_init({"update_interval": minutes, "max_observation_age": 6}))
            self.assertEqual(result["errors"], {"update_interval": "invalid_interval"})


if __name__ == "__main__":
    unittest.main()
