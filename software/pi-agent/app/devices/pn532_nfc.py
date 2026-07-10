from app.devices.nfc import NFCDevice, NFCReading


class PN532NFCDevice(NFCDevice):
    """Real PN532 NFC reader adapter for the legacy device manager interface."""

    def read(self) -> NFCReading:
        from app.services.nfc_service import get_nfc

        status = get_nfc()
        return NFCReading(
            connected=bool(status.get("connected", False)),
            tag_present=bool(status.get("tagPresent", False)),
            tag_id=status.get("tagId"),
        )

    def present_tag(self, tag_id: str) -> None:
        raise RuntimeError("Mock tag presentation is only available when NFC mock mode is enabled.")

    def remove_tag(self) -> None:
        raise RuntimeError("Mock tag removal is only available when NFC mock mode is enabled.")
