from fastapi import APIRouter

from app.services.nfc_service import get_nfc

router = APIRouter()


@router.get("/nfc")
def read_nfc() -> dict:
    return get_nfc()
