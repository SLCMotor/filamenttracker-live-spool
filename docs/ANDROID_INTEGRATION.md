# Android Integration

FilamentTracker Android is the master database. Live Spool is a local hardware appliance.

The integration rule is:

```text
Android owns inventory.
Live Spool reports hardware state and performs temporary NFC write jobs.
```

## Android Settings

In FilamentTracker Android:

1. Open Settings.
2. Enable Live Spool integration.
3. Enter the Live Spool API URL:

```text
http://<live-spool-ip>:8001
```

4. Tap Test Connection.

If the connection succeeds, Android can:

- read Live Spool scale weight
- send NFC write jobs to the Pi
- update a spool after user confirmation
- rewrite NFC tags with updated weight snapshots

## Spool NFC Writing

Android supports two spool-specific NFC write paths:

- Phone NFC
- Live Spool NFC

Both write the same FilamentTracker spool payload. The difference is which device writes the tag.

### Phone NFC

1. Open a filament.
2. Find the target spool card.
3. Tap Phone NFC.
4. Hold a writable NFC tag to the phone.

### Live Spool NFC

1. Open a filament.
2. Find the target spool card.
3. Tap Live Spool NFC.
4. Android sends `POST /nfc/write` to the Pi.
5. Live Spool switches to its write screen.
6. Place a writable NFC tag on the Pi reader.
7. Live Spool writes, verifies, and returns to the dashboard.
8. Android receives success or failure.

## Payload Schema

Recommended spool payload:

```json
{
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
}
```

Required minimum fields:

- `app`: `FT`
- `ver`: payload version, currently `1`
- `type`: `spool`
- `spoolId`
- `filamentId`

Optional but useful fields:

- `brand`
- `material`
- `colorName`
- `colorHex`
- `initialGrams`
- `remainingGrams`
- `updatedAtEpochMs`

The tag is a snapshot. It should not be treated as the source of truth.

## Weight Update Workflow

Recommended appliance workflow:

1. Place tagged spool on Live Spool.
2. Live Spool reads the tag and live scale weight.
3. Live Spool compares live weight to tag `remainingGrams`.
4. If the values differ beyond tolerance, Live Spool displays the change.
5. In Android, open that spool and tap Update Weight from Live Spool.
6. Android shows current saved weight, detected weight, and difference.
7. User confirms.
8. Android saves the new remaining grams.
9. Android offers to rewrite the NFC tag.
10. User chooses Phone NFC or Live Spool NFC.

This keeps Android authoritative while still making the Pi feel automatic.

## Error Handling

Android should handle:

- Pi unavailable
- scale disconnected
- NFC reader disconnected
- writer busy
- write timeout
- verification failure
- user cancellation

Live Spool write states:

- `ready`
- `writing`
- `verifying`
- `succeeded`
- `failed`
- `timed_out`
- `canceled`

Android should poll `GET /nfc/write/{requestId}` or `GET /nfc/write/current` until a terminal state is reached.

Terminal states:

- `succeeded`
- `failed`
- `timed_out`
- `canceled`

## Important Design Notes

- Live Spool should not maintain a spool database.
- Live Spool should not decide inventory changes.
- Live Spool may display weight differences.
- Android should approve and save inventory changes.
- Android should decide whether to rewrite the NFC tag.
