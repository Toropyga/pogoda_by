# Release v0.1.3 — Bug Fixes and Compatibility Improvements

**Release Date:** November 12, 2026

## Overview

This release addresses critical compatibility issues discovered during testing on Python 3.11 and fixes JSON parsing errors related to UTF-8 byte order marks (BOM).

## What's Fixed

### 🔧 Critical Fixes

1. **UTF-8 BOM in manifest.json**
   - Removed byte order mark that was causing JSON parsing errors
   - Improved compatibility with environments sensitive to BOM in JSON files
   - Updated test suite to handle BOM using `utf-8-sig` encoding

2. **Python 3.11 Compatibility**
   - Replaced PEP 695 type alias syntax (`type X = Y`) with `TypeAlias` from `typing` module
   - PEP 695 type alias syntax is only available in Python 3.12+
   - Now verified working with both Python 3.11 and 3.12 in GitHub Actions CI/CD

### ✅ Testing

- All 36 unit tests pass on Python 3.11 ✓
- All 36 unit tests pass on Python 3.12 ✓
- GitHub Actions CI/CD validated on every commit
- JSON validation for manifest and configuration files verified

## Installation

### Using HACS

1. Open Home Assistant Settings → Devices & Services → HACS
2. Click the "Custom repositories" option
3. Add repository URL: `https://github.com/Toropyga/pogoda_by`
4. Select "Integration" category
5. Install and restart Home Assistant

### Manual Installation

1. Download the release archive
2. Extract to `custom_components/pogoda_by/` in your Home Assistant config directory
3. Restart Home Assistant

## Compatibility

- **Home Assistant:** 2024.12+
- **Python:** 3.11, 3.12
- **Operating Systems:** Any (Linux, macOS, Windows via Home Assistant OS/Docker)

## Supported Languages

- 🇷🇺 Russian (Русский)
- 🇬🇧 English
- 🇵🇱 Polish (Polski)
- 🇧🇾 Belarusian (Беларускі)

## Known Issues

None reported for this release.

## Special Thanks

- Home Assistant community for feedback and testing
- GitHub Actions for automated CI/CD validation
- All contributors and testers

## Documentation

- [README](README.md) — Main documentation and quick start guide
- [CHANGELOG.md](CHANGELOG.md) — Complete version history
- [GitHub Issues](https://github.com/Toropyga/pogoda_by/issues) — Report bugs or request features
- [GitHub Discussions](https://github.com/Toropyga/pogoda_by/discussions) — Community discussions

---

**GitHub Release:** [Release v0.1.3](https://github.com/Toropyga/pogoda_by/releases/tag/v0.1.3)
