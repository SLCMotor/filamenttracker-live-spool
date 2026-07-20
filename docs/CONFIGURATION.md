# Configuration

Appliance configuration lives outside the Git checkout so updates cannot replace
hardware choices or calibration.

## Files and precedence

1. `LIVE_SPOOL_*` environment variables
2. `/etc/filamenttracker-live-spool/config.yaml`
3. `software/pi-agent/config/config.yaml` for development fallback

The systemd service reads `/etc/filamenttracker-live-spool/live-spool.env`.
Restart the service after changes.

## Environment variables

| Variable | Meaning | Default |
| --- | --- | --- |
| `LIVE_SPOOL_CONFIG_FILE` | YAML file path | system file when present |
| `LIVE_SPOOL_DATA_DIR` | calibration/runtime directory | application `data/` |
| `LIVE_SPOOL_DEVICE_NAME` | advertised device name | `Live Spool` |
| `LIVE_SPOOL_DEVICE_LOCATION` | optional display location | empty |
| `LIVE_SPOOL_API_HOST` | bind address | `0.0.0.0` |
| `LIVE_SPOOL_API_PORT` | HTTP port | `8001` |
| `LIVE_SPOOL_LOG_LEVEL` | Uvicorn log level | `info` |
| `LIVE_SPOOL_SCALE_BACKEND` | `mock`, `nau7802`, or `hx711` | YAML value |
| `LIVE_SPOOL_HX711_DATA_PIN` | BCM data pin | `5` |
| `LIVE_SPOOL_HX711_CLOCK_PIN` | BCM clock pin | `6` |
| `LIVE_SPOOL_NAU7802_ADDRESS` | decimal or `0x` address | `0x2A` |
| `LIVE_SPOOL_PN532_ADDRESS` | decimal or `0x` address | `0x24` |
| `LIVE_SPOOL_DEVELOPMENT_MODE` | expose development behavior | `false` appliance |
| `LIVE_SPOOL_MOCK_HARDWARE` | force all mock devices | `false` appliance |
| `LIVE_SPOOL_SYSTEM_CONTROLS_ENABLED` | expose local appliance controls | `true` on installed appliances |

Boolean values accept `true/false`, `yes/no`, `on/off`, and `1/0`.

## Real NAU7802 example

Set `hardware.device_mode` to `real`, `scale.backend` to `nau7802`, both
`scale.mock` and `nfc.mock` to `false`, and retain PN532 address `0x24`.

## Real HX711 example

Use the same real NFC settings, set `scale.backend` to `hx711`, and configure the
BCM GPIO pins under `scale.hx711`.

System controls are disabled in development defaults and enabled for new
appliance installations. The installer grants the appliance user only the
commands required to restart Live Spool, reboot, and power off. These local
controls do not add authentication and must never be exposed directly to the
Internet.
