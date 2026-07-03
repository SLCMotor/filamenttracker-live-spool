from typing import Any

from pydantic import BaseModel


class NfcStatus(BaseModel):
    connected: bool
    tagPresent: bool
    tagId: str | None = None
    data: str | None = None
    tag: dict[str, Any] | None = None
    tagType: str | None = None
    bambu: dict[str, Any] | None = None
    error: str | None = None


class MockNfcTagRequest(BaseModel):
    tagId: str
