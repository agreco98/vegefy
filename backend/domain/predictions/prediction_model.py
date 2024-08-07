from pydantic import BaseModel
from typing import Optional

class Prediction(BaseModel):
    id: Optional[str] | None
    user_id: str
    response: int
    image: str
    created_at: str


class PredictionResponse(BaseModel):
    prediction: Prediction
    base64: str