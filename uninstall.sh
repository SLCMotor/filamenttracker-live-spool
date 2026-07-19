#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="live-spool-agent"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="/etc/filamenttracker-live-spool"
DATA_DIR="/var/lib/filamenttracker-live-spool"
REMOVE_CONFIG=false
REMOVE_DATA=false
REMOVE_VENV=false
YES=false

usage() {
  echo "Usage: sudo ./uninstall.sh [--remove-config] [--remove-data] [--remove-venv] [--yes]"
  echo "Configuration and calibration/runtime data are preserved by default."
}
while (($#)); do
  case "$1" in
    --remove-config) REMOVE_CONFIG=true ;;
    --remove-data) REMOVE_DATA=true ;;
    --remove-venv) REMOVE_VENV=true ;;
    --yes) YES=true ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done
if [[ $EUID -ne 0 ]]; then
  echo "Run with sudo: sudo ./uninstall.sh" >&2
  exit 1
fi
if [[ "$REMOVE_CONFIG" == true || "$REMOVE_DATA" == true ]]; then
  if [[ "$YES" != true ]]; then
    if [[ ! -t 0 ]]; then
      echo "Data removal requires an interactive confirmation or --yes." >&2
      exit 1
    fi
    echo "Requested removal: config=$REMOVE_CONFIG runtime/calibration=$REMOVE_DATA"
    read -r -p "Type REMOVE to permanently delete the selected data: " answer
    [[ "$answer" == REMOVE ]] || { echo "Canceled."; exit 1; }
  fi
fi

systemctl disable --now "$SERVICE_NAME" 2>/dev/null || true
rm -f "/etc/systemd/system/${SERVICE_NAME}.service"
systemctl daemon-reload

kiosk_user="${SUDO_USER:-}"
if [[ -n "$kiosk_user" ]] && id "$kiosk_user" >/dev/null 2>&1; then
  kiosk_home="$(getent passwd "$kiosk_user" | cut -d: -f6)"
  rm -f "$kiosk_home/.config/autostart/live-spool-kiosk.desktop"
fi
[[ "$REMOVE_VENV" == true ]] && rm -rf -- "$APP_DIR/software/pi-agent/.venv"
[[ "$REMOVE_CONFIG" == true ]] && rm -rf -- "$CONFIG_DIR"
[[ "$REMOVE_DATA" == true ]] && rm -rf -- "$DATA_DIR"

echo "Live Spool service removed."
[[ "$REMOVE_CONFIG" != true ]] && echo "Preserved configuration: $CONFIG_DIR"
[[ "$REMOVE_DATA" != true ]] && echo "Preserved calibration/runtime data: $DATA_DIR"
echo "The Git checkout and operating-system packages were not removed."
