from fastapi import APIRouter

from app.services.nfc_service import erase_nfc_tag, get_nfc

router = APIRouter()


@router.get("/nfc")
def read_nfc() -> dict:
    return get_nfc()


@router.post("/nfc/erase")
def erase_nfc() -> dict:
    return erase_nfc_tag()
