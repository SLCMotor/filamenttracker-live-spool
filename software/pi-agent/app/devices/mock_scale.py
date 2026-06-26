import random

from app.devices.base import ScaleDevice


class MockScale(ScaleDevice):
    """Mock scale used for development without real hardware."""

    def __init__(self):
        self._connected = True
        self._weight = 850.0

    def is_connected(self) -> bool:
        return self._connected

    def get_weight_grams(self) -> float:
        # Simulate slight fluctuations in weight
        self._weight += random.uniform(-0.5, 0.5)
        return round(self._weight, 2)

    def tare(self) -> bool:
        self._weight = 0.0
        return True
