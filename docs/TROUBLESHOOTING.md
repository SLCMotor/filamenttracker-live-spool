# Troubleshooting

## Service or API unavailable

```bash
sudo systemctl status live-spool-agent --no-pager -l
sudo journalctl -u live-spool-agent -n 100 --no-pager
curl -v http://127.0.0.1:8001/health
```

Verify paths in the installed unit with `systemctl cat live-spool-agent` and check
YAML indentation in `/etc/filamenttracker-live-spool/config.yaml`.

## I2C hardware unavailable

```bash
ls -l /dev/i2c-1
i2cdetect -y 1
groups
```

Expected addresses are PN532 `24` and NAU7802 `2a`. Power down before changing
wiring. Confirm the PN532 board is physically switched/jumpered to I2C mode.
Both devices may share SDA/SCL but require unique addresses and a common ground.

## Incorrect or unstable weight

- ensure the platform is not touching the enclosure
- check that the load direction is consistent
- verify all four bridge connections
- increase sample counts only after checking mechanical noise
- recalibrate with an accurate known weight near the normal operating range
- swap `A+` and `A-` if force produces the opposite sign

## Kiosk does not start

Run the launcher from the desktop user session and inspect errors:

```bash
software/pi-agent/scripts/start-dashboard-kiosk.sh
```

Confirm Chromium is installed and the desktop user's autostart file exists at
`~/.config/autostart/live-spool-kiosk.desktop`.

## Android or Server cannot connect

Confirm the client and Pi are on the same trusted LAN, use the Pi's current local
address and configured port, and do not use `localhost` from the Android device.
Do not expose the port through router forwarding.
