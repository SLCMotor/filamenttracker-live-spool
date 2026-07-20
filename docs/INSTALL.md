# Installation

## Requirements

- Raspberry Pi 5 (tested) with 64-bit Raspberry Pi OS
- Raspberry Pi 4 64-bit is provisional/community-supported
- network access during installation
- optional Raspberry Pi OS desktop for touchscreen kiosk mode
- supported NFC/scale hardware, or mock mode

## Install

```bash
git clone https://github.com/SLCMotor/filamenttracker-live-spool.git
cd filamenttracker-live-spool
sudo ./install.sh
```

Use `--scale-backend nau7802` or `--scale-backend hx711` to configure real hardware during a new install; omit it for an interactive choice or safe mock default.

Use `--no-kiosk` for a headless installation. On an unsupported development
machine, `--allow-unsupported` bypasses only the platform check.

The installer enables the local restart, reboot, and shutdown controls and adds
a narrowly scoped sudoers rule for those three appliance operations.

The installer is safe to rerun. It preserves existing external configuration and
calibration. A legacy calibration inside `software/pi-agent/data` is migrated
only when the external destination does not already exist.

## Select hardware

Edit `/etc/filamenttracker-live-spool/config.yaml`. For production NAU7802 and
PN532 operation, change the hardware mode/backend and both mock flags:

```yaml
hardware:
  device_mode: real
scale:
  backend: nau7802
  mock: false
nfc:
  mock: false
```

Restart and verify:

```bash
sudo systemctl restart live-spool-agent
curl --fail http://127.0.0.1:8001/health
curl --fail http://127.0.0.1:8001/status
i2cdetect -y 1
```

## Update

```bash
sudo ./scripts/update.sh
```

The checkout must be clean. Backups are stored below
`/var/backups/filamenttracker-live-spool/`.

## Uninstall

```bash
sudo ./uninstall.sh
```

Configuration and runtime/calibration data are preserved by default. Destructive
removal requires explicit `--remove-config` or `--remove-data` flags and a typed
confirmation (or `--yes` for deliberate automation).
