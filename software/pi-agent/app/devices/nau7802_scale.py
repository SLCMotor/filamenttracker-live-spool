import statistics
import threading
import time

from app.devices.base import ScaleDevice


class NAU7802Scale(ScaleDevice):
    """NAU7802 scale backend using Blinka I2C on Raspberry Pi."""

    def __init__(
        self,
        address: int = 0x2A,
        channel: int = 1,
        gain: int = 128,
        poll_rate: int = 10,
        samples: int = 15,
        stable_stddev: float = 1000.0,
    ):
        self.address = address
        self.channel = channel
        self.gain = gain
        self.poll_rate = poll_rate
        self.samples = max(1, samples)
        self.stable_stddev = stable_stddev
        self._connected = False
        self._last_error: str | None = None
        self._sensor = None
        self._lock = threading.RLock()
        self._last_read_at = 0.0
        self._last_stable = False
        self._last_stddev = 0.0
        self._cached_raw = 0.0
        self._stop_sampler = threading.Event()
        self._init_sensor()
        self._start_sampler()

    def is_connected(self) -> bool:
        return self._connected

    def is_stable(self) -> bool:
        if not self._connected:
            return False

        with self._lock:
            return self._last_stable

    def get_raw_weight_grams(self) -> float:
        with self._lock:
            return self._cached_raw

    def get_fresh_raw_weight_grams(self) -> float:
        with self._lock:
            readings = self._read_samples(self.samples)
            if not readings:
                self._last_stable = False
                self._last_stddev = 0.0
                self._last_read_at = time.monotonic()
                return 0.0

            self._last_stddev = statistics.pstdev(readings) if len(readings) > 1 else 0.0
            self._last_stable = self._last_stddev < self.stable_stddev
            self._last_read_at = time.monotonic()
            self._cached_raw = float(self._trimmed_mean(readings))
            return self._cached_raw

    def set_mock_raw_weight_grams(self, weight_grams: float) -> None:
        raise RuntimeError("Mock weight is not available for NAU7802 scale backend.")

    def _init_sensor(self) -> None:
        try:
            import board
            from cedargrove_nau7802 import NAU7802

            active_channels = 2 if self.channel == 2 else 1
            sensor = NAU7802(
                board.I2C(),
                address=self.address,
                active_channels=active_channels,
            )
            sensor.enable(True)
            sensor.channel = self.channel
            sensor.gain = self.gain
            sensor.poll_rate = self.poll_rate

            self._sensor = sensor
            self._connected = True
            self._last_error = None
        except Exception as exc:
            self._sensor = None
            self._connected = False
            self._last_error = str(exc)

    def _start_sampler(self) -> None:
        if not self._connected:
            return

        thread = threading.Thread(
            target=self._sample_loop,
            name="nau7802-scale-sampler",
            daemon=True,
        )
        thread.start()

    def _sample_loop(self) -> None:
        while not self._stop_sampler.is_set():
            self.get_fresh_raw_weight_grams()
            time.sleep(0.25)

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
        if not self._connected or self._sensor is None:
            return None

        if not self._wait_ready(timeout_seconds=1.0):
            return None

        try:
            return int(self._sensor.read())
        except Exception as exc:
            self._last_error = str(exc)
            return None

    def _wait_ready(self, timeout_seconds: float) -> bool:
        if self._sensor is None:
            return False

        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            try:
                if self._sensor.available():
                    return True
            except Exception as exc:
                self._last_error = str(exc)
                return False
            time.sleep(0.01)
        return False
