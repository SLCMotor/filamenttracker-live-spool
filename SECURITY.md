# Security Policy

## Supported versions

Until the first public tag, only the latest commit on `main` receives security
fixes. After `v0.1.0`, the latest released version and `main` will be supported.

## Intended deployment

Live Spool is a trusted-local-network appliance. It has no TLS termination,
Internet authentication, or remote-access hardening. Do not expose its HTTP port
through router port forwarding, a public reverse proxy, or a public tunnel.
Network-capable endpoints can write/erase NFC tags and change calibration.
Optional system power controls are disabled by default.

Use host/router firewalling and an isolated IoT/workshop VLAN when appropriate.
Treat NFC contents, tag UIDs, device names, and diagnostic output as potentially
sensitive local data.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting feature for this repository. Include
the affected commit/version, deployment assumptions, reproduction steps, impact,
and any suggested mitigation. Do not include real credentials, private addresses,
or private NFC/inventory data.

Please allow a reasonable period for acknowledgement and remediation before
public disclosure. Security fixes will be credited unless anonymity is requested.
