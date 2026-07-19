#!/usr/bin/env bash
set -e

export DISPLAY="${DISPLAY:-:0}"

DASHBOARD_URL="${LIVE_SPOOL_DASHBOARD_URL:-http://localhost:8001/dashboard}"
KIOSK_DATA_DIR="${LIVE_SPOOL_KIOSK_DATA_DIR:-${XDG_STATE_HOME:-$HOME/.local/state}/filamenttracker-live-spool/chromium}"
mkdir -p "$KIOSK_DATA_DIR"

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

# Hide cursor after idle if unclutter is installed.
if command -v unclutter >/dev/null 2>&1; then
  unclutter -idle 2 -root &
fi

# Launch Chromium in kiosk mode.
exec /usr/bin/chromium \
  --kiosk "$DASHBOARD_URL" \
  --noerrdialogs \
  --disable-infobars \
  --disable-session-crashed-bubble \
  --disable-features=TranslateUI \
  --password-store=basic \
  --user-data-dir="$KIOSK_DATA_DIR"
