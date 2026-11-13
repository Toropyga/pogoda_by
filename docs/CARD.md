# Pogoda.by Card — 0.2.0

[Полная инструкция на русском](CARD.ru.md)

A dependency-free custom dashboard card for the Pogoda.by integration. Displays observed weather, sensor units, wind, pressure and observation time; optional humidity, gusts and visibility only appear when available. Includes an optional Home Assistant temperature history graph, a station picker, five interface languages (EN/RU/BE/PL/DE), theme support and compact mode.

## Install

Starting with **integration version 0.2.0**, the card is bundled in `custom_components/pogoda_by/frontend/pogoda-by-card.js` and installed/updated with the integration.

1. Install or update Pogoda.by and restart Home Assistant. For a manual install, copy the entire `custom_components/pogoda_by` folder to `/config/custom_components/`.
2. Add a station if this is your first installation. Existing station entries are retained on updates.
3. Refresh your browser; add **Pogoda.by Card** from the dashboard card picker and select your station.

The integration automatically serves and registers `/pogoda_by/pogoda-by-card.js?v=0.2.0` as a module when resources are managed in storage (the normal UI mode). No separate copy to `www` or second HACS repository is needed. Registration runs once for the whole integration, before station data is fetched. Updates change the resource URL's version without creating duplicates. Adding the card to a dashboard is still a user action.

Existing manual resource records at `/local/pogoda-by-card.js` (including query strings) are migrated to the bundled URL. Duplicate records at these two known local paths are consolidated; unrelated resources and the old file on disk are retained.

### YAML-managed resources

For `lovelace.resource_mode: yaml`, add the following to your existing configuration; the integration does not modify user YAML:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /pogoda_by/pogoda-by-card.js?v=0.2.0
      type: module
```

Before Home Assistant 2026.2, retain the existing `mode: yaml` instead of `resource_mode`. Do not switch a dashboard's mode solely for this card. Reload resources or restart HA, then refresh the browser. Update the URL version manually after upgrades. YAML dashboard definitions can still use storage-managed resources; it is the resource collection's mode that matters.

If automatic registration fails, check the integration log and register the same URL manually as a JavaScript module in Settings → Dashboards → Resources.

```yaml
type: custom:pogoda-by-card
station: BY_26850 # Example only; select your configured station in the editor.
show_graph: true
show_details: true
show_observation: true
hours_to_show: 24
stale_after: 180
compact: false
language: auto
```

`station` uses `COUNTRY_STATION_ID`. Sensor discovery uses the entity registry's stable unique IDs, so renamed entity IDs are supported. `name` overrides the title. `hours_to_show` accepts 1–168; `stale_after` accepts 5–10080 minutes. `language`: `auto`, `en`, `ru`, `be`, `pl`, `de`. Existing Lovelace visibility/grid options are retained by the editor. Provider descriptions are not translated.

If registry access is unavailable, an optional `entities` mapping can explicitly set any of `temperature`, `pressure`, `pressure_trend`, `wind_speed`, `wind_direction`, `condition`, `observation_time`, `station`, `humidity`, `wind_gust`, `visibility` to real sensor entity IDs. With explicit mappings, `station` is optional.

Freshness uses the actual observation timestamp. Missing or invalid timestamps are never marked fresh. Units come directly from Home Assistant sensors. No forecast or missing measurements are synthesized. The history graph uses the built-in `history-graph` through `loadCardHelpers` and requires Recorder/History with recorded temperature data. The card does not poll the weather service.

For updates, replace/update the whole integration, restart Home Assistant and refresh the browser. Storage-managed resource URLs update automatically; update the version manually for YAML-managed resources. Run `node --test tests/test_card.cjs` for logic tests in a minimal simulated DOM (Node.js 22+). For local browser tests, run `node tools/test_card.cjs` (Node.js 22+, Chrome; override its path with `CHROME_BIN`). A local demo is in `tools/card-preview.html`; serve the repository over HTTP. Its data and graph are illustrative. Tests with a simulated host do not substitute for verification in a running Home Assistant instance.
