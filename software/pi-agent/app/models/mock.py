from pydantic import BaseModel


class MockWeightRequest(BaseModel):
    weightGrams: float
