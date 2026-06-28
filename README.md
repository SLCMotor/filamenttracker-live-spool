# Live Spool

**An open-source smart filament spool station for Filament Tracker.**

Live Spool is a Raspberry Pi powered smart spool station that automatically identifies filament spools using NFC technology and measures spool weight using a precision load cell.

Designed to work alongside **Filament Tracker**, Live Spool automates spool identification and weight measurement so filament inventory stays accurate with minimal user interaction.

Simply place a spool on the station. Live Spool identifies the spool, measures its weight, and provides real-time data to Filament Tracker.

---

## Why Live Spool?

Keeping track of remaining filament can be tedious.

Most filament inventory systems require users to manually estimate or enter the amount of filament remaining after every print. While this works, it is easy to forget and becomes less accurate over time.

Live Spool was created to remove as much manual work as possible.

The result is a simple workflow:

1. Place the spool on the Live Spool station.
2. The spool is automatically identified.
3. The spool weight is measured.
4. Filament Tracker receives the updated information.

No manual spool selection.  
No manual weight entry.  
Just set the spool down and let Live Spool do the work.

---

## How It Works

    Filament Spool
          |
    NFC Tag + Weight
          |
          v
    Live Spool
    Raspberry Pi 5
    - PN532 NFC
    - HX711 Scale
    - FastAPI API
          |
    Local Network
          |
          v
    Filament Tracker App

Live Spool acts as a dedicated hardware appliance.

It continuously measures spool weight, detects NFC tags, and exposes this information through a local REST API.

Filament Tracker remains the master source of truth for your filament inventory while Live Spool provides accurate, real-world sensor data.

---

## Quick Start

Clone the repository:

    git clone https://github.com/SLCMotor/filamenttracker-live-spool.git
    cd filamenttracker-live-spool

Run the installer:

    ./install.sh

Update later with:

    ./update.sh

Default API endpoint:

    http://<live-spool-ip>:8001/status

---

## Features

### Hardware

- Raspberry Pi 5
- Precision load cell
- HX711 amplifier
- PN532 NFC reader
- 7-inch touchscreen
- Custom 3D printed enclosure

### Software

- FastAPI REST API
- Automatic startup with systemd
- Local network communication
- GitHub deployment workflow
- Installer and updater scripts
- Modular hardware architecture

### Planned

- Live weight monitoring
- NFC tag programming
- Touchscreen dashboard
- Calibration wizard
- Device diagnostics
- Custom boot splash
- OTA software updates
- Multi-device support

---

## Project Status

🚧 **Active Development**

The software foundation has been completed and the project is currently transitioning from simulated hardware to real hardware.

### Completed

- Raspberry Pi platform
- FastAPI REST API
- Local HTTP communication
- Automatic startup using systemd
- GitHub deployment workflow
- Installer script
- Update script
- Mock Scale service
- Mock NFC service

### Currently In Progress

- HX711 Load Cell integration
- PN532 NFC integration
- Touchscreen dashboard
- Live hardware testing

---

*More documentation will be added as the project progresses.*
