from dataclasses import dataclass


@dataclass
class NFCReading:
    connected: bool
    tag_present: bool
    tag_id: str | None


class NFCDevice:
    """Base interface for all NFC reader implementations."""

    def read(self) -> NFCReading:
        raise NotImplementedError

    def present_tag(self, tag_id: str) -> None:
        raise NotImplementedError

    def remove_tag(self) -> None:
        raise NotImplementedError
