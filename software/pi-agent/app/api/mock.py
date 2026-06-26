from fastapi import APIRouter

from app.core.device_manager import devices
from app.models.status import MockNfcTagRequest, StatusResponse
from app.services.status_service import get_status

router = APIRouter(prefix="/mock", tags=["mock"])


@router.post("/nfc/present", response_model=StatusResponse)
def mock_nfc_present(request: MockNfcTagRequest):
    devices.nfc.present_tag(request.tagId)
    return get_status()


@router.post("/nfc/remove", response_model=StatusResponse)
def mock_nfc_remove():
    devices.nfc.remove_tag()
    return get_status()
