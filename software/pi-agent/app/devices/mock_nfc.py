from app.devices.nfc import NFCDevice, NFCReading


class MockNFCDevice(NFCDevice):
    """Mock NFC reader used for development without real hardware."""

    def __init__(self) -> None:
        self.connected = True
        self.tag_present = False
        self.tag_id: str | None = None

    def read(self) -> NFCReading:
        return NFCReading(
            connected=self.connected,
            tag_present=self.tag_present,
            tag_id=self.tag_id,
        )

    def present_tag(self, tag_id: str) -> None:
        self.tag_present = True
        self.tag_id = tag_id.upper()

    def remove_tag(self) -> None:
        self.tag_present = False
        self.tag_id = None
