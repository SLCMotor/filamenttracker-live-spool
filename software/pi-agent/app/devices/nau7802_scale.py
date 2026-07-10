import statistics
import threading
import time

from app.devices.base import ScaleDevice


NAU7802_PU_CTRL = 0x00
NAU7802_CTRL1 = 0x01
NAU7802_CTRL2 = 0x02
NAU7802_ADCO_B2 = 0x12
NAU7802_ADC = 0x15
NAU7802_PGA = 0x1B
NAU7802_PGA_PWR = 0x1C
NAU7802_DEVICE_REV = 0x1F

PU_CTRL_RR = 0
PU_CTRL_PUD = 1
PU_CTRL_PUA = 2
PU_CTRL_PUR = 3
PU_CTRL_CS = 4
PU_CTRL_CR = 5
PU_CTRL_AVDDS = 7

CTRL2_CALS = 2
CTRL2_CAL_ERROR = 3
CTRL2_CHS = 7

PGA_LDOMODE = 6
PGA_PWR_PGA_CAP_EN = 7

CALMOD_INTERNAL = 0

GAIN_BITS = {
    1: 0b000,
    2: 0b001,
    4: 0b010,
    8: 0b011,
    16: 0b100,
    32: 0b101,
    64: 0b110,
    128: 0b111,
}

SAMPLE_RATE_BITS = {
    10: 0b000,
    20: 0b001,
    40: 0b010,
    80: 0b011,
    320: 0b111,
}


