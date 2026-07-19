import os
from pathlib import Path
from typing import Any

import yaml

APP_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = APP_ROOT / "config" / "config.yaml"
SYSTEM_CONFIG_PATH = Path("/etc/filamenttracker-live-spool/config.yaml")


def _env(name: str) -> str | None:
    value = os.getenv(f"LIVE_SPOOL_{name}")
    return value.strip() if value and value.strip() else None


def _bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _int(value: Any, default: int) -> int:
    if value is None:
        return default
    return int(value, 0) if isinstance(value, str) else int(value)


class Config:
    """YAML configuration with LIVE_SPOOL_* environment overrides."""

    def __init__(self, path: Path | None = None):
        configured = _env("CONFIG_FILE")
        if path is not None:
            self.path = path
        elif configured:
            self.path = Path(configured)
        elif SYSTEM_CONFIG_PATH.exists():
            self.path = SYSTEM_CONFIG_PATH
        else:
            self.path = DEFAULT_CONFIG_PATH
        with self.path.open("r", encoding="utf-8") as file:
            self.data = yaml.safe_load(file) or {}

    def _get(self, *keys: str, default: Any = None) -> Any:
        value: Any = self.data
        for key in keys:
            if not isinstance(value, dict):
                return default
            value = value.get(key, default)
        return value

    @property
    def app_name(self):
        return str(self._get("app", "name", default="FilamentTracker Live Spool"))

    @property
    def version(self):
        return str(self._get("app", "version", default="0.1.0"))

    @property
    def environment(self):
        return _env("ENVIRONMENT") or str(self._get("app", "environment", default="production"))

    @property
    def development_mode(self):
        return _bool(_env("DEVELOPMENT_MODE"), self.environment == "development")

    @property
    def host(self):
        return _env("API_HOST") or str(self._get("server", "host", default="0.0.0.0"))

    @property
    def port(self):
        return _int(_env("API_PORT") or self._get("server", "port"), 8001)

    @property
    def log_level(self):
        return (_env("LOG_LEVEL") or str(self._get("server", "log_level", default="info"))).lower()

    @property
    def device_name(self):
        return _env("DEVICE_NAME") or str(self._get("device", "name", default="Live Spool"))

    @property
    def device_location(self):
        return _env("DEVICE_LOCATION") or str(self._get("device", "location", default=""))

    @property
    def device_mode(self):
        if _bool(_env("MOCK_HARDWARE"), False):
            return "mock"
        return str(self._get("hardware", "device_mode", default="mock")).lower()

    @property
    def mock_hardware(self):
        return self.device_mode == "mock"

    @property
    def data_dir(self):
        value = _env("DATA_DIR") or self._get("runtime", "data_dir")
        path = Path(value) if value else APP_ROOT / "data"
        return path if path.is_absolute() else APP_ROOT / path

    @property
    def scale_enabled(self):
        return _bool(self._get("scale", "enabled"), True)

    @property
    def scale_backend(self):
        backend = _env("SCALE_BACKEND") or self._get("scale", "backend", default="mock")
        if self.mock_hardware or _bool(self._get("scale", "mock"), False):
            return "mock"
        return str(backend).strip().lower()

    @property
    def hx711_data_pin(self):
        return _int(_env("HX711_DATA_PIN") or self._get("scale", "hx711", "data_pin"), 5)

    @property
    def hx711_clock_pin(self):
        return _int(_env("HX711_CLOCK_PIN") or self._get("scale", "hx711", "clock_pin"), 6)

    @property
    def hx711_gain(self):
        return _int(self._get("scale", "hx711", "gain"), 128)

    @property
    def hx711_samples(self):
        return _int(self._get("scale", "hx711", "samples"), 15)

    @property
    def nau7802_address(self):
        return _int(_env("NAU7802_ADDRESS") or self._get("scale", "nau7802", "address"), 0x2A)

    @property
    def nau7802_channel(self):
        return _int(self._get("scale", "nau7802", "channel"), 1)

    @property
    def nau7802_gain(self):
        return _int(self._get("scale", "nau7802", "gain"), 128)

    @property
    def nau7802_poll_rate(self):
        return _int(self._get("scale", "nau7802", "poll_rate"), 10)

    @property
    def nau7802_samples(self):
        return _int(self._get("scale", "nau7802", "samples"), 15)

    @property
    def nau7802_stable_stddev(self):
        return float(self._get("scale", "nau7802", "stable_stddev", default=1000))

    @property
    def nfc_enabled(self):
        return _bool(self._get("nfc", "enabled"), True)

    @property
    def nfc_mock(self):
        return self.mock_hardware or _bool(self._get("nfc", "mock"), False)

    @property
    def pn532_address(self):
        return _int(_env("PN532_ADDRESS") or self._get("nfc", "pn532", "address"), 0x24)

    @property
    def system_controls_enabled(self):
        default = _bool(self._get("admin", "system_controls_enabled"), False)
        return _bool(_env("SYSTEM_CONTROLS_ENABLED"), default)


config = Config()
