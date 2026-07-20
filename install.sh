#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="live-spool-agent"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PI_AGENT_DIR="$APP_DIR/software/pi-agent"
VENV_DIR="$PI_AGENT_DIR/.venv"
CONFIG_DIR="/etc/filamenttracker-live-spool"
DATA_DIR="/var/lib/filamenttracker-live-spool"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
SUDOERS_FILE="/etc/sudoers.d/filamenttracker-live-spool"
APP_USER="${SUDO_USER:-}"
ALLOW_UNSUPPORTED=false
INSTALL_KIOSK=true
SCALE_BACKEND=""

usage() {
  echo "Usage: sudo ./install.sh [--user USER] [--scale-backend mock|nau7802|hx711] [--no-kiosk] [--allow-unsupported]"
}

while (($#)); do
  case "$1" in
    --user) APP_USER="${2:?--user requires a username}"; shift 2 ;;
    --scale-backend) SCALE_BACKEND="${2:?--scale-backend requires a value}"; shift 2 ;;
    --no-kiosk) INSTALL_KIOSK=false; shift ;;
    --allow-unsupported) ALLOW_UNSUPPORTED=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ $EUID -ne 0 ]]; then
  echo "Run this installer with sudo: sudo ./install.sh" >&2
  exit 1
fi
if [[ -z "$APP_USER" || "$APP_USER" == root ]] || ! id "$APP_USER" >/dev/null 2>&1; then
  echo "Could not determine the non-root appliance user; pass --user USER." >&2
  exit 1
fi
if [[ ! -f "$PI_AGENT_DIR/requirements.txt" ]]; then
  echo "Run install.sh from a complete FilamentTracker Live Spool checkout." >&2
  exit 1
fi

ARCH="$(dpkg --print-architecture 2>/dev/null || uname -m)"
PI_MODEL="$(tr -d '\0' </proc/device-tree/model 2>/dev/null || true)"
if [[ "$PI_MODEL" != Raspberry\ Pi* || "$ARCH" != arm64 ]]; then
  if [[ "$ALLOW_UNSUPPORTED" != true ]]; then
    echo "Supported appliance platform: 64-bit Raspberry Pi OS on Raspberry Pi 4 or 5." >&2
    echo "Detected: ${PI_MODEL:-non-Raspberry Pi}, architecture $ARCH" >&2
    echo "Use --allow-unsupported only for development or testing." >&2
    exit 1
  fi
  echo "WARNING: continuing on unsupported platform: ${PI_MODEL:-unknown} ($ARCH)"
fi

APP_GROUP="$(id -gn "$APP_USER")"
echo "Installing operating-system packages..."
apt-get update
packages=(git python3 python3-pip python3-venv curl i2c-tools)
if [[ "$INSTALL_KIOSK" == true ]]; then
  packages+=(chromium unclutter)
fi
DEBIAN_FRONTEND=noninteractive apt-get install -y "${packages[@]}"

if command -v raspi-config >/dev/null 2>&1; then
  raspi-config nonint do_i2c 0
else
  echo "WARNING: raspi-config not found; verify that I2C is enabled."
fi

install -d -m 0755 "$CONFIG_DIR"
install -d -o "$APP_USER" -g "$APP_GROUP" -m 0750 "$DATA_DIR"
if [[ ! -f "$CONFIG_DIR/config.yaml" ]]; then
  install -m 0644 "$PI_AGENT_DIR/config/config.yaml" "$CONFIG_DIR/config.yaml"
  sed -i 's/environment: "development"/environment: "production"/' "$CONFIG_DIR/config.yaml"
  sed -i 's@data_dir: "data"@data_dir: "/var/lib/filamenttracker-live-spool"@' "$CONFIG_DIR/config.yaml"
  if [[ -z "$SCALE_BACKEND" && -t 0 ]]; then
    read -r -p "Scale backend [mock/nau7802/hx711] (mock): " SCALE_BACKEND
  fi
  SCALE_BACKEND="${SCALE_BACKEND:-mock}"
  case "$SCALE_BACKEND" in
    mock|nau7802|hx711) ;;
    *) echo "Invalid scale backend: $SCALE_BACKEND" >&2; exit 2 ;;
  esac
  if [[ "$SCALE_BACKEND" != mock ]]; then
    sed -i "s/device_mode: \"mock\"/device_mode: \"real\"/; s/backend: \"mock\"/backend: \"$SCALE_BACKEND\"/; s/mock: true/mock: false/g" "$CONFIG_DIR/config.yaml"
  fi
  echo "Created $CONFIG_DIR/config.yaml (scale backend: $SCALE_BACKEND)."
