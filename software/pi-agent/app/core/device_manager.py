from app.core.config import config
from app.devices.mock_nfc import MockNFCDevice
from app.devices.mock_scale import MockScale


class DeviceManager:
    """Central manager for all hardware devices."""

    def __init__(self):
        self.device_mode = config.device_mode
        self.scale = self._load_scale()
        self.nfc = self._load_nfc()

    def _load_scale(self):
        if self.device_mode == "mock":
            return MockScale()

        raise RuntimeError(
            f"Unsupported scale device mode: {self.device_mode}"
        )

    def _load_nfc(self):
        if self.device_mode == "mock":
            return MockNFCDevice()

        raise RuntimeError(
            f"Unsupported NFC device mode: {self.device_mode}"
        )


devices = DeviceManager()
