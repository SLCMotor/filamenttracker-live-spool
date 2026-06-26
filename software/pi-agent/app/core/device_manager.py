from app.devices.mock_scale import MockScale


class DeviceManager:
    """Central manager for all hardware devices."""

    def __init__(self):
        self.scale = MockScale()


devices = DeviceManager()
