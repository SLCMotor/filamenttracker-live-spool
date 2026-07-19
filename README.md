# FilamentTracker Live Spool

FilamentTracker Live Spool turns a Raspberry Pi into a local-network spool scale,
NFC/RFID station, touchscreen dashboard, and hardware API for FilamentTracker.
The Android application and FilamentTracker Server remain the inventory systems
of record; Live Spool stores no second spool inventory database.

> [!IMPORTANT]
> Live Spool is designed for a trusted home or workshop LAN. It is not hardened
> for direct Internet exposure. Do not port-forward its API.

## Features

- live spool weight with NAU7802, HX711, or mock scale backends
- PN532 NFC read, verified write, and logical erase operations over I2C
- FilamentTracker JSON/NDEF spool tags and Bambu Lab RFID interoperability
- temporary Android-triggered NFC write sessions
- combined current-spool state without a local inventory database
- touchscreen dashboard, calibration wizard, diagnostics, and settings
- REST API for FilamentTracker Android and FilamentTracker Server
- external configuration and calibration storage designed to survive updates
- idempotent installer, preservation-first updater, and safe uninstaller

## Hardware

Tested appliance:

- Raspberry Pi 5 with 64-bit Raspberry Pi OS
- ELECROW 7-inch 1024×600 touchscreen
- PN532 NFC reader in I2C mode at `0x24`
- NAU7802 load-cell ADC at `0x2A`
- 5 kg four-wire load cell

Also supported in software:

- HX711 load-cell ADC using BCM GPIO pins (defaults: data 5, clock 6)
- mock hardware on Linux development systems

Raspberry Pi 5 is the reference and tested platform. Raspberry Pi 4 with a
64-bit Raspberry Pi OS is expected to work but has not yet received the same
hardware validation. See [Hardware](docs/HARDWARE.md) before wiring anything.

## Wiring summary

PN532 and NAU7802 intentionally share I2C bus 1:

| Signal | Raspberry Pi | PN532 | NAU7802 |
| --- | --- | --- | --- |
| 3.3 V | Pin 1 or 17 | VCC/VIN* | VCC/VIN* |
| Ground | Any GND | GND | GND |
| SDA1 | GPIO 2 / pin 3 | SDA | SDA |
| SCL1 | GPIO 3 / pin 5 | SCL | SCL |

\* Confirm the voltage requirement printed on your exact breakout board.

Default HX711 wiring:

| HX711 | Raspberry Pi |
| --- | --- |
| VCC | 3.3 V |
| GND | Ground |
| DAT / DOUT | GPIO 5 / pin 29 |
| CLK / SCK | GPIO 6 / pin 31 |

Load-cell wire colors are not universal. For the tested cell, red is `E+`, black
is `E-`, green is `A+`, and white is `A-`. Verify your load-cell datasheet.

## Install

```bash
git clone https://github.com/SLCMotor/filamenttracker-live-spool.git
cd filamenttracker-live-spool
sudo ./install.sh
```

The installer checks the platform, installs system packages, enables I2C, creates
a virtual environment, installs the service and optional kiosk autostart, and
verifies the local API. Existing configuration and calibration are preserved.
New installs use safe mock-hardware defaults; select `nau7802` or `hx711` in:

```text
/etc/filamenttracker-live-spool/config.yaml
```

Then restart:

```bash
sudo systemctl restart live-spool-agent
curl --fail http://127.0.0.1:8001/status
```

Detailed instructions: [Installation](docs/INSTALL.md).

## Configuration

Configuration precedence is environment variables, external YAML, then the
repository development defaults. Appliance files are:

```text
/etc/filamenttracker-live-spool/config.yaml
/etc/filamenttracker-live-spool/live-spool.env
/var/lib/filamenttracker-live-spool/calibration.json
```

Configurable values include device name/location, API host and port, log level,
runtime directory, scale backend and GPIO pins, I2C addresses, development mode,
mock hardware, and local system-control availability. See
[Configuration](docs/CONFIGURATION.md).

## REST API

Common endpoints:

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | process health without requiring hardware |
| GET | `/status` | combined appliance and hardware status |
| GET | `/weight` | current scale reading |
| GET | `/nfc` | NFC reader and current tag state |
| GET | `/spool/current` | combined live scale and tag snapshot |
| POST | `/nfc/write` | start a temporary verified write session |
| POST | `/nfc/erase` | logically erase a writable NTAG |
| GET/POST | `/calibration/*` | inspect or perform calibration |

Mock routes exist only in development/mock mode. System power routes are disabled
by default. The API intentionally has no cloud discovery or remote-access layer.
See the complete [REST API](docs/API.md) and
[Android integration](docs/ANDROID_INTEGRATION.md).

## Calibration

Open `http://<live-spool-host>:8001/calibration-wizard`, remove all weight, tare,
place an accurately known weight, enter its mass, and verify the result. The
calibration file is written atomically under `/var/lib` and is not overwritten
by installation or updates.

## Screenshots

Release screenshots are not available yet. Contributions of publication-safe
photos or screenshots showing the dashboard, calibration flow, and completed
hardware are welcome. Do not include Wi-Fi credentials, private addresses, NFC
UIDs, or personal inventory data in submitted images.

## Updating

```bash
cd filamenttracker-live-spool
sudo ./scripts/update.sh
```

The updater requires a clean checkout, creates a timestamped configuration and
calibration backup, performs a fast-forward-only pull, updates dependencies,
restarts the service, and verifies health. It never pushes changes.

## Troubleshooting

Start with:

```bash
sudo systemctl status live-spool-agent --no-pager -l
sudo journalctl -u live-spool-agent -n 100 --no-pager
i2cdetect -y 1
curl --fail http://127.0.0.1:8001/health
```

Expected I2C addresses are `24` for PN532 and `2a` for NAU7802. See
[Troubleshooting](docs/TROUBLESHOOTING.md).

## Known limitations

- Raspberry Pi 5 is the only fully validated Pi model today.
- The API assumes a trusted LAN and must not be exposed directly to the Internet.
- Bambu RFID support is read-only and depends on successful tag authentication.
- NFC writing targets compatible NTAG/NDEF tags; tag capacity varies.
- Kiosk behavior varies among Raspberry Pi OS desktop/display-server releases.
- Scale accuracy depends heavily on mechanical construction and calibration.

## Roadmap

- validate Raspberry Pi 4 and additional displays
- improve guided hardware selection during installation
- add authentication for optional administrative operations
- expand Android and FilamentTracker Server integration tests
- publish enclosure/build plans and real appliance photographs
- add upgrade rollback assistance and packaged releases

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Please report security issues privately
rather than opening a public issue.

## License

MIT. See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
FilamentTracker and Bambu Lab names belong to their respective owners; this
project is an independent interoperability tool.
