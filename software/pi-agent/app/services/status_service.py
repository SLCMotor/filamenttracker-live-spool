from app.core.config import config
from app.core.device_manager import devices
from app.models.nfc import NfcStatus
from app.models.scale import ScaleStatus
from app.models.status import StatusResponse


def get_status() -> StatusResponse:
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
