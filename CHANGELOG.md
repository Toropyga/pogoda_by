# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Inclusion in the community Marketplace / HACS catalogue (separate from Home Assistant Core)
- Enhanced debugging logging for troubleshooting

---

## [0.2.0] - 2026-11-13

### Added
- Bundled Pogoda.by Card 0.2.0: visual station selection, renamed-entity discovery, current observations, optional temperature history, freshness indicators, theme support, compact layout and five interface languages.
- Automatic static-file and Lovelace resource registration during component setup; the card installs and updates with the integration.
- Migration from the previous `/local/pogoda-by-card.js` resource, versioned URLs and consolidation of known duplicate local card resources. Unrelated resources are preserved, including when the collection has not been loaded yet.
- YAML resource instructions, a demonstration host, frontend registration tests and card logic checks in CI. Registration failures are logged without failing weather sensor setup.

### Changed
- The card source now lives in `custom_components/pogoda_by/frontend/`, so integration installation includes it.
- All five READMEs document the combined installation, card configuration, YAML resource mode, upgrades and current validation status.
- Integration metadata, frontend version and resource URL examples are aligned at 0.2.0.

### Fixed
- Removed an incorrect HACS Default badge from the Belarusian README; the project is installed as a custom repository.
- Repaired broken README links, a duplicate release heading and corrupted punctuation in this changelog.

### Validation
- 50 Python tests and 18 card logic tests pass locally; syntax and whitespace checks pass.
- A running Home Assistant instance, the real Recorder history graph and visual rendering still require verification.

---

## [0.1.4] - 2026-11-13

### Added
- **German interface translation** — Added `de.json` translation covering country and station selection, error messages, update settings and sensor names
- **German README** — Added `docs/README.de.md`; all README files now link to the German version
- **README organization** — The English README is in the repository root; Russian, Polish, Belarusian and German versions are in `docs/`

### Fixed
- **Spelling and grammar in translated READMEs** — Corrected a gender-agreement error and a Russian-calque word in the Belarusian README, a comma splice in the German README, and a missing article plus an omitted German mention in the English README

### Technical Details
- **Tests**: All 36 unit tests pass; the translation-key consistency check now covers five languages (`en`, `ru`, `be`, `pl`, `de`) instead of four

---

## [0.1.3] — 2026-11-12

### Fixed
- **UTF-8 BOM in manifest.json** — Removed byte order mark that was causing JSON parsing errors in some environments
- **Python 3.11 compatibility** — Replaced PEP 695 type alias syntax (`type X = Y`) with `TypeAlias` from `typing` module for compatibility with Python 3.11
- **JSON parsing in tests** — Updated test_bundle.py to use `utf-8-sig` encoding to handle BOM-prefixed JSON files

### Technical Details
- **Compatibility**: Verified working with Python 3.11 and 3.12
- **Tests**: All 36 unit tests pass with GitHub Actions CI/CD
- **JSON handling**: Improved robustness for manifest and configuration files

---

## [0.1.2] — 2026-11-12

### Added
- **GitHub Actions CI/CD workflow** — Automated testing on Python 3.11 and 3.12 on every commit and pull request
- **MIT License** — Proper open-source licensing for distribution
- **Enhanced README organization** — Installation and configuration buttons moved to appropriate sections in all 4 languages

### Changed
- **Documentation structure** — Unified badge placement across Russian, English, Polish, and Belarusian README files

### Technical Details
- **CI/CD**: Tests run automatically on every push and PR
- **License**: MIT (see [LICENSE](LICENSE))
- **Python versions tested**: 3.11, 3.12

### Testing
- All 36 existing tests continue to pass
- GitHub Actions validates syntax and runs full test suite

---

## [0.1.1] — 2026-11-12

### Added
- **Marketplace integration support** — Full support for Home Assistant 2026.11+ built-in Marketplace and HACS for earlier versions
- **Multi-language interface** — Translations for Russian (`ru`), English (`en`), Polish (`pl`), and Belarusian (`be`)
  - Country and station selection translated
  - Error messages translated
  - Update settings translated
  - Sensor names translated
- **Brand icon** — Pogoda.by icon with transparent background (256×256 and 512×512 pixels)
- **README files in multiple languages** — Complete setup and troubleshooting guides:
  - Russian: [README.ru.md](docs/README.ru.md)
  - English: [README.md](README.md)
  - Polish: [README.pl.md](docs/README.pl.md)
  - Belarusian: [README.be.md](docs/README.be.md)
- **HACS configuration** — Ready for Marketplace/HACS installation with `hacs.json`
- **License** — MIT license for open-source distribution
- **GitHub Actions workflow** — Automated testing and syntax checking on every commit
- **Publication guide** — Step-by-step instructions in `HACS.md` for publishing to Marketplace/HACS

### Changed
- **Default update interval** — Increased from 10 minutes to **1 hour (60 minutes)**
  - User-configured intervals are preserved during updates
  - Configurable from 5 to 180 minutes
- **Documentation structure** — Reorganized README with separate sections for Marketplace and HACS

### Technical Details
- **Sensors**: Temperature, atmospheric pressure, pressure trend, wind speed, wind direction, weather description, observation time, station metadata, humidity (optional), wind gusts (optional), visibility (optional)
- **Device integration**: One device per weather station
- **Data polling**: Coordinated via `DataUpdateCoordinator`, one RSS request per update cycle
- **API compatibility**: No API key required, uses public Pogoda.by RSS and JSON API
- **Dependencies**: Zero production dependencies (uses only Python standard library and Home Assistant built-ins)

### Testing
- **36 automated tests** — 100% pass rate
  - 25 tests for JSON catalogue and RSS parsing
  - 7 tests for HTTP error handling
  - 4 tests for bundle consistency
- **Syntax validation** — All Python files compile successfully
- **Localization checks** — Translation keys synchronized across all 4 languages

### Known Limitations
- Full installation validation in a running Home Assistant instance has not been performed
- Forecast data not provided (observations only)
- RSS text values retain the provider's original language
- Local integration icons require Home Assistant 2026.3 or later for display

### Documentation
- Complete setup guide for Marketplace and HACS
- Manual installation instructions
- Sensor reference table with units and descriptions
- Troubleshooting section with common issues
- Language availability documentation
- Live data provider smoke-test script (`tools/check_live.py`)

---

## Upgrade to 0.2.0

1. Update the whole integration, including `frontend`, `brand` and `translations`, and restart Home Assistant. Existing station entries are retained.
2. Refresh the browser. Add **Pogoda.by Card** to the desired dashboard and select a station.
3. With UI-managed resources, the card module registers automatically and a previous manual `/local/pogoda-by-card.js` record is migrated. Other resources are preserved.
4. With YAML-managed resources, add `/pogoda_by/pogoda-by-card.js?v=0.2.0` with `type: module`, reload resources and refresh the browser. The integration does not edit user YAML.

See the [card guide](docs/CARD.md) or [Russian guide](docs/CARD.ru.md). The card displays observations; temperature history requires Recorder/History. No forecast is provided.
