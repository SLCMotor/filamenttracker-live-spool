from app.services.nfc_service import get_nfc
from app.services.scale_service import scale_service


def get_status() -> dict:
    return {
        "status": "online",
        "deviceName": "Live Spool",
        "version": "0.1.0",
        "scale": scale_service.get_weight(),
        "nfc": get_nfc(),
    }
