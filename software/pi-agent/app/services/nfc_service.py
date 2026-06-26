from app.core.device_manager import devices
from app.models.nfc import NfcStatus


def get_nfc() -> NfcStatus:
    reading = devices.nfc.read()

    return NfcStatus(
        connected=reading.connected,
        tagPresent=reading.tag_present,
        tagId=reading.tag_id,
    )
