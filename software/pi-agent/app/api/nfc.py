from fastapi import APIRouter

from app.models.nfc import NfcStatus
from app.services.nfc_service import get_nfc

router = APIRouter(tags=["nfc"])


@router.get("/nfc", response_model=NfcStatus)
def nfc():
    return get_nfc()
