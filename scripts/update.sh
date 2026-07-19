#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="live-spool-agent"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PI_AGENT_DIR="$APP_DIR/software/pi-agent"
VENV_DIR="$PI_AGENT_DIR/.venv"
CONFIG_DIR="/etc/filamenttracker-live-spool"
DATA_DIR="/var/lib/filamenttracker-live-spool"
BACKUP_ROOT="/var/backups/filamenttracker-live-spool"

if [[ $EUID -ne 0 ]]; then
  echo "Run with sudo: sudo ./scripts/update.sh" >&2
  exit 1
fi
if [[ -n "$(git -C "$APP_DIR" status --porcelain)" ]]; then
  echo "Refusing to update a checkout with local changes." >&2
  git -C "$APP_DIR" status --short >&2
  exit 1
fi

old_commit="$(git -C "$APP_DIR" rev-parse HEAD)"
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
backup_dir="$BACKUP_ROOT/$stamp"
install -d -m 0700 "$backup_dir"
for source in "$CONFIG_DIR/config.yaml" "$CONFIG_DIR/live-spool.env" "$DATA_DIR/calibration.json"; do
  [[ -f "$source" ]] && cp -a "$source" "$backup_dir/"
done
printf '%s\n' "$old_commit" >"$backup_dir/previous-commit.txt"

echo "Updating from $old_commit (backup: $backup_dir)"
git -C "$APP_DIR" pull --ff-only
if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  python3 -m venv "$VENV_DIR"
fi
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$PI_AGENT_DIR/requirements.txt"
systemctl restart "$SERVICE_NAME"

port="$(sed -n 's/^LIVE_SPOOL_API_PORT=//p' "$CONFIG_DIR/live-spool.env" 2>/dev/null | tail -1)"
port="${port:-8001}"
for _ in {1..30}; do
  if curl -fsS "http://127.0.0.1:${port}/status" >/dev/null; then
    echo "Update complete: $(git -C "$APP_DIR" rev-parse --short HEAD)"
    exit 0
  fi
  sleep 1
done
systemctl status "$SERVICE_NAME" --no-pager -l || true
echo "Update installed, but health verification failed." >&2
echo "Previous commit: $old_commit; backup: $backup_dir" >&2
exit 1
