#!/usr/bin/env bash
set -e

DASHBOARD_URL="http://localhost:8001/dashboard"

# Wait for the Live Spool API/dashboard to be ready before opening Chromium.
for i in {1..60}; do
  if curl -fsS "$DASHBOARD_URL" >/dev/null 2>&1; then
    break
  fi

  sleep 1
done

# Keep the display awake.
xset s off || true
xset -dpms || true
xset s noblank || true

# Launch Chromium in kiosk mode.
exec /usr/bin/chromium \
  --kiosk "$DASHBOARD_URL" \
  --noerrdialogs \
  --disable-infobars \
  --disable-session-crashed-bubble \
  --disable-features=TranslateUI \
  --password-store=basic \
  --user-data-dir=/home/livespool/.config/chromium-live-spool-kiosk
