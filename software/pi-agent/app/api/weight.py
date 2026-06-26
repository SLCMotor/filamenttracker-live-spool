from fastapi import APIRouter

from app.models.scale import ScaleStatus
from app.services.scale_service import get_weight

router = APIRouter(tags=["weight"])


@router.get("/weight", response_model=ScaleStatus)
def weight():
    return get_weight()
