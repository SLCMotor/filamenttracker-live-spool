from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.calibration_service import calibration_service
from app.services.scale_service import scale_service

router = APIRouter(prefix="/calibration")


class KnownWeightRequest(BaseModel):
    knownWeightGrams: float


@router.post("/tare")
def tare():
    raw_weight = scale_service.get_raw_weight()
    calibration_service.tare(raw_weight)

    return {
        "success": True,
        "message": "Scale tared",
        "zeroOffset": calibration_service.zero_offset,
    }


@router.post("/known-weight")
def known_weight(request: KnownWeightRequest):
    try:
        raw_weight = scale_service.get_raw_weight()
        calibration_service.calibrate(
            raw_weight=raw_weight,
            known_weight=request.knownWeightGrams,
        )

        return {
            "success": True,
            "message": "Scale calibrated",
            "knownWeightGrams": request.knownWeightGrams,
            "scaleFactor": calibration_service.scale_factor,
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("/status")
def status():
    return calibration_service.status()
