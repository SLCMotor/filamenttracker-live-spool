from app.core.device_manager import devices
from app.models.scale import ScaleStatus
from app.services.calibration_service import calibration_service


class ScaleService:
    def set_mock_raw_weight(self, weight_grams: float):
        devices.scale.set_mock_raw_weight_grams(weight_grams)

    def get_raw_weight(self) -> float:
        return devices.scale.get_raw_weight_grams()

    def get_fresh_raw_weight(self) -> float:
        return devices.scale.get_fresh_raw_weight_grams()

    def get_weight(self) -> ScaleStatus:
        raw_weight = self.get_raw_weight()

        calibrated_weight = (
            raw_weight - calibration_service.zero_offset
        ) / calibration_service.scale_factor

        return ScaleStatus(
            connected=devices.scale.is_connected(),
            stable=devices.scale.is_stable(),
            weightGrams=round(calibrated_weight, 2),
        )


scale_service = ScaleService()
