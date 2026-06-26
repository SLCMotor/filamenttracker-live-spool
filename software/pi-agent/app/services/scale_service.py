from app.core.device_manager import devices
from app.models.scale import ScaleStatus


def get_weight() -> ScaleStatus:
    return ScaleStatus(
        connected=devices.scale.is_connected(),
        stable=True,
        weightGrams=devices.scale.get_weight_grams(),
    )
