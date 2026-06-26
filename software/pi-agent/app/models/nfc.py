from pydantic import BaseModel


class NfcStatus(BaseModel):
    connected: bool
    tagPresent: bool
    tagId: str | None


class MockNfcTagRequest(BaseModel):
    tagId: str
