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


class NfcWriteRequest(BaseModel):
    requestId: str
    payload: dict[str, Any]
    display: dict[str, Any] | None = None
    timeoutSeconds: int = 60


class NfcWriteStatus(BaseModel):
    requestId: str | None = None
    state: str
    message: str
    tagId: str | None = None
    errorCode: str | None = None
    payload: dict[str, Any] | None = None
    display: dict[str, Any] | None = None
    startedAt: str | None = None
    updatedAt: str | None = None
    finishedAt: str | None = None
