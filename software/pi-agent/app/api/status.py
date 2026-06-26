from fastapi import APIRouter

from app.core.config import config
from app.core.device_manager import devices
from app.models.status import NfcStatus, ScaleStatus, StatusResponse

router = APIRouter()


@router.get("/status", response_model=StatusResponse)
def status():
    weight = devices.scale.get_weight_grams()
    nfc_reading = devices.nfc.read()

    return StatusResponse(
        status="online",
        deviceName=config.device_name,
        version=config.version,
        scale=ScaleStatus(
            connected=devices.scale.is_connected(),
            stable=True,
            weightGrams=weight,
        ),
        nfc=NfcStatus(
            connected=nfc_reading.connected,
            tagPresent=nfc_reading.tag_present,
            tagId=nfc_reading.tag_id,
        ),
    )
