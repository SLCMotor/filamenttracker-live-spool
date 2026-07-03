import statistics
import threading
import time

from app.devices.base import ScaleDevice


class HX711Scale(ScaleDevice):
    """HX711 scale backend using Raspberry Pi BCM GPIO pin numbers."""

    def __init__(
        self,
        data_pin: int,
        clock_pin: int,
        gain: int = 128,
        samples: int = 5,
    ):
        self.data_pin = data_pin
        self.clock_pin = clock_pin
        self.gain = gain
        self.samples = max(1, samples)
        self._connected = False
        self._last_error: str | None = None
        self._data = None
        self._clock = None
        self._lock = threading.RLock()
        self._last_read_at = 0.0
        self._last_stable = False
        self._last_stddev = 0.0
        self._gain_pulses = self._resolve_gain_pulses(gain)
        self._init_gpio()

    def is_connected(self) -> bool:
        return self._connected

    def is_stable(self) -> bool:
        if not self._connected:
            return False

        if time.monotonic() - self._last_read_at < 2.0:
            return self._last_stable

        self.get_raw_weight_grams()
        return self._last_stable

    def get_raw_weight_grams(self) -> float:
        with self._lock:
            readings = self._read_samples(self.samples)
            if not readings:
                self._last_stable = False
                self._last_stddev = 0.0
                self._last_read_at = time.monotonic()
                return 0.0

            self._last_stddev = statistics.pstdev(readings) if len(readings) > 1 else 0.0
            self._last_stable = self._last_stddev < 1000
            self._last_read_at = time.monotonic()

            return float(self._trimmed_mean(readings))

    def set_mock_raw_weight_grams(self, weight_grams: float) -> None:
        raise RuntimeError("Mock weight is not available for HX711 scale backend.")

    def _init_gpio(self) -> None:
        try:
            from gpiozero import DigitalInputDevice, DigitalOutputDevice

            self._data = DigitalInputDevice(self.data_pin, pull_up=False)
            self._clock = DigitalOutputDevice(self.clock_pin, initial_value=False)
            self._connected = True
            self._last_error = None
        except Exception as exc:
            self._connected = False
            self._last_error = str(exc)

    def _read_samples(self, count: int) -> list[int]:
        readings: list[int] = []
        for _ in range(max(1, count)):
            value = self._read_raw_once()
            if value is not None:
                readings.append(value)
        return readings

    @staticmethod
    def _trimmed_mean(readings: list[int]) -> float:
        if len(readings) < 5:
            return float(statistics.median(readings))

        sorted_readings = sorted(readings)
        trim_count = max(1, len(sorted_readings) // 5)
        trimmed = sorted_readings[trim_count:-trim_count]
        if not trimmed:
            trimmed = sorted_readings

        return float(statistics.mean(trimmed))

    def _read_raw_once(self) -> int | None:
        if not self._connected or self._data is None or self._clock is None:
            return None

        if not self._wait_ready(timeout_seconds=1.0):
            return None

        value = 0
        for _ in range(24):
            self._clock.on()
            value = (value << 1) | int(self._data.value)
            self._clock.off()

        for _ in range(self._gain_pulses):
            self._clock.on()
            self._clock.off()

        if value & 0x800000:
            value -= 0x1000000

        return value

    def _wait_ready(self, timeout_seconds: float) -> bool:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            if self._data is not None and not self._data.value:
                return True
            time.sleep(0.001)
        return False

    @staticmethod
    def _resolve_gain_pulses(gain: int) -> int:
        if gain == 128:
            return 1
        if gain == 32:
            return 2
        if gain == 64:
            return 3
        return 1
