# Hardware

Live Spool is designed as a small appliance built around a Raspberry Pi, NFC reader, scale amplifier, load cell, and touchscreen.

For the printable enclosure and illustrated build package, see the
[hardware documentation index](../hardware/README.md).

## Tested Hardware

- Raspberry Pi 5
- 64-bit Raspberry Pi OS Trixie
- 7 inch ELECROW touchscreen
- PN532 NFC reader over I2C
- SparkFun HX711 load cell amplifier
- 5 kg load cell

## Supported Scale Backends

Live Spool currently supports these scale backends:

| Backend | Status | Notes |
| --- | --- | --- |
| `hx711` | Tested | SparkFun HX711 on GPIO 5/6 |
| `nau7802` | Tested on Raspberry Pi 5 | NAU7802 over I2C at default address `0x2A` |
| `mock` | Tested | Development and UI testing |

## PN532 NFC Reader

The current PN532 implementation uses I2C.

Typical Raspberry Pi I2C pins:

| PN532 | Raspberry Pi |
| --- | --- |
| VIN / VCC | 3.3V or board-supported power input |
| GND | GND |
| SDA | GPIO 2 / SDA1 |
| SCL | GPIO 3 / SCL1 |

Enable I2C on the Pi if it is not already enabled.

```bash
sudo raspi-config
```

Then use Interface Options to enable I2C.

The code currently initializes the PN532 at I2C address `0x24`.

## HX711 Scale

The current tested HX711 GPIO wiring is:

| HX711 | Raspberry Pi |
| --- | --- |
| VDD / VCC | 3.3V |
| GND | GND |
| DAT | GPIO 5 |
| CLK | GPIO 6 |

Corresponding config:

```yaml
scale:
  backend: "hx711"
  mock: false
  hx711:
    data_pin: 5
    clock_pin: 6
    gain: 128
    samples: 15
```

Use 3.3V for Pi GPIO logic compatibility.

## Load Cell Wiring

For the tested 4-wire load cell:

| Load cell wire | HX711 |
| --- | --- |
| Red | E+ |
| Black | E- |
| White | A- |
| Green | A+ |

If the load cell has a yellow shield wire, leave it unconnected unless your load cell documentation says otherwise.

If weight increases in the wrong direction, swap `A+` and `A-`.

## Calibration

### Open the technician menu

Press and hold the **Filament Tracker / Live Spool** title in the upper-left
corner of the touchscreen for about one second. When the hold indicator
completes, select **Calibration**. The same menu also provides Dashboard,
Diagnostics, and Settings shortcuts.

Calibration can be started from:

- the dashboard Calibrate shortcut
- the technician menu
- `/calibration-wizard`

Recommended flow:

1. Remove all weight from the scale.
2. Tare the scale.
3. Place a known weight on the scale.
4. Enter the known weight in grams.
5. Save calibration.
6. Verify with the same known weight.

Calibration data is saved on installed appliances under:

```text
/var/lib/filamenttracker-live-spool/calibration.json
```

## NAU7802 Scale

NAU7802 support is implemented with direct I2C register access. Your `i2cdetect`
scan should show the NAU7802 at address `0x2A`.

Typical Raspberry Pi I2C wiring:

| NAU7802 | Raspberry Pi |
| --- | --- |
| VIN / VCC | 3.3V |
| GND | GND |
| SDA | GPIO 2 / SDA1 |
| SCL | GPIO 3 / SCL1 |

Load cell wiring is the same bridge layout as HX711 boards:

| Load cell wire | NAU7802 |
| --- | --- |
| Red | E+ |
| Black | E- |
| White | A- |
| Green | A+ |

Corresponding config:

```yaml
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
```

The Android app does not need to care which scale backend the Pi uses.

## Photographs

See the [hardware gallery](GALLERY.md) for publication-safe photographs of the completed appliance, display enclosure, Raspberry Pi 5, load cell, PN532, NAU7802, HX711, GPIO breakout, and installed wiring.

## Printable enclosure

Use the [3MF print project](../hardware/printable/FilamentTracker_Live_Spool.3mf)
for the recommended plate layout or the
[STL package](../hardware/printable/FilamentTracker_Live_Spool_STL.zip) with
another slicer. Build guides and licensing details are maintained under
[`hardware/`](../hardware/README.md).
