# Hardware

Live Spool is designed as a small appliance built around a Raspberry Pi, NFC reader, scale amplifier, load cell, and touchscreen.

## Tested Hardware

- Raspberry Pi 5
- 7 inch ELECROW touchscreen
- PN532 NFC reader over I2C
- SparkFun HX711 load cell amplifier
- 5 kg load cell

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

Calibration data is saved under:

```text
software/pi-agent/data/
```

## NAU7802

NAU7802 support is planned. The long-term goal is to let builders choose either:

- HX711
- NAU7802
- mock scale

The Android app should not need to care which scale backend the Pi uses.
