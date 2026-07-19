# Changelog

All notable changes are documented here. This project follows Semantic
Versioning and the Keep a Changelog format.

## [Unreleased]

### Added

- external appliance configuration and runtime-data paths
- preservation-first installer, updater, uninstaller, systemd unit, and kiosk setup
- mock-hardware tests and GitHub Actions quality checks
- public release, security, contribution, and hardware documentation
- publication-safe appliance, interface, component, and wiring photographs

### Changed

- safe mock hardware is now the development and first-install default
- mock and system-control routes are conditionally exposed
- PN532 address, API listener, scale pins/backend, runtime path, and logging are configurable

## [0.1.0] - TBD

Initial public preview of the Live Spool Raspberry Pi appliance, including
PN532, NAU7802, HX711, Bambu RFID reading, touchscreen UI, calibration, and the
FilamentTracker Android/API workflow.
