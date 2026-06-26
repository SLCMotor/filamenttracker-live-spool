from app.models.calibration import CalibrationStatus


class CalibrationService:
    def __init__(self):
        self.zero_offset = 0.0
        self.scale_factor = 1.0
        self.calibrated = False

    def tare(self, current_raw_weight: float):
        self.zero_offset = current_raw_weight
        self.calibrated = True

    def calibrate(self, raw_weight: float, known_weight: float):
        if known_weight <= 0:
            raise ValueError("Known weight must be greater than zero")

        self.scale_factor = (raw_weight - self.zero_offset) / known_weight
        self.calibrated = True

    def status(self):
        return CalibrationStatus(
            calibrated=self.calibrated,
            zeroOffset=self.zero_offset,
            scaleFactor=self.scale_factor,
        )


calibration_service = CalibrationService()
