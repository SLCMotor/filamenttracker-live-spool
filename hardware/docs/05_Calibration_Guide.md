# Calibration Guide

Calibration converts raw load-cell readings into grams. Perform it during the
initial build and repeat it whenever the load cell, scale ADC, mounting, or
platform mechanics change.

Calibration is stored outside the repository at:

```text
/var/lib/filamenttracker-live-spool/calibration.json
```

Installation and updates preserve this file.

## Before you begin

- Place Live Spool on a solid, level surface.
- Make sure the platform moves freely and does not touch the enclosure.
- Check that no cable pulls on the platform or load cell.
- Remove the spool and every other object from the platform.
- Use an accurately known reference weight. A 500 g or 1,000 g calibration
  weight is a practical choice for the 5 kg reference load cell.
- Allow the electronics and displayed reading to stabilize.
- Do not touch or lean on the appliance during measurements.

## Open the calibration wizard

Use the dashboard calibration shortcut, the technician menu, or open:

```text
http://<live-spool-host>:8001/calibration-wizard
```

Replace `<live-spool-host>` with the appliance hostname or local IP address.

## Calibration procedure

1. **Remove all weight.** Confirm that the platform is completely empty.
2. **Tare the scale.** Press **Tare** to record the unloaded zero offset.
3. **Add the reference weight.** Place it gently in the center of the platform.
4. **Enter its mass.** Select the matching preset or enter the exact value in
   grams. Enter the reference weight's known mass—not the displayed reading.
5. **Calibrate.** Wait for a stable measurement, then run the calibration step.
6. **Verify.** Confirm that the measured value is acceptably close to the known
   mass.
7. **Save.** Finish the wizard so the calibration is persisted across reboots.

## Verify the result

1. Remove the reference weight and confirm the reading returns close to zero.
2. Place the weight in the center again and allow the reading to settle.
3. Compare the displayed value with the known mass.
4. Repeat this test two or three times.

A small amount of variation is normal. Large, inconsistent, or steadily
changing errors usually indicate a mechanical or wiring problem rather than a
calibration-value problem.

## Troubleshooting

### Reading drifts while untouched

- Check that the platform and load cell do not touch the enclosure.
- Make sure wiring is not applying force to the moving assembly.
- Move the appliance away from vibration, drafts, or an unstable work surface.
- Allow the electronics to warm up and repeat tare.

### Calibration fails or reports the wrong value

- Confirm the entered reference mass is correct and expressed in grams.
- Make sure the platform was empty during tare.
- Center the reference weight and wait for a stable reading.
- Repeat the complete process rather than calibrating over an old tare.

### Reading is unstable

- Inspect load-cell wiring and tighten loose terminals.
- Check load-cell and platform fasteners without mechanically binding the beam.
- Confirm the selected scale backend matches the installed ADC.
- Keep NFC and other wiring clear of the weighing mechanism.

### No weight is detected

For NAU7802 installations, verify that address `0x2A` appears:

```bash
i2cdetect -y 1
```

Then inspect service and hardware status:

```bash
curl --fail http://127.0.0.1:8001/status
curl --fail http://127.0.0.1:8001/weight
sudo journalctl -u live-spool-agent -n 100 --no-pager
```

For HX711 installations, recheck the configured data and clock GPIO pins.

## Recalibrate after hardware changes

Always recalibrate after changing the load cell, ADC, platform, mounting
hardware, or anything that changes the mechanical load path. A normal software
update does not require recalibration.
