"""Constants for the Pogoda.by integration."""

DOMAIN = "pogoda_by"
NAME = "Pogoda.by"
VERSION = "0.2.2"
CATALOG_URL = "https://pogoda.by/api/v2/weather-fact/all-cities"
RSS_URL = "https://pogoda.by/rss/weather"
CONF_COUNTRY = "country"
CONF_STATION = "station_id"
CONF_INTERVAL = "update_interval"
DEFAULT_INTERVAL = 60
MIN_INTERVAL = 5
MAX_INTERVAL = 180
CONF_MAX_OBSERVATION_AGE = "max_observation_age"
DEFAULT_MAX_OBSERVATION_AGE = 6
MIN_MAX_OBSERVATION_AGE = 1
MAX_MAX_OBSERVATION_AGE = 168
# Allow a small clock skew, but never confirm a substantially future observation.
FUTURE_TOLERANCE_SECONDS = 300
REQUEST_TIMEOUT = 30
MAX_RESPONSE_BYTES = 4 * 1024 * 1024
