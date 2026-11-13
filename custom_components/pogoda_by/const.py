"""Constants for the Pogoda.by integration."""

DOMAIN = "pogoda_by"
NAME = "Pogoda.by"
VERSION = "0.2.1"
CATALOG_URL = "https://pogoda.by/api/v2/weather-fact/all-cities"
RSS_URL = "https://pogoda.by/rss/weather"
CONF_COUNTRY = "country"
CONF_STATION = "station_id"
CONF_INTERVAL = "update_interval"
DEFAULT_INTERVAL = 60
MIN_INTERVAL = 5
MAX_INTERVAL = 180
REQUEST_TIMEOUT = 30
MAX_RESPONSE_BYTES = 4 * 1024 * 1024
