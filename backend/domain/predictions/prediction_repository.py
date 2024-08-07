from typing import List, Optional
from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection
from gridfs import GridFS

from domain.predictions.prediction_model import Prediction
from domain.predictions.prediction_schema import prediction_schema


class PredictionRepository:
    def __init__(self, db: Database, fs: Optional[GridFS] = None):
        self.collection: Collection = db.predictions
        self.fs = fs

    def create(self, prediction: Prediction, image: bytes) -> Prediction:
        image_id = self.fs.put(image, filename=prediction.image)

        prediction_dict = dict(prediction)
        prediction_dict["image"] = str(image_id)
        del prediction_dict["id"]

        id = self.collection.insert_one(prediction_dict).inserted_id

        new_prediction = prediction_schema(self.collection.find_one({"_id": id}))
        
        return Prediction(**new_prediction)

    def get_all(self) -> List[Prediction]:
        predictions = self.collection.find()
        return [Prediction(**prediction_schema(prediction)) for prediction in predictions]
    
    def get_all_by_id(self, user_id: str) -> List[Prediction]:
        predictions = self.collection.find({"user_id": user_id})
        return [Prediction(**prediction_schema(prediction)) for prediction in predictions]

    def get_prediction(self, _id: str) -> Prediction:
        prediction = self.search_prediction("_id", ObjectId(_id))
        if prediction:
            return Prediction(**prediction_schema(prediction))
        return None

    def search_prediction(self, field: str, key) -> Optional[Prediction]:
        prediction = self.collection.find_one({field: key})
        return Prediction(**prediction_schema(prediction)) if prediction else None
    
    def get_image(self, image_id: str) -> bytes:
        return self.fs.get(ObjectId(image_id)).read()
    
    def update(self, prediction: Prediction) -> Prediction:
        prediction_dict = dict(prediction)
        del prediction_dict["id"]

        self.collection.find_one_and_replace({"_id": ObjectId(prediction.id)}, prediction_dict)
        return self.search_prediction("_id", ObjectId(prediction.id))

    def delete(self, _id: str) -> bool:
        found = self.collection.find_one_and_delete({"_id": ObjectId(_id)})
        return found is not None