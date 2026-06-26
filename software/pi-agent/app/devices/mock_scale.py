from app.devices.base import ScaleDevice


class MockScale(ScaleDevice):
    """Mock scale used for development without real hardware."""

    def __init__(self):
        self._connected = True
        self._stable = True
        self._raw_weight_grams = 850.47

    def is_connected(self) -> bool:
        return self._connected

    def is_stable(self) -> bool:
        return self._stable

    def get_raw_weight_grams(self) -> float:
        return self._raw_weight_grams

    def set_mock_raw_weight_grams(self, weight_grams: float) -> None:
        self._raw_weight_grams = weight_grams
