from pydantic import BaseModel


class ScaleStatus(BaseModel):
    connected: bool
    stable: bool
    weightGrams: float | None
