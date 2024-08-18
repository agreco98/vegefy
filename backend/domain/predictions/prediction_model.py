from pydantic import BaseModel
from typing import Optional

class Prediction(BaseModel):
    id: Optional[str] | None
    user_id: str
    response: dict
    gemini_response: dict
    image: str
    created_at: str


class PredictionResponse(BaseModel):
    prediction: Prediction
    base64: str