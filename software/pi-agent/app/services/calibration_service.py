import json
import os
import tempfile
from pathlib import Path
from typing import Any

from app.models.calibration import CalibrationStatus


class CalibrationService:
    def __init__(self):
        self.app_root = Path(__file__).resolve().parents[2]
        self.calibration_file = self.app_root / "data" / "calibration.json"

        self.zero_offset = 0.0
        self.scale_factor = 1.0
        self.calibrated = False
        self.loaded_from_disk = False
        self.error: str | None = None

        self.load()

    def load(self):
        self.loaded_from_disk = False
        self.error = None

        if not self.calibration_file.exists():
            return

        try:
            with self.calibration_file.open("r", encoding="utf-8") as file:
                data: dict[str, Any] = json.load(file)

            self.zero_offset = float(data.get("zeroOffset", 0.0))
            self.scale_factor = float(data.get("scaleFactor", 1.0))
            self.calibrated = bool(data.get("calibrated", False))

            if self.scale_factor == 0:
                self.scale_factor = 1.0
                self.calibrated = False
                self.error = "Stored scaleFactor was zero; reset to 1.0"

            self.loaded_from_disk = True

        except Exception as exc:
            self.zero_offset = 0.0
            self.scale_factor = 1.0
            self.calibrated = False
            self.loaded_from_disk = False
            self.error = f"Failed to load calibration: {exc}"

    def save(self):
        self.calibration_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "calibrated": self.calibrated,
            "zeroOffset": self.zero_offset,
            "scaleFactor": self.scale_factor,
        }

        temp_fd, temp_path = tempfile.mkstemp(
            prefix="calibration-",
            suffix=".json",
            dir=str(self.calibration_file.parent),
            text=True,
        )

        try:
            with os.fdopen(temp_fd, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2)
                file.write("\n")
                file.flush()
                os.fsync(file.fileno())

            os.replace(temp_path, self.calibration_file)
            self.loaded_from_disk = True
            self.error = None

        except Exception as exc:
            try:
                os.unlink(temp_path)
            except OSError:
                pass

            self.error = f"Failed to save calibration: {exc}"
            raise

    def tare(self, current_raw_weight: float):
        self.zero_offset = current_raw_weight
        self.scale_factor = 1.0
        self.calibrated = False
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
            calibrationFile=str(self.calibration_file),
            loadedFromDisk=self.loaded_from_disk,
            error=self.error,
        )


calibration_service = CalibrationService()
