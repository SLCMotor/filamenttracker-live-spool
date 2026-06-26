from pydantic import BaseModel


class CalibrationStatus(BaseModel):
    calibrated: bool
    zeroOffset: float
    scaleFactor: float
