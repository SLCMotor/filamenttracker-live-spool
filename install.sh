#!/usr/bin/env bash
set -euo pipefail

APP_NAME="FilamentTracker Live Spool"
SERVICE_NAME="filamenttracker-live-spool"
APP_PORT="8001"
APP_USER="${SUDO_USER:-$(whoami)}"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PI_AGENT_DIR="$APP_DIR/software/pi-agent"
VENV_DIR="$APP_DIR/.venv"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

echo "======================================"
echo " $APP_NAME Installer"
echo "======================================"
echo

if [[ ! -d "$PI_AGENT_DIR/app" ]]; then
  echo "ERROR: Could not find pi-agent app directory:"
  echo "$PI_AGENT_DIR/app"
  exit 1
fi

echo "Installing system packages..."
sudo apt update
sudo apt install -y git python3-venv python3-pip curl

echo
echo "Creating Python virtual environment..."
python3 -m venv "$VENV_DIR"

echo
echo "Installing Python packages..."
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$PI_AGENT_DIR/requirements.txt"

echo
echo "Installing systemd service..."
sudo tee "$SERVICE_FILE" > /dev/null << SERVICEEOF
[Unit]
Description=FilamentTracker Live Spool Pi Agent
After=network-online.target
Wants=network-online.target

[Service]
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$PI_AGENT_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/uvicorn app.main:app --host 0.0.0.0 --port $APP_PORT
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICEEOF

echo
echo "Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo
echo "Checking service status..."
sleep 2
sudo systemctl status "$SERVICE_NAME" --no-pager -l || true

echo
echo "Testing local API..."
if curl -fsS "http://127.0.0.1:${APP_PORT}/status" > /dev/null; then
  echo "API is responding locally."
else
  echo "WARNING: API did not respond locally yet."
fi

IP_ADDRESS="$(hostname -I | awk '{print $1}')"

echo
echo "======================================"
echo " Installation Complete"
echo "======================================"
echo "Service: $SERVICE_NAME"
echo "Port:    $APP_PORT"
echo "Status:  sudo systemctl status $SERVICE_NAME --no-pager -l"
echo
echo "API:"
echo "http://${IP_ADDRESS}:${APP_PORT}/status"
echo
