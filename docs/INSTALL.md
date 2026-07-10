# Installation

These instructions install the Live Spool Pi agent as a systemd service on Raspberry Pi OS.

## Requirements

- Raspberry Pi 5
- Raspberry Pi OS
- Network access to GitHub
- Python 3
- Git
- Optional but recommended: 7 inch touchscreen kiosk display
- PN532 NFC reader over I2C
- HX711 load cell amplifier, NAU7802 load cell amplifier, or mock scale mode for development

## Clone

```bash
cd /home/livespool
git clone https://github.com/SLCMotor/filamenttracker-live-spool.git
cd filamenttracker-live-spool
```

## Install

```bash
./install.sh
```

The installer:

- installs system packages
- creates `software/pi-agent/.venv`
- installs Python dependencies
- creates the `live-spool-agent` systemd service
- starts the API on port `8001`

## Verify

```bash
sudo systemctl status live-spool-agent --no-pager -l
curl -s http://localhost:8001/status
curl -s http://localhost:8001/spool/current
curl -s http://localhost:8001/nfc
```

The service should be active and the API should return JSON.

## Update

For a normal update:

```bash
cd /home/livespool/filamenttracker-live-spool
git pull --ff-only
sudo systemctl restart live-spool-agent
sudo systemctl restart lightdm
```

Restarting `lightdm` refreshes the local touchscreen browser. The screen may briefly go blank.

The repo also includes an updater:

```bash
./update.sh
```

## Configuration

Main config file:

```text
software/pi-agent/config/config.yaml
```

Common scale options:

```yaml
scale:
  enabled: true
  backend: "hx711"
  mock: false
  unit: "grams"
  hx711:
    data_pin: 5
    clock_pin: 6
    gain: 128
    samples: 15
  nau7802:
    address: 0x2A
    channel: 1
    gain: 128
    poll_rate: 10
    samples: 15
    stable_stddev: 1000
```

For development without real hardware:

```yaml
hardware:
  device_mode: "mock"

scale:
  backend: "mock"
  mock: true

nfc:
  mock: true
```

For real PN532 NFC and HX711 scale hardware:

```yaml
hardware:
  device_mode: "real"

scale:
  backend: "hx711"
  mock: false

nfc:
  enabled: true
  mock: false
```

For real PN532 NFC and NAU7802 scale hardware:

```yaml
hardware:
  device_mode: "real"

scale:
  backend: "nau7802"
  mock: false
  nau7802:
    address: 0x2A
    channel: 1
    gain: 128
    poll_rate: 10
    samples: 15
    stable_stddev: 1000

nfc:
  enabled: true
  mock: false
```

After changing to the NAU7802 backend, restart the service and run the calibration wizard before relying on scale values.

After changing config:

```bash
sudo systemctl restart live-spool-agent
```

## Android Setup

In FilamentTracker Android:

1. Open Settings.
2. Enable Live Spool integration.
3. Enter the Pi API URL, for example:

```text
http://<live-spool-ip>:8001
```

4. Tap Test Connection.

If the test succeeds, Android can read Live Spool weight and send NFC write jobs to the appliance.

## Troubleshooting

Service logs:

```bash
sudo journalctl -u live-spool-agent -f
```

Restart the API:

```bash
sudo systemctl restart live-spool-agent
```

Restart the display:

```bash
sudo systemctl restart lightdm
```

Check port 8001:

```bash
sudo ss -ltnp | grep ':8001'
```

Check the running process:

```bash
ps -ef | grep '[u]vicorn'
```
