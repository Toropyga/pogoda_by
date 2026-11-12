# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Integration into the main Home Assistant catalogue (requires HACS approval)
- Enhanced debugging logging for troubleshooting
- Improved user interface for update interval selection
- Support for custom station metadata caching

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

## [0.1.1] вЂ” 2026-11-12

### Added
- **Marketplace integration support** вЂ” Full support for Home Assistant 2026.11+ built-in Marketplace and HACS for earlier versions
- **Multi-language interface** вЂ” Translations for Russian (`ru`), English (`en`), Polish (`pl`), and Belarusian (`be`)
  - Country and station selection translated
  - Error messages translated
  - Update settings translated
  - Sensor names translated
- **Brand icon** вЂ” Official Pogoda.by icon with transparent background (256Г—256 and 512Г—512 pixels)
- **README files in multiple languages** вЂ” Complete setup and troubleshooting guides:
  - Russian: [README.md](README.md)
  - English: [README.en.md](README.en.md)
  - Polish: [README.pl.md](README.pl.md)
  - Belarusian: [README.be.md](README.be.md)
- **HACS configuration** вЂ” Ready for Marketplace/HACS installation with `hacs.json`
- **License** вЂ” MIT license for open-source distribution
- **GitHub Actions workflow** вЂ” Automated testing and syntax checking on every commit
- **Release notes** вЂ” Multilingual release documentation in `RELEASE_NOTES.md`
- **Publication guide** вЂ” Step-by-step instructions in `HACS.md` for publishing to Marketplace/HACS

### Changed
- **Default update interval** вЂ” Increased from 10 minutes to **1 hour (60 minutes)**
  - User-configured intervals are preserved during updates
  - Configurable from 5 to 180 minutes
- **Documentation structure** вЂ” Reorganized README with separate sections for Marketplace and HACS

### Technical Details
- **Sensors**: Temperature, atmospheric pressure, pressure trend, wind speed, wind direction, weather description, observation time, station metadata, humidity (optional), wind gusts (optional), visibility (optional)
- **Device integration**: One device per weather station
- **Data polling**: Coordinated via `DataUpdateCoordinator`, one RSS request per update cycle
- **API compatibility**: No API key required, uses public Pogoda.by RSS and JSON API
- **Dependencies**: Zero production dependencies (uses only Python standard library and Home Assistant built-ins)

### Testing
- **36 automated tests** вЂ” 100% pass rate
  - 25 tests for JSON catalogue and RSS parsing
  - 7 tests for HTTP error handling
  - 4 tests for bundle consistency
- **Syntax validation** вЂ” All Python files compile successfully
- **Localization checks** вЂ” Translation keys synchronized across all 4 languages

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

## Versions

### Semver Compatibility
- **Current version**: 0.1.1 (alpha/preview)
- **Target minimum**: Home Assistant 2025.1.0
- **Minimum Python**: 3.11 (as per Home Assistant requirements)

### Release Timeline
- **0.1.1** (2026-11-12) вЂ” Initial preview release with full Marketplace/HACS support

---

## Migration Notes

### From Unreleased/Development
If upgrading from development versions:
1. The default update interval has changed from 10 to 60 minutes
2. Your custom intervals are automatically preserved
3. No configuration changes required beyond the interval setting if desired

### Between Marketplace and HACS Installation
To switch from one installation method to another:
1. Add the same repository to the target platform (Marketplace or HACS)
2. Install/download the integration
3. No need to delete the existing Pogoda.by entry in Devices & services
4. The integration will update automatically

---

## Contributing

Found an issue or have a suggestion? Please open an issue at:
https://github.com/Toropyga/pogoda_by/issues

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## References

### Official Documentation
- [Marketplace Integration Guide](https://www.home-assistant.io/integrations/marketplace/)
- [HACS Publishing Requirements](https://www.hacs.xyz/docs/publish/integration/)
- [Home Assistant Config Flow Documentation](https://contributors.home-assistant.io/core/integrations/config-entries/)

### Data Source
- **Provider**: Belhydromet (Р‘РµР»РіРёРґСЂРѕРјРµС‚)
- **API**: https://pogoda.by/api/v2/weather-fact/all-cities
- **RSS**: https://pogoda.by/rss/weather
- **Website**: https://pogoda.by

### Related Repositories
- Home Assistant Core: https://github.com/home-assistant/core
- HACS: https://github.com/hacs/integration
- Marketplace Integration Examples: https://github.com/search?q=topic:homeassistant-integration

---

**Last updated**: 2026-11-12  
**Maintained by**: [@Toropyga](https://github.com/Toropyga)

