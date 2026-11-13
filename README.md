# Pogoda.by for Home Assistant — 0.2.1

[Русский](docs/README.ru.md) | [English](README.md) | [Polski](docs/README.pl.md) | [Беларуская](docs/README.be.md) | [Deutsch](docs/README.de.md)

A custom integration for Home Assistant. Retrieves observed weather from Belhydromet via RSS and the list of countries and stations via a JSON API. No API key is required. Weather forecasts are not provided.

![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)
![Version](https://img.shields.io/badge/version-v0.2.1-blue.svg)

> ⚠️ **Important note:** The integration provides complete information for weather stations **in Belarus**. For stations in other countries, the information is often **unavailable or incomplete**, as the Pogoda.by service is primarily focused on Belhydromet data (Belarus). If you have selected a station from another country and the sensors show an error or become unavailable, this is due to data unavailability from the Pogoda.by service.

## Installation with Marketplace / HACS

The integration supports installation through Marketplace / HACS from the `Toropyga/pogoda_by` repository.

[![Install via HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Toropyga&repository=pogoda_by&category=Integration)

### Home Assistant 2026.11 and later — Marketplace

Starting with **Home Assistant 2026.11**, HACS is built into Home Assistant as the **Marketplace**. No separate HACS installation is needed. Administrators can access the Marketplace under Settings. Pogoda.by is not yet in the default catalogue, so add its repository from a link.

1. Open **Settings → Marketplace**.
2. Select **Add from link**.
3. Enter `https://github.com/Toropyga/pogoda_by` and select **Add**.
4. Connect GitHub if prompted: custom repositories require a connection. If the content type is not detected automatically, select **Integration**.
5. Open **Pogoda.by** and select **Install**.
6. Select a country and station in the configuration flow. If the Marketplace requests a restart, restart first, then follow the configuration section below.

A first installation may open configuration immediately without a restart. When updating an existing installation, follow the Marketplace notification about restarting.

### Home Assistant 2026.10 and earlier — HACS

On earlier versions, [HACS](https://www.hacs.xyz/) must already be installed and configured. Add the integration as a custom repository:

1. Open **HACS** in Home Assistant.
2. Select **⋮ → Custom repositories**.
3. Enter `https://github.com/Toropyga/pogoda_by`.
4. Select **Integration** as the type and click **Add**.
5. Find **Pogoda.by**, open it and click **Download**.
6. Confirm the suggested version. If no releases have been published, HACS uses the repository's default branch.
7. Restart Home Assistant and follow the configuration steps below.

Marketplace and HACS place the files in `/config/custom_components/pogoda_by/`, including `frontend`, `brand` and `translations`. Future published versions can be downloaded through the corresponding interface.

If the integration was installed manually, add the same repository to Marketplace or HACS and install it over the existing files. There is no need to delete the Pogoda.by entry from Devices & services when changing the installation method.

## Manual installation

1. Copy the `custom_components/pogoda_by` folder from this project to your Home Assistant configuration directory. The resulting path must be `/config/custom_components/pogoda_by/manifest.json`.
2. Restart Home Assistant.
3. Follow the configuration steps below.

## Configuration after installation

[![Add integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=pogoda_by)

1. Open **Settings → Devices & services → Add integration → Pogoda.by**.
2. Select a country from the catalogue, then a station from that country's list. The label includes the actual station ID, rather than its position in the JSON data.
3. Wait for the first successful RSS response. If the station does not publish supported weather data, the form will report this and let you choose another station.

To use multiple stations, add the integration more than once. Adding the same station twice is blocked. To change stations, add a new entry and remove the old one when it is no longer needed.

This is a preliminary version. Source code: https://github.com/Toropyga/pogoda_by. For manual installation, download the repository using **Code → Download ZIP** and extract it. Only the nested `pogoda_by` folder belongs in `custom_components`. A separate GitHub Release is not required for Marketplace / HACS installation. Publication preparation is described in [HACS.md](docs/HACS.md) (in Russian).

## Interface languages

**Belarusian (`be`), Polish (`pl`), Russian (`ru`), English (`en`) and German (`de`)** are supported. Translations cover country and station selection, error messages, update settings and sensor names.

The language follows the Home Assistant interface language selected in the user's profile. No separate language selector is needed in the integration. User-defined entity names are not overwritten.

Station names and text values received from Pogoda.by are preserved as provided. For example, weather descriptions, pressure trends and wind directions from the Russian-language RSS feed are not translated automatically; numeric readings are the same in every language.

## Integration icon

The integration includes a **Pogoda.by** icon with a transparent background:

- `custom_components/pogoda_by/brand/icon.png` — 256×256 pixels;
- `custom_components/pogoda_by/brand/icon@2x.png` — 512×512 pixels.

Home Assistant **2026.3 and later** automatically uses images from the `brand` folder. No additional `manifest.json` settings are needed. When updating an installed integration, copy the entire `pogoda_by` folder, restart Home Assistant and refresh your browser. Earlier Home Assistant versions do not support local integration images this way.

The source image is saved as `assets/pogoda-by-source.png`. To regenerate the required sizes on Windows, run `./tools/build_brand.ps1` from the project directory.

## Dashboard card

**Pogoda.by Card 0.2.1** is installed and updated together with the integration. Copy the entire `custom_components/pogoda_by` directory when installing manually, including `frontend`, `brand` and `translations`. A second dashboard repository or a separate copy to `/config/www` is not needed.

After installing or updating, restart Home Assistant and refresh the browser. In the dashboard editor, select **Add card → Pogoda.by Card**, then choose a configured station. Adding the card to a particular dashboard remains a user action; registering its JavaScript resource is automatic in the normal UI-managed resource mode.

The card displays temperature, current conditions, wind, pressure and the observation timestamp. It marks old observations, supports compact mode, light/dark themes and five interface languages. Humidity, gusts and visibility appear only when available. Clicking a reading opens the entity details. The optional temperature graph uses Home Assistant Recorder/History; no forecast is generated.

Example configuration — replace `BY_26850` with your station, or select it in the visual editor:

```yaml
type: custom:pogoda-by-card
station: BY_26850
show_details: true
show_graph: true
hours_to_show: 24
stale_after: 180
compact: false
language: auto
```

### Full and compact views

In the visual editor, use **Card view → Full view / Compact view**. YAML uses the existing boolean `compact`: `false` selects the full view (default), `true` selects the compact view.

Full view includes detailed readings and an optional temperature graph. Compact view uses a separate horizontal header with the station, conditions and temperature, plus a short wind/pressure row, freshness status and observation time. The graph and optional humidity/gust/visibility readings are hidden in compact view, even if `show_graph: true`; graph settings are retained when returning to full view.

```yaml
type: custom:pogoda-by-card
station: BY_26850
compact: true
```

### YAML-managed resources

With **YAML-managed resources** (`lovelace.resource_mode: yaml`), add `/pogoda_by/pogoda-by-card.js?v=0.2.1` with `type: module` to the existing resource list, then reload resources and refresh the browser. A YAML dashboard can still use UI-managed resources; it is the resource mode that determines whether registration is automatic.

Add this to `configuration.yaml`, merging it into the existing `lovelace` and `resources` sections and keeping your other resources:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /pogoda_by/pogoda-by-card.js?v=0.2.1
      type: module
```

Restart Home Assistant after upgrading the integration. After changing YAML resources, run `lovelace.reload_resources` or restart Home Assistant. Refresh the browser with **Ctrl+F5** and reopen **Add card**.

To check the resource, open `/pogoda_by/pogoda-by-card.js?v=0.2.1` under your Home Assistant address. It should return JavaScript. If it returns **404**, check that `/config/custom_components/pogoda_by/frontend/pogoda-by-card.js` exists and that the integration has started.

Updates preserve configured stations and update the card resource URL. An existing manual `/local/pogoda-by-card.js` resource is migrated automatically in storage mode; duplicate entries at the known local card paths are consolidated. Renamed sensor entity IDs are supported.

See the [card guide](docs/CARD.md), [Russian guide](docs/CARD.ru.md) and [changelog](CHANGELOG.md).

## Sensors

A sensor is created when its field first appears in the RSS feed. If a field appears later, no restart is needed. If a previously available field disappears, the sensor becomes unavailable; missing readings are not replaced with zero.

| Field | Unit / type | Additional information |
| --- | --- | --- |
| Temperature | °C | Supports negative values and decimal points or commas |
| Atmospheric pressure | hPa | `status` attribute: trend from the RSS feed |
| Pressure trend | Text | For example, “falling” |
| Wind speed | m/s | `direction` and `speed_kmh`; units can be changed in Home Assistant |
| Wind direction | Text | Calm conditions are not reported as a northerly wind |
| Weather | Text | Full description and the original text in attributes |
| Observation time | Timestamp | `pubDate` converted to UTC; the interface displays local time |
| Weather station | Diagnostic text | ID, country, name, coordinates, time zone, ICAO and link |
| Humidity | % | Only if the RSS feed explicitly contains this field |
| Wind gust | m/s | Only if the RSS feed explicitly contains this field |
| Visibility | km | Only if the RSS feed explicitly contains this field in kilometres |

The parser supports humidity, wind gusts and visibility as optional fields, but their availability in the current service has not been confirmed. The integration does not derive them from other readings.

Each station is represented by a separate device. Entities have stable unique_id values based on the country, station ID and measurement type. Home Assistant assigns entity_id values.

The default update interval is **1 hour (60 minutes)**. Select **Configure** on the integration entry to choose an interval from 5 to 180 minutes. Each cycle uses one RSS request for all sensors at a station. The catalogue is loaded during configuration; the chosen station's metadata is stored in the entry and does not need to be downloaded again when Home Assistant starts.

After an update, the default applies to entries without an explicitly saved interval. If an interval was saved using **Configure**, it is retained; set it to **60** manually for hourly updates.

If an HTTP error, timeout or invalid RSS response occurs, weather sensors become unavailable. Home Assistant retries updates automatically. The diagnostic station sensor stores metadata locally and remains available. A successful response with an old observation date is not treated as a network error: check the observation time. The integration does not guarantee that the station itself publishes new measurements every hour.

No forecast `weather` entity is created. Display observations with Pogoda.by Card or standard entity cards, tiles and sensor graphs. Numeric readings have device_class, state_class and standard Home Assistant units.

## Validation

Offline JSON/RSS parsing tests use the Python standard library:

```powershell
python -m unittest discover -s tests -v
node --check custom_components/pogoda_by/frontend/pogoda-by-card.js
node --test tests/test_card.cjs
```

Check live responses from the website without installing Home Assistant:

```powershell
python tools/check_live.py --country BY --station 26851
python tools/check_live.py --country PL --station 12372
```

The script only reads public data. It does not modify the Home Assistant configuration. To diagnose integration messages, you can temporarily enable:

```yaml
logger:
  logs:
    custom_components.pogoda_by: debug
```

## Validation status of this build

Version 0.2.1 passes **50 Python tests and 26 card logic tests** locally, plus syntax, translation-key consistency and whitespace checks. The card tests use a minimal DOM host and the registration tests use Home Assistant API doubles; they do not prove compatibility with a running Home Assistant frontend.

Live API/RSS responses, actual resource registration, the real Recorder graph and visual rendering on desktop/mobile still need verification. Details: [validation](VALIDATION.md) (in Russian). The target minimum remains Home Assistant 2025.1; runtime compatibility has not yet been confirmed.

## Sources

- Marketplace: https://www.home-assistant.io/integrations/marketplace/
- Moving from HACS: https://contributors.home-assistant.io/marketplace/how-it-works/
- Catalogue: https://pogoda.by/api/v2/weather-fact/all-cities
- RSS: https://pogoda.by/rss/weather?station=26851
- Home Assistant documentation: https://contributors.home-assistant.io/core/integrations/config-entries/
- Data fetching: https://contributors.home-assistant.io/core/integrations/fetching-data/

Data is provided by Belhydromet. This project is not an official Belhydromet integration.
