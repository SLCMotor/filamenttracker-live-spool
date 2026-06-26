from app.models.status import StatusResponse
from app.services.scale_service import scale_service
from app.services.nfc_service import get_nfc


def get_status() -> StatusResponse:
    return StatusResponse(
        status="online",
        deviceName="Live Spool",
        version="0.1.0",
        scale=scale_service.get_weight(),
        nfc=get_nfc(),
    )
