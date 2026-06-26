from pydantic import BaseModel


class ScaleStatus(BaseModel):
    connected: bool
    stable: bool
    weightGrams: float | None


class NfcStatus(BaseModel):
    connected: bool
    tagPresent: bool
    tagId: str | None


class StatusResponse(BaseModel):
    status: str
    deviceName: str
    version: str
    scale: ScaleStatus
    nfc: NfcStatus


class MockNfcTagRequest(BaseModel):
    tagId: str
