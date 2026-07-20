#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="live-spool-agent"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PI_AGENT_DIR="$APP_DIR/software/pi-agent"
VENV_DIR="$PI_AGENT_DIR/.venv"
CONFIG_DIR="/etc/filamenttracker-live-spool"
DATA_DIR="/var/lib/filamenttracker-live-spool"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
SUDOERS_FILE="/etc/sudoers.d/filamenttracker-live-spool"
BACKUP_ROOT="/var/backups/filamenttracker-live-spool"

if [[ $EUID -ne 0 ]]; then
  echo "Run with sudo: sudo ./scripts/update.sh" >&2
  exit 1
fi

REPO_USER="$(stat -c '%U' "$APP_DIR/.git")"
if [[ -z "$REPO_USER" || "$REPO_USER" == root ]] || ! id "$REPO_USER" >/dev/null 2>&1; then
  echo "Could not determine the non-root Git checkout owner." >&2
  exit 1
fi
git_as_owner() {
  runuser -u "$REPO_USER" -- git -C "$APP_DIR" "$@"
}
if [[ -n "$(git_as_owner status --porcelain)" ]]; then
  echo "Refusing to update a checkout with local changes." >&2
  git_as_owner status --short >&2
  exit 1
fi

old_commit="$(git_as_owner rev-parse HEAD)"
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
backup_dir="$BACKUP_ROOT/$stamp"
install -d -m 0700 "$backup_dir"
for source in \
  "$CONFIG_DIR/config.yaml" \
  "$CONFIG_DIR/live-spool.env" \
  "$DATA_DIR/calibration.json" \
  "$SERVICE_FILE" \
  "$SUDOERS_FILE"; do
  [[ -f "$source" ]] && cp -a "$source" "$backup_dir/"
done
printf '%s\n' "$old_commit" >"$backup_dir/previous-commit.txt"

echo "Updating from $old_commit (backup: $backup_dir)"
git_as_owner pull --ff-only
if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  python3 -m venv "$VENV_DIR"
fi
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$PI_AGENT_DIR/requirements.txt"

APP_USER="$(systemctl show -p User --value "$SERVICE_NAME")"
if [[ -z "$APP_USER" || "$APP_USER" == root ]] || ! id "$APP_USER" >/dev/null 2>&1; then
  echo "Could not determine the installed appliance user." >&2
  exit 1
fi
APP_GROUP="$(id -gn "$APP_USER")"

supplementary=()
for group in i2c gpio spi; do
  getent group "$group" >/dev/null && supplementary+=("$group")
done
supplementary_line="# No supplementary hardware groups found"
if ((${#supplementary[@]})); then
  supplementary_line="SupplementaryGroups=${supplementary[*]}"
fi

sed \
  -e "s|@APP_USER@|$APP_USER|g" \
  -e "s|@APP_GROUP@|$APP_GROUP|g" \
  -e "s|@PI_AGENT_DIR@|$PI_AGENT_DIR|g" \
  -e "s|@VENV_DIR@|$VENV_DIR|g" \
  -e "s|@SUPPLEMENTARY_GROUPS@|$supplementary_line|g" \
  "$APP_DIR/deploy/systemd/live-spool-agent.service" >"$SERVICE_FILE"
chmod 0644 "$SERVICE_FILE"

sed "s|@APP_USER@|$APP_USER|g" \
  "$APP_DIR/deploy/sudoers/live-spool-agent" >"$SUDOERS_FILE"
chmod 0440 "$SUDOERS_FILE"
visudo -cf "$SUDOERS_FILE" >/dev/null

systemctl daemon-reload
systemctl restart "$SERVICE_NAME"

port="$(sed -n 's/^LIVE_SPOOL_API_PORT=//p' "$CONFIG_DIR/live-spool.env" 2>/dev/null | tail -1)"
port="${port:-8001}"
for _ in {1..30}; do
  if curl -fsS "http://127.0.0.1:${port}/health" >/dev/null; then
    echo "Update complete: $(git_as_owner rev-parse --short HEAD)"
    exit 0
  fi
  sleep 1
done
systemctl status "$SERVICE_NAME" --no-pager -l || true
echo "Update installed, but health verification failed." >&2
echo "Previous commit: $old_commit; backup: $backup_dir" >&2
exit 1
