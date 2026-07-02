from pydantic import BaseModel

from app.models.nfc import NfcStatus
from app.models.scale import ScaleStatus


class StatusResponse(BaseModel):
    status: str
    deviceName: str
    version: str
    scale: ScaleStatus
    nfc: NfcStatus
    cpuTempC: float | None = None
    uptime: str | None = None
