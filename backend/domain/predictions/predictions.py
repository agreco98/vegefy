from pydantic import BaseModel
from typing import Optional

class Prediction(BaseModel):
    id: Optional[str] | None
    user_id: str
    response: str
    image: str
    created_at: str
