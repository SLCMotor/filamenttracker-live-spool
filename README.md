# FilamentTracker Live Spool

Live Spool is a Raspberry Pi appliance for the FilamentTracker Android app. It reads NFC/RFID tags, measures spool weight, shows a local touchscreen dashboard, and exposes a local REST API for Android.

FilamentTracker Android is the source of truth. Live Spool does not keep its own inventory database. It only reports real-world hardware state and temporarily handles NFC write requests.

## Current Status

Live Spool currently supports:

- Raspberry Pi 5
- 7 inch touchscreen dashboard
- FastAPI local REST API on port `8001`
- PN532 NFC reader over I2C
- FilamentTracker JSON NFC tags
- Bambu Lab RFID tag reading where authentication succeeds
- NFC tag erase and write tools
- Android-triggered NFC write sessions
- HX711 load cell scale backend
- NAU7802 scale backend over I2C
- Mock hardware mode for development
- Calibration wizard
- Diagnostics and settings pages
- System controls for app restart, Pi reboot, and Pi shutdown

The software is active development, but the main appliance workflow is working:

1. Android opens a spool.
2. Android sends a write request to Live Spool.
3. Live Spool switches to the NFC writer screen.
4. The user places a writable NFC tag on the reader.
5. Live Spool writes, verifies, and returns to the dashboard.
6. Android receives the result.

## Architecture

```text
FilamentTracker Android
  - master database
  - brands, materials, colors
  - spool IDs and inventory
  - remaining grams
  - user approval and sync decisions

        |
        | local HTTP API
        v

FilamentTracker Live Spool
  - NFC/RFID reader
  - live weight scale
  - touchscreen dashboard
  - temporary NFC write sessions
  - no local spool database
```

Live Spool can read the weight snapshot stored on a FilamentTracker NFC tag and compare it with the live scale reading. When the physical weight differs from the tag snapshot, Live Spool displays the difference. Android is still responsible for saving the updated inventory value and rewriting the tag.

## Repository Layout

```text
.
|-- install.sh
|-- update.sh
|-- docs/
|   |-- API.md
|   |-- ANDROID_INTEGRATION.md
|   |-- HARDWARE.md
|   `-- INSTALL.md
`-- software/pi-agent/
    |-- app/
    |-- config/config.yaml
    |-- static/
    `-- templates/
```

## Quick Start

Clone and install on the Raspberry Pi:

```bash
git clone https://github.com/SLCMotor/filamenttracker-live-spool.git
cd filamenttracker-live-spool
./install.sh
```

Update an installed appliance:

```bash
cd /home/livespool/filamenttracker-live-spool
git pull --ff-only
sudo systemctl restart live-spool-agent
sudo systemctl restart lightdm
```

Check the API:

```bash
curl http://localhost:8001/status
curl http://localhost:8001/spool/current
curl http://localhost:8001/nfc
```

## Default URLs

Replace `<live-spool-ip>` with your Pi address.

- Dashboard: `http://<live-spool-ip>:8001/dashboard`
- Status API: `http://<live-spool-ip>:8001/status`
- Current spool state: `http://<live-spool-ip>:8001/spool/current`
- NFC status: `http://<live-spool-ip>:8001/nfc`
- Calibration wizard: `http://<live-spool-ip>:8001/calibration-wizard`
- Settings: `http://<live-spool-ip>:8001/settings`

## FilamentTracker NFC Payload

Live Spool reads and writes FilamentTracker JSON payloads. A spool tag can include:

```json
{
  "app": "FT",
  "ver": 1,
  "type": "spool",
  "spoolId": "b85d04fc-bcb0-4d84-8b0f-29ff79d6e9cd",
  "filamentId": "6666d29d-47f4-4ced-9818-2dc9bbeb1724",
  "brand": "Creality",
  "material": "Hyper PLA",
  "colorName": "Gray",
  "colorHex": "#808080",
  "initialGrams": 1000,
  "remainingGrams": 200.52,
  "updatedAtEpochMs": 1780000000000
}
```

The tag is a portable snapshot. Android remains the master database.

## Documentation

- [Installation](docs/INSTALL.md)
- [Hardware](docs/HARDWARE.md)
- [API](docs/API.md)
- [Android integration](docs/ANDROID_INTEGRATION.md)

## Useful Service Commands

```bash
sudo systemctl status live-spool-agent --no-pager -l
sudo systemctl restart live-spool-agent
sudo journalctl -u live-spool-agent -f
sudo systemctl restart lightdm
```

`lightdm` controls the local display session. Restart it when the touchscreen kiosk needs to reload cached dashboard JavaScript.

## Roadmap

Planned next steps:

- continued NAU7802 calibration tuning with real spools
- tighter Android synchronization flows
- automatic Android prompts when Live Spool detects a changed spool
- remaining filament calculations using verified live scale readings
- stronger setup tools for choosing scale backend and GPIO pins
