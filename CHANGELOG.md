# Changelog

All notable changes are documented here. This project follows Semantic
Versioning and the Keep a Changelog format.

## [Unreleased]

### Fixed

- Raspberry Pi reboot and shutdown controls now use installed, narrowly scoped
  authorization and report disabled or failed requests instead of displaying a
  false success state.

## [0.1.0] - 2026-07-20

Initial public preview of the FilamentTracker Live Spool Raspberry Pi appliance.

### Added

- external appliance configuration and runtime-data paths
- preservation-first installer, updater, uninstaller, systemd unit, and kiosk setup
- mock-hardware tests and GitHub Actions quality checks
- public release, security, contribution, and hardware documentation
- publication-safe appliance, interface, component, and wiring photographs
- printable enclosure files, build guides, BOM, and calibration documentation
- CC BY 4.0 attribution and modification record for the derivative enclosure

### Changed

- safe mock hardware is now the development and first-install default
- mock and system-control routes are conditionally exposed
- PN532 address, API listener, scale pins/backend, runtime path, and logging are configurable

### Supported hardware and integration

- PN532, NAU7802, HX711, and Bambu RFID reading
- touchscreen dashboard, calibration, diagnostics, and local REST API
- FilamentTracker Android and FilamentTracker Server workflows
