from fastapi import APIRouter

from app.services.spool_service import get_current_spool

router = APIRouter(prefix="/spool", tags=["spool"])


@router.get("/current")
def current_spool() -> dict:
    return get_current_spool()
