from pathlib import Path
import platform
import re
import socket
import subprocess

import fastapi
from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates

from app.core.config import config

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def read_file(path: str, fallback: str = "Unknown") -> str:
    try:
        value = Path(path).read_text().replace("\x00", "").strip()
        return value if value else fallback
    except Exception:
        return fallback


def short_pi_model() -> str:
    model = read_file("/proc/device-tree/model")
    return re.sub(r"\s+Rev\s+.*$", "", model)


def command_output(command: list[str], fallback: str = "Unknown") -> str:
    try:
        value = subprocess.check_output(
            command,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2,
        ).strip()
        return value if value else fallback
    except Exception:
        return fallback


def command_success(command: list[str]) -> bool:
    try:
        subprocess.check_output(
            command,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2,
        )
        return True
    except Exception:
        return False


def os_pretty_name() -> str:
    try:
        for line in Path("/etc/os-release").read_text().splitlines():
            if line.startswith("PRETTY_NAME="):
                return line.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass

    return "Unknown"


def ip_for_interface(interface: str) -> str:
    return command_output(["ip", "-4", "addr", "show", interface], "")


def interface_status(interface: str) -> str:
    state_path = f"/sys/class/net/{interface}/operstate"
    state = read_file(state_path, "down").lower()
    return "Connected" if state == "up" else "Disconnected"


def primary_ip_address() -> str:
    output = command_output(["hostname", "-I"], "")
    if not output:
        return "Unavailable"

    addresses = [item for item in output.split() if item]
    return addresses[0] if addresses else "Unavailable"


def display_resolution() -> str:
    output = command_output(["wlr-randr"], "")
    match = re.search(r"current\s+(\d+)\s*x\s*(\d+)", output)
    if match:
        return f"{match.group(1)} × {match.group(2)}"

    output = command_output(["xrandr", "--current"], "")
    match = re.search(r"\b(\d+)x(\d+)\+\d+\+\d+", output)
    if match:
        return f"{match.group(1)} × {match.group(2)}"

    return "1024 × 600"


def cursor_hide_status() -> str:
    if command_success(["pgrep", "-x", "unclutter"]):
        return "Enabled"

    return "Not Running"


def kiosk_mode_status() -> str:
    chromium_running = command_success(["pgrep", "-f", "chromium"])
    kiosk_configured = Path("/home/livespool/.xinitrc").exists()

    if chromium_running:
        return "Enabled"

    if kiosk_configured:
        return "Configured"

    return "Not Running"


def screen_blanking_status() -> str:
    xset_output = command_output(["xset", "q"], "")

    if "timeout:  0" in xset_output and "DPMS is Disabled" in xset_output:
        return "Disabled"

    if xset_output:
        return "Enabled"

    return "Unknown"


def brightness_status() -> str:
    backlight_root = Path("/sys/class/backlight")

    try:
        devices = [item for item in backlight_root.iterdir() if item.is_dir()]
    except Exception:
        return "Unsupported"

    if not devices:
        return "Unsupported"

    device = devices[0]
    brightness = read_file(str(device / "brightness"), "")
    max_brightness = read_file(str(device / "max_brightness"), "")

    try:
        percent = round((int(brightness) / int(max_brightness)) * 100)
        return f"{percent}%"
    except Exception:
        return "Detected"


def network_info() -> dict:
    wlan_raw = ip_for_interface("wlan0")
    eth_raw = ip_for_interface("eth0")

    wifi_connected = "inet " in wlan_raw and interface_status("wlan0") == "Connected"
    ethernet_connected = "inet " in eth_raw and interface_status("eth0") == "Connected"

    return {
        "status": "Ready" if wifi_connected or ethernet_connected else "Offline",
        "hostname": socket.gethostname(),
        "ip_address": primary_ip_address(),
        "wifi_status": "Connected" if wifi_connected else "Disconnected",
        "ethernet_status": "Connected" if ethernet_connected else "Disconnected",
        "api_port": "8001",
        "api_status": "Ready",
    }


def display_info() -> dict:
    return {
        "touchscreen": "7 inch ELECROW",
        "resolution": display_resolution(),
        "kiosk_mode": kiosk_mode_status(),
        "cursor_hide": cursor_hide_status(),
        "screen_blanking": screen_blanking_status(),
        "brightness": brightness_status(),
    }


def about_info() -> dict:
    return {
        "project": "FilamentTracker Live Spool",
        "version": f"v{config.version}",
        "pi_model": short_pi_model(),
        "os_version": os_pretty_name(),
        "python_version": platform.python_version(),
        "fastapi_version": fastapi.__version__,
        "git_commit": command_output(["git", "rev-parse", "--short", "HEAD"], "Local Build"),
        "build_status": "Development",
    }


SETTINGS_SECTIONS = {
    "general": {
        "title": "System",
        "subtitle": "Application and Raspberry Pi power controls",
        "items": [
            ("Restart Application", "Available soon"),
            ("Reboot Raspberry Pi", "Available soon"),
            ("Shutdown Raspberry Pi", "Available soon"),
        ],
    },
    "scale": {
        "title": "Scale",
        "subtitle": "Calibration entry point and scale status",
        "items": [
            ("Calibration Wizard", "Available"),
            ("Scale Status", "Use dashboard live status"),
        ],
    },
    "nfc": {
        "title": "NFC",
        "subtitle": "Reader management and tag operations",
        "items": [],
    },
    "display": {
        "title": "Display",
        "subtitle": "Kiosk, touchscreen, brightness, and screen behavior",
        "items": [
            ("Touchscreen", "7 inch ELECROW"),
            ("Kiosk Mode", "Live"),
            ("Cursor Hide", "Live"),
            ("Screen Blanking", "Live"),
            ("Brightness", "Live"),
        ],
    },
    "network": {
        "title": "Network",
        "subtitle": "Local API, hostname, and connection status",
        "items": [],
    },
    "about": {
        "title": "About",
        "subtitle": "Build, device, and project information",
        "items": [],
    },
}


def template_context(request: Request, extra: dict | None = None):
    context = {
        "request": request,
        "app_name": config.app_name,
        "device_name": config.device_name,
        "version": config.version,
        "environment": config.environment,
        "active_page": "settings",
    }

    if extra:
        context.update(extra)

    return context


def settings_template_for(section_key: str) -> str:
    section_template = Path("templates") / f"settings_{section_key}.html"

    if section_template.exists():
        return f"settings_{section_key}.html"

    return "settings_section.html"


@router.get("/settings")
def settings_page(request: Request):
    return templates.TemplateResponse(
        request,
        "settings.html",
        template_context(request, {"sections": SETTINGS_SECTIONS}),
    )


@router.get("/settings/{section_key}")
def settings_section_page(request: Request, section_key: str):
    section = SETTINGS_SECTIONS.get(section_key)

    if not section:
        raise HTTPException(status_code=404, detail="Settings section not found")

    extra = {
        "section_key": section_key,
        "section": section,
    }

    if section_key == "about":
        extra["about"] = about_info()

    if section_key == "network":
        extra["network"] = network_info()

    if section_key == "display":
        extra["display"] = display_info()

    if section_key == "scale":
        extra["scale_backend"] = config.scale_backend.upper()

    return templates.TemplateResponse(
        request,
        settings_template_for(section_key),
        template_context(request, extra),
    )
