from dataclasses import dataclass
from typing import Optional


@dataclass
class NFCReading:
    connected: bool
    tag_present: bool
    tag_id: Optional[str]


class NFCDevice:
    def read(self) -> NFCReading:
        raise NotImplementedError
