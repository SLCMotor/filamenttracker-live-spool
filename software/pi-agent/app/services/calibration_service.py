import json
from pathlib import Path

from app.models.calibration import CalibrationStatus


class CalibrationService:
    def __init__(self):
        self.calibration_file = Path("data/calibration.json")
        self.zero_offset = 0.0
        self.scale_factor = 1.0
        self.calibrated = False
        self.load()

    def load(self):
        if not self.calibration_file.exists():
            return

        with self.calibration_file.open("r", encoding="utf-8") as file:
            data = json.load(file)

        self.zero_offset = float(data.get("zeroOffset", 0.0))
        self.scale_factor = float(data.get("scaleFactor", 1.0))
        self.calibrated = bool(data.get("calibrated", False))

        if self.scale_factor == 0:
            self.scale_factor = 1.0

    def save(self):
        self.calibration_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "calibrated": self.calibrated,
            "zeroOffset": self.zero_offset,
            "scaleFactor": self.scale_factor,
        }

        with self.calibration_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    def tare(self, current_raw_weight: float):
        self.zero_offset = current_raw_weight
        self.calibrated = True
        self.save()

    def calibrate(self, raw_weight: float, known_weight: float):
        if known_weight <= 0:
            raise ValueError("Known weight must be greater than zero")

        measured_delta = raw_weight - self.zero_offset

        if measured_delta <= 0:
            raise ValueError("Raw weight must be greater than zero offset")

        self.scale_factor = measured_delta / known_weight
        self.calibrated = True
        self.save()

    def reset(self):
        self.zero_offset = 0.0
        self.scale_factor = 1.0
        self.calibrated = False
        self.save()

    def status(self):
        return CalibrationStatus(
            calibrated=self.calibrated,
            zeroOffset=self.zero_offset,
            scaleFactor=self.scale_factor,
        )


calibration_service = CalibrationService()
