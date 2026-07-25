# FilamentTracker Live Spool 0.1.1

This patch release improves appliance controls and maintenance while preserving
the public-preview hardware and API behavior.

## Highlights

- fixes Raspberry Pi reboot and shutdown authorization and failure reporting
- runs updater Git operations as the checkout owner
- documents the touchscreen gesture for opening the hidden Technician Menu
- reports the installed software version independently of preserved user configuration
- adds reproducible ZIP and TAR release bundles with SHA-256 checksums

## Install

New Raspberry Pi installations can clone the repository and run:

```bash
sudo ./install.sh
```

Alternatively, download and extract the complete ZIP or TAR bundle attached to
this release, then run the same command from the extracted directory.

## Update

Existing installations can update with:

```bash
