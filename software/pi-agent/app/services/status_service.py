from pathlib import Path

from app.core.config import config
from app.services.scale_service import scale_service
from app.services.spool_service import get_current_spool


def get_cpu_temp_c() -> float | None:
    temp_path = Path("/sys/class/thermal/thermal_zone0/temp")

    try:
        raw_value = temp_path.read_text().strip()
        return round(int(raw_value) / 1000, 1)
    except Exception:
        return None


def get_uptime() -> str | None:
    uptime_path = Path("/proc/uptime")

    try:
        raw_seconds = float(uptime_path.read_text().split()[0])
    except Exception:
        return None

    total_minutes = int(raw_seconds // 60)
    days = total_minutes // 1440
    hours = (total_minutes % 1440) // 60
    minutes = total_minutes % 60

    if days:
        return f"{days}d {hours}h"

    if hours:
        return f"{hours}h {minutes}m"

    return f"{minutes}m"


def get_status() -> dict:
    spool_state = get_current_spool()
    nfc = spool_state.get("nfc") or {
        "connected": False,
        "tagPresent": False,
        "tagId": None,
        "data": None,
        "tag": None,
        "error": "Monitor warming up",
    }

    return {
        "status": "online",
        "deviceName": config.device_name,
        "version": config.version,
        "scale": scale_service.get_weight(),
        "nfc": nfc,
        "cpuTempC": get_cpu_temp_c(),
        "uptime": get_uptime(),
    }