else
  echo "Preserving existing $CONFIG_DIR/config.yaml"
fi
if [[ ! -f "$CONFIG_DIR/live-spool.env" ]]; then
  install -m 0644 "$PI_AGENT_DIR/config/live-spool.env.example" "$CONFIG_DIR/live-spool.env"
  sed -i 's/LIVE_SPOOL_SYSTEM_CONTROLS_ENABLED=false/LIVE_SPOOL_SYSTEM_CONTROLS_ENABLED=true/' "$CONFIG_DIR/live-spool.env"
else
  echo "Preserving existing $CONFIG_DIR/live-spool.env"
fi

LEGACY_CALIBRATION="$PI_AGENT_DIR/data/calibration.json"
if [[ -f "$LEGACY_CALIBRATION" && ! -f "$DATA_DIR/calibration.json" ]]; then
  install -o "$APP_USER" -g "$APP_GROUP" -m 0640 "$LEGACY_CALIBRATION" "$DATA_DIR/calibration.json"
  echo "Migrated existing calibration to $DATA_DIR/calibration.json"
elif [[ -f "$DATA_DIR/calibration.json" ]]; then
  echo "Preserving existing calibration."
fi

python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$PI_AGENT_DIR/requirements.txt"
chown -R "$APP_USER:$APP_GROUP" "$VENV_DIR"

supplementary=()
for group in i2c gpio spi; do
  if getent group "$group" >/dev/null; then
    usermod -a -G "$group" "$APP_USER"
    supplementary+=("$group")
  fi
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
if ! visudo -cf "$SUDOERS_FILE" >/dev/null; then
  rm -f "$SUDOERS_FILE"
  echo "Generated system-control authorization is invalid." >&2
  exit 1
fi

if [[ "$INSTALL_KIOSK" == true ]]; then
  USER_HOME="$(getent passwd "$APP_USER" | cut -d: -f6)"
  AUTOSTART_DIR="$USER_HOME/.config/autostart"
  install -d -o "$APP_USER" -g "$APP_GROUP" -m 0755 "$AUTOSTART_DIR"
  sed "s|@KIOSK_SCRIPT@|$PI_AGENT_DIR/scripts/start-dashboard-kiosk.sh|g" \
    "$APP_DIR/deploy/live-spool-kiosk.desktop" >"$AUTOSTART_DIR/live-spool-kiosk.desktop"
  chown "$APP_USER:$APP_GROUP" "$AUTOSTART_DIR/live-spool-kiosk.desktop"
fi

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

health_url="http://127.0.0.1:8001/health"
for _ in {1..30}; do
  if curl -fsS "$health_url" >/dev/null; then
    address="$(hostname -I 2>/dev/null | awk '{print $1}')"
    echo "Live Spool is running: http://${address:-localhost}:8001/dashboard"
    echo "Configuration: $CONFIG_DIR/config.yaml"
    echo "Runtime data:  $DATA_DIR"
    echo "Select nau7802 or hx711 in the configuration, then restart the service."
    exit 0
  fi
  sleep 1
done

systemctl status "$SERVICE_NAME" --no-pager -l || true
echo "Installation finished, but the API health check failed." >&2
exit 1
