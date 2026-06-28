#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="filamenttracker-live-spool"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PI_AGENT_DIR="$APP_DIR/software/pi-agent"
VENV_DIR="$APP_DIR/.venv"
APP_PORT="8001"

echo "======================================"
echo " FilamentTracker Live Spool Updater"
echo "======================================"
echo

cd "$APP_DIR"

echo "Pulling latest code..."
git pull

echo
echo "Installing/updating Python packages..."
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$PI_AGENT_DIR/requirements.txt"

echo
echo "Restarting service..."
sudo systemctl restart "$SERVICE_NAME"

echo
echo "Testing API..."
sleep 2
curl -fsS "http://127.0.0.1:${APP_PORT}/status"
echo

echo
echo "Update complete."
