from fastapi import APIRouter

from app.models.nfc import NfcWriteRequest
from app.services.nfc_service import erase_nfc_tag, get_nfc
from app.services.nfc_write_service import (
    cancel_nfc_write,
    get_current_nfc_write_status,
    get_nfc_write_status,
    start_nfc_write,
)

router = APIRouter()


@router.get("/nfc")
def read_nfc() -> dict:
    return get_nfc()


@router.post("/nfc/erase")
def erase_nfc() -> dict:
    return erase_nfc_tag()


@router.post("/nfc/write")
def write_nfc(request: NfcWriteRequest) -> dict:
    return start_nfc_write(request)


@router.get("/nfc/write/current")
def current_nfc_write() -> dict:
    return get_current_nfc_write_status()


@router.get("/nfc/write/{request_id}")
def nfc_write_status(request_id: str) -> dict:
    return get_nfc_write_status(request_id)


@router.delete("/nfc/write/{request_id}")
def cancel_write_nfc(request_id: str) -> dict:
    return cancel_nfc_write(request_id)
