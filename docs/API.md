# API

Live Spool exposes a local HTTP API on port `8001`.

Example base URL:

```text
http://<live-spool-ip>:8001
```

## Status

```http
GET /status
```

Returns overall API, scale, NFC, CPU temperature, and uptime.

Example:

```json
{
  "status": "online",
  "deviceName": "Live Spool",
  "version": "0.1.0",
  "scale": {
    "connected": true,
    "stable": true,
    "weightGrams": 1000.93
  },
  "nfc": {
    "connected": true,
    "tagPresent": false,
    "tagId": null,
    "data": null,
    "tag": null,
    "tagType": null,
    "bambu": null,
    "error": null
  },
  "cpuTempC": 54.0,
  "uptime": "58m"
}
```

## Weight

```http
GET /weight
```

Returns the scale status.

Example:

```json
{
  "connected": true,
  "stable": true,
  "weightGrams": 1000.93
}
```

## NFC

```http
GET /nfc
```

Returns the current NFC reader state.

FilamentTracker tag example:

```json
{
  "connected": true,
  "tagPresent": true,
  "tagId": "0479DDA3822681",
  "data": "{\"app\":\"FT\",\"ver\":1,\"type\":\"spool\"}",
  "tag": {
    "app": "FT",
    "ver": 1,
    "type": "spool",
    "spoolId": "b85d04fc-bcb0-4d84-8b0f-29ff79d6e9cd",
    "filamentId": "6666d29d-47f4-4ced-9818-2dc9bbeb1724",
    "brand": "Creality",
    "material": "Hyper PLA",
    "colorName": "Gray",
    "colorHex": "#808080",
    "initialGrams": 1000,
    "remainingGrams": 200.52,
    "updatedAtEpochMs": 1780000000000
  },
  "tagType": "filamenttracker",
  "bambu": null,
  "error": null
}
```

Bambu Lab RFID tag example:

```json
{
  "connected": true,
  "tagPresent": true,
  "tagId": "01B76103",
  "tag": {
    "app": "Bambu Lab",
    "type": "rfid",
    "uid": "01B76103",
    "brand": "Bambu Lab",
    "material": "PLA",
    "variant": "PLA Basic",
    "filamentCode": "A00-G06",
    "colorHex": "#00AE42",
    "spoolWeightG": 1000
  },
  "tagType": "bambu_lab_rfid",
  "bambu": {
    "isBambuTag": true,
    "uid": "01B76103",
    "authenticatedSectorCount": 16,
    "readBlockCount": 48,
    "parseWarnings": []
  },
  "error": null
}
```

## Erase NFC Tag

```http
POST /nfc/erase
```

Performs a logical erase of a writable NTAG by replacing user data with an empty NDEF message.

## Write NFC Tag

```http
POST /nfc/write
```

Starts an NFC write session. The request is temporary and is discarded after the write succeeds, fails, is canceled, or times out.

Request:

```json
{
  "requestId": "android-unique-request-id",
  "timeoutSeconds": 60,
  "payload": {
    "app": "FT",
    "ver": 1,
    "type": "spool",
    "spoolId": "b85d04fc-bcb0-4d84-8b0f-29ff79d6e9cd",
    "filamentId": "6666d29d-47f4-4ced-9818-2dc9bbeb1724",
    "brand": "Creality",
    "material": "Hyper PLA",
    "colorName": "Gray",
    "colorHex": "#808080",
    "initialGrams": 1000,
    "remainingGrams": 200.52,
    "updatedAtEpochMs": 1780000000000
  },
  "display": {
    "locationName": "Filament Rack"
  }
}
```

Response:

```json
{
  "requestId": "android-unique-request-id",
  "state": "ready",
  "message": "Ready to Write",
  "tagId": null,
  "errorCode": null,
  "payload": {},
  "display": {},
  "startedAt": "2026-07-03T04:43:02.170112+00:00",
  "updatedAt": "2026-07-03T04:43:02.170112+00:00",
  "finishedAt": null
}
```

Write states:

| State | Meaning |
| --- | --- |
| `ready` | Waiting for a tag |
| `writing` | Writing the payload |
| `verifying` | Reading back and checking the payload |
| `succeeded` | Write and verification succeeded |
| `failed` | Write failed |
| `timed_out` | No writable tag was completed before timeout |
| `canceled` | Request was canceled |
| `idle` | No active request |

Poll current write session:

```http
GET /nfc/write/current
```

Poll by request ID:

```http
GET /nfc/write/{requestId}
```

Cancel:

```http
DELETE /nfc/write/{requestId}
```

## Current Spool State

```http
GET /spool/current
```

Returns combined scale and NFC state for the dashboard and Android workflows.

Important fields:

| Field | Meaning |
| --- | --- |
| `loaded` | True when a FilamentTracker spool is recognized |
| `weightGrams` | Current live scale reading |
| `tagPresent` | True when any NFC/RFID tag is present |
| `tagId` | Current tag UID |
| `spool` | Parsed FilamentTracker spool payload, if available |
| `nfc` | Raw NFC status |
| `scale` | Raw scale status |
| `tagWeightGrams` | `remainingGrams` read from the NFC tag |
| `weightDeltaGrams` | Live scale minus tag weight snapshot |
| `tagWeightChanged` | True when delta exceeds tolerance |
| `weightToleranceGrams` | Current comparison tolerance |

## Calibration

```http
GET /calibration/status
POST /calibration/tare
POST /calibration/known-weight
POST /calibration/reset
```

Known weight request:

```json
{
  "knownWeightGrams": 1000
}
```

## UI Pages

```text
/dashboard
/diagnostics
/settings
/settings/scale
/settings/nfc
/settings/network
/settings/display
/settings/about
/calibration-wizard
```

## Process Health

```http
GET /health
```

Returns application process health and version without requiring the scale or NFC
reader to be connected. Use `/status` when hardware state is also required.

## Local-network security

The API is intended only for a trusted LAN and must not be exposed directly to
the Internet. Mock endpoints are registered only in development/mock mode.
`/system/*` routes are disabled unless `system_controls_enabled` is deliberately
set. Enabling those routes does not add authentication or Internet hardening.
