from app.core.device_manager import devices
from app.models.nfc import NfcStatus


class NfcService:
    def get_status(self) -> NfcStatus:
        reading = devices.nfc.read()

        return NfcStatus(
            connected=reading.connected,
            tagPresent=reading.tag_present,
            tagId=reading.tag_id,
        )


nfc_service = NfcService()


def get_nfc() -> NfcStatus:
    return nfc_service.get_status()
