from app.models.scale import ScaleStatus
from app.services.calibration_service import calibration_service


class ScaleService:
    def __init__(self):
        self.mock_raw_weight = 850.47
        self.connected = True
        self.stable = True

    def set_mock_raw_weight(self, weight_grams: float):
        self.mock_raw_weight = weight_grams

    def get_raw_weight(self) -> float:
        return self.mock_raw_weight

    def get_weight(self) -> ScaleStatus:
        raw_weight = self.get_raw_weight()

        calibrated_weight = (
            raw_weight - calibration_service.zero_offset
        ) / calibration_service.scale_factor

        return ScaleStatus(
            connected=self.connected,
            stable=self.stable,
            weightGrams=round(calibrated_weight, 2),
        )


scale_service = ScaleService()
