# Bill of Materials

This list covers the reference FilamentTracker Live Spool appliance. Equivalent
components can be used when their electrical and mechanical specifications are
compatible.

## Core components

| Component | Quantity | Purpose and notes |
| --- | ---: | --- |
| Raspberry Pi 5, 4 GB or 8 GB | 1 | Main controller; Raspberry Pi 4 is expected to work but is not as thoroughly validated |
| ELECROW 7-inch 1024×600 touchscreen | 1 | Local kiosk interface |
| PN532 NFC reader configured for I2C | 1 | Reads and writes FilamentTracker NFC tags; default address `0x24` |
| NAU7802 load-cell ADC | 1 | Recommended scale interface; default address `0x2A` |
| 5 kg four-wire load cell | 1 | Weight sensor |
| microSD card, 32 GB minimum | 1 | Raspberry Pi OS and Live Spool; 64–256 GB is recommended |
| Raspberry Pi USB-C power supply, 5 V/5 A | 1 | Use the official supply or an equivalent high-quality unit |
| NTAG215 NFC tags | As needed | Filament spool identification; compatible NTAG213/216 tags can also be used when capacity permits |

## Recommended and optional components

| Component | Quantity | Purpose and notes |
| --- | ---: | --- |
| Raspberry Pi GPIO breakout board | 1 | Recommended for cleaner wiring, maintenance, and future expansion |
| Raspberry Pi 5 active cooler | 1 | Recommended for sustained appliance use |
| HX711 load-cell ADC | 1 | Optional alternative to the NAU7802; software support is retained |
| NVMe/SSD HAT and drive | 1 | Optional storage expansion supported by the enlarged enclosure |
| M2.5 and M3 fasteners | As needed | Screws, threaded inserts, and standoffs for the selected components |
| M4 × 25 mm screws | 4 | Load-cell and platform mounting; confirm against your printed parts |
| Rubber feet | 4 | Keeps the scale stable and helps isolate vibration |
| Hookup wire and connectors | As needed | Use secure, appropriately sized connections |

## Before ordering

- Confirm the touchscreen model and mounting dimensions. Similar-looking
  seven-inch displays are not necessarily mechanically interchangeable.
- Confirm the PN532 breakout supports I2C and the voltage printed on the board.
- Confirm the NAU7802 or HX711 input and supply requirements.
- Check the load cell's rated capacity, hole spacing, physical dimensions, and
  wiring documentation. Wire colors are not standardized.
- Compare fastener requirements with the current print project before ordering.

## Build notes

- PN532 and NAU7802 intentionally share Raspberry Pi I2C bus 1.
- The reference addresses are `0x24` for PN532 and `0x2A` for NAU7802.
- Do not apply power until supply, ground, SDA, and SCL connections have been
  checked against the [wiring diagram](02_Wiring_Diagram.png).
- The [3MF project](../printable/FilamentTracker_Live_Spool.3mf) is the
  recommended printable; an [STL package](../printable/FilamentTracker_Live_Spool_STL.zip)
  is available for other slicers.

## Enclosure attribution

The printable enclosure is modified from the
[SpoolBuddy enclosure by MartinNYHC](https://makerworld.com/en/models/2296982-spoolbuddy)
under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).
See the complete [attribution and modification record](../ATTRIBUTION.md).
