from app.core.config import config
from app.devices.hx711_scale import HX711Scale
from app.devices.mock_nfc import MockNFCDevice
from app.devices.mock_scale import MockScale


class DeviceManager:
    """Central manager for all hardware devices."""

    def __init__(self):
        self.device_mode = config.device_mode
        self.scale_backend = config.scale_backend
        self.scale = self._load_scale()
        self.nfc = self._load_nfc()

    def _load_scale(self):
        if self.scale_backend == "mock":
            return MockScale()
        if self.scale_backend == "hx711":
            return HX711Scale(
                data_pin=config.hx711_data_pin,
                clock_pin=config.hx711_clock_pin,
                gain=config.hx711_gain,
                samples=config.hx711_samples,
            )

        raise RuntimeError(
            f"Unsupported scale backend: {self.scale_backend}"
        )

    def _load_nfc(self):
        if self.device_mode == "mock":
            return MockNFCDevice()

        raise RuntimeError(
            f"Unsupported NFC device mode: {self.device_mode}"
        )


devices = DeviceManager()
