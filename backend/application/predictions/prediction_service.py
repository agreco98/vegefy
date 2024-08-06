from typing import List
from fastapi import HTTPException
from bson import ObjectId
from pymongo.database import Database

import infrastructure.database.client as db
from domain.predictions.prediction_model import Prediction
from domain.predictions.prediction_repository import PredictionRepository


class PredictionService:
    def __init__(self, db: Database):
        self.repository = PredictionRepository(db)

    def create(self, prediction: Prediction) -> Prediction:
        if self.repository.search_prediction("_id", ObjectId(prediction.id)) is not None:
            raise HTTPException(status_code=400, detail="Prediction already exists")
        return self.repository.create(prediction)

    def get_all(self) -> List[Prediction]:
        return self.repository.get_all()
    
    def get_all_by_id(self, user_id: str) -> List[Prediction]:
        return self.repository.get_all_by_id(user_id)
    
    def get_prediction_by_id(self, _id: str) -> Prediction:
        return self.repository.search_prediction("_id", ObjectId(_id))

    def update(self, prediction: Prediction) -> Prediction:
        if not self.repository.search_prediction("_id", ObjectId(prediction.id)):
            raise HTTPException(status_code=404, detail="Prediction not found")
        return self.repository.update(prediction)
    
    def delete(self, _id: str) -> bool:
        if not self.repository.search_prediction("_id", ObjectId(_id)):
            raise HTTPException(status_code=404, detail="Prediction not found")
        return self.repository.delete(_id)