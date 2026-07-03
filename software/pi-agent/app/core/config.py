from pathlib import Path

import yaml

CONFIG_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "config"
    / "config.yaml"
)


def _int_config(value, default: int) -> int:
    if value is None:
        return default
    if isinstance(value, str):
        return int(value, 0)
    return int(value)


class Config:
    def __init__(self):
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            self.data = yaml.safe_load(file)

    @property
    def app_name(self):
        return self.data["app"]["name"]

    @property
    def version(self):
        return self.data["app"]["version"]

    @property
    def environment(self):
        return self.data["app"]["environment"]

    @property
    def host(self):
        return self.data["server"]["host"]

    @property
    def port(self):
        return self.data["server"]["port"]

    @property
    def device_name(self):
        return self.data["device"]["name"]

    @property
    def device_location(self):
        return self.data["device"].get("location", "")

    @property
    def device_mode(self):
        return self.data.get("hardware", {}).get("device_mode", "mock")

    @property
    def scale_enabled(self):
        return bool(self.data.get("scale", {}).get("enabled", True))

    @property
    def scale_backend(self):
        scale = self.data.get("scale", {})
        if bool(scale.get("mock", False)):
            return "mock"
        return str(scale.get("backend", "mock")).strip().lower()

    @property
    def hx711_data_pin(self):
        return int(self.data.get("scale", {}).get("hx711", {}).get("data_pin", 5))

    @property
    def hx711_clock_pin(self):
        return int(self.data.get("scale", {}).get("hx711", {}).get("clock_pin", 6))

    @property
    def hx711_gain(self):
        return int(self.data.get("scale", {}).get("hx711", {}).get("gain", 128))

    @property
    def hx711_samples(self):
        return int(self.data.get("scale", {}).get("hx711", {}).get("samples", 5))

    @property
    def nau7802_address(self):
        return _int_config(
            self.data.get("scale", {}).get("nau7802", {}).get("address"),
            0x2A,
        )

    @property
    def nau7802_channel(self):
        return int(self.data.get("scale", {}).get("nau7802", {}).get("channel", 1))

    @property
    def nau7802_gain(self):
        return int(self.data.get("scale", {}).get("nau7802", {}).get("gain", 128))

    @property
    def nau7802_poll_rate(self):
        return int(self.data.get("scale", {}).get("nau7802", {}).get("poll_rate", 10))

    @property
    def nau7802_samples(self):
        return int(self.data.get("scale", {}).get("nau7802", {}).get("samples", 15))

    @property
    def nau7802_stable_stddev(self):
        return float(
            self.data.get("scale", {}).get("nau7802", {}).get("stable_stddev", 1000)
        )

    @property
    def nfc_enabled(self):
        return bool(self.data.get("nfc", {}).get("enabled", True))


config = Config()