class NAU7802Scale(ScaleDevice):
    """NAU7802 scale backend using direct Blinka I2C register access."""

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
        self._i2c = None
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

            self._i2c = board.I2C()
            self._sensor = self._i2c
            self._read_register(NAU7802_DEVICE_REV)
            self._reset()
            self._power_up()
            self._set_ldo_3v3()
            self._set_gain(self.gain)
            self._set_sample_rate(self.poll_rate)
            self._set_channel(self.channel)

            # Recommended NAU7802 startup tweaks from the SparkFun reference
            # driver: disable CLK_CHP, enable PGA capacitor, and use normal LDO.
            self._write_register(NAU7802_ADC, self._read_register(NAU7802_ADC) | 0x30)
            self._set_bit(PGA_PWR_PGA_CAP_EN, NAU7802_PGA_PWR)
            self._clear_bit(PGA_LDOMODE, NAU7802_PGA)

            time.sleep(0.25)
            self._calibrate_afe()
            self._connected = True
            self._read_samples(min(self.samples, 10))
            self._last_error = None
        except Exception as exc:
            self._i2c = None
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
            data = self._read_registers(NAU7802_ADCO_B2, 3)
            value = (data[0] << 16) | (data[1] << 8) | data[2]
            if value & 0x800000:
                value -= 0x1000000
            return value
        except Exception as exc:
            self._last_error = str(exc)
            return None

    def _wait_ready(self, timeout_seconds: float) -> bool:
        if self._i2c is None:
            return False

        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            try:
                if self._get_bit(PU_CTRL_CR, NAU7802_PU_CTRL):
                    return True
            except Exception as exc:
                self._last_error = str(exc)
                return False
            time.sleep(0.01)
        return False

    def _reset(self) -> None:
        self._set_bit(PU_CTRL_RR, NAU7802_PU_CTRL)
        time.sleep(0.001)
        self._clear_bit(PU_CTRL_RR, NAU7802_PU_CTRL)
        time.sleep(0.001)

    def _power_up(self) -> None:
        self._set_bit(PU_CTRL_PUD, NAU7802_PU_CTRL)
        self._set_bit(PU_CTRL_PUA, NAU7802_PU_CTRL)

        deadline = time.monotonic() + 0.2
        while time.monotonic() < deadline:
            if self._get_bit(PU_CTRL_PUR, NAU7802_PU_CTRL):
                self._set_bit(PU_CTRL_CS, NAU7802_PU_CTRL)
                return
            time.sleep(0.001)

        raise RuntimeError("NAU7802 did not report power-up ready.")

    def _set_ldo_3v3(self) -> None:
        self._update_bits(NAU7802_CTRL1, mask=0b00111000, value=0b100 << 3)
        self._set_bit(PU_CTRL_AVDDS, NAU7802_PU_CTRL)

    def _set_gain(self, gain: int) -> None:
        if gain not in GAIN_BITS:
            raise ValueError(
                "NAU7802 gain must be one of: "
                + ", ".join(str(value) for value in sorted(GAIN_BITS))
            )
        self._update_bits(NAU7802_CTRL1, mask=0b00000111, value=GAIN_BITS[gain])

    def _set_sample_rate(self, sample_rate: int) -> None:
        if sample_rate not in SAMPLE_RATE_BITS:
            raise ValueError(
                "NAU7802 poll_rate must be one of: "
                + ", ".join(str(value) for value in sorted(SAMPLE_RATE_BITS))
            )
        self._update_bits(
            NAU7802_CTRL2,
            mask=0b01110000,
            value=SAMPLE_RATE_BITS[sample_rate] << 4,
        )

    def _set_channel(self, channel: int) -> None:
        if channel == 1:
            self._clear_bit(CTRL2_CHS, NAU7802_CTRL2)
        elif channel == 2:
            self._set_bit(CTRL2_CHS, NAU7802_CTRL2)
        else:
            raise ValueError("NAU7802 channel must be 1 or 2.")

    def _calibrate_afe(self) -> None:
        self._update_bits(NAU7802_CTRL2, mask=0b00000011, value=CALMOD_INTERNAL)
        self._set_bit(CTRL2_CALS, NAU7802_CTRL2)

        deadline = time.monotonic() + 1.0
        while time.monotonic() < deadline:
            if not self._get_bit(CTRL2_CALS, NAU7802_CTRL2):
                if self._get_bit(CTRL2_CAL_ERROR, NAU7802_CTRL2):
                    raise RuntimeError("NAU7802 analog front-end calibration failed.")
                return
            time.sleep(0.001)

        raise RuntimeError("NAU7802 analog front-end calibration timed out.")

    def _get_bit(self, bit: int, register: int) -> bool:
        return bool(self._read_register(register) & (1 << bit))

    def _set_bit(self, bit: int, register: int) -> None:
        self._update_bits(register, mask=1 << bit, value=1 << bit)

    def _clear_bit(self, bit: int, register: int) -> None:
        self._update_bits(register, mask=1 << bit, value=0)

    def _update_bits(self, register: int, mask: int, value: int) -> None:
        current = self._read_register(register)
        self._write_register(register, (current & ~mask) | (value & mask))

    def _read_register(self, register: int) -> int:
        return self._read_registers(register, 1)[0]

    def _write_register(self, register: int, value: int) -> None:
        self._i2c_write(bytes([register, value & 0xFF]))

    def _read_registers(self, register: int, length: int) -> bytes:
        buffer = bytearray(length)
        self._i2c_write_then_read(bytes([register]), buffer)
        return bytes(buffer)

    def _i2c_write(self, data: bytes) -> None:
        if self._i2c is None:
            raise RuntimeError("NAU7802 I2C bus is not initialized.")

        self._lock_i2c()
        try:
            self._i2c.writeto(self.address, data)
        finally:
            self._i2c.unlock()

    def _i2c_write_then_read(self, out_buffer: bytes, in_buffer: bytearray) -> None:
        if self._i2c is None:
            raise RuntimeError("NAU7802 I2C bus is not initialized.")

        self._lock_i2c()
        try:
            self._i2c.writeto_then_readfrom(self.address, out_buffer, in_buffer)
        finally:
            self._i2c.unlock()

    def _lock_i2c(self) -> None:
        if self._i2c is None:
            raise RuntimeError("NAU7802 I2C bus is not initialized.")

        deadline = time.monotonic() + 1.0
        while time.monotonic() < deadline:
            if self._i2c.try_lock():
                return
            time.sleep(0.001)

        raise RuntimeError("Timed out waiting for NAU7802 I2C bus lock.")
