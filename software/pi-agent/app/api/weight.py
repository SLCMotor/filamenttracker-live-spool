from fastapi import APIRouter

from app.services.scale_service import scale_service

router = APIRouter()


@router.get("/weight")
def get_weight():
    return scale_service.get_weight()
