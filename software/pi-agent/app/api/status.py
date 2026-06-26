from fastapi import APIRouter

from app.models.status import StatusResponse
from app.services.status_service import get_status

router = APIRouter()


@router.get("/status", response_model=StatusResponse)
def status():
    return get_status()
