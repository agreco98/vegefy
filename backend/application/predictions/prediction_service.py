from typing import List, Optional
from fastapi import HTTPException, UploadFile
from bson import ObjectId
from pymongo.database import Database
import base64
from gridfs import GridFS
from io import BufferedReader
from datetime import datetime

from domain.predictions.prediction_model import Prediction, PredictionResponse
from domain.predictions.prediction_repository import PredictionRepository
from application.ml import (post_process_detections, 
                            non_max_suppression, 
                            classify_banana_type, 
                            draw_boxes, 
                            preprocess_image, 
                            filter_banana_detections, 
                            draw_and_classify_bananas
                            )


class PredictionService:
    def __init__(self, db: Database, fs: Optional[GridFS] = None):
        self.repository = PredictionRepository(db, fs) 

    def create(self, prediction: Prediction, image: bytes) -> Prediction:
        if self.repository.search_prediction("_id", ObjectId(prediction.id)) is not None:
            raise HTTPException(status_code=400, detail="Prediction already exists")
        return self.repository.create(prediction, image)

    def get_all(self) -> List[Prediction]:
        return self.repository.get_all()
    
    def get_all_by_id(self, user_id: str) -> List[Prediction]:
        return self.repository.get_all_by_id(user_id)
    
    def get_prediction_by_id(self, _id: str) -> PredictionResponse:
        prediction = self.repository.search_prediction("_id", ObjectId(_id))

        image_content = self.repository.get_image(prediction.image)
        encoded_image = base64.b64encode(image_content).decode("utf-8")
        
        return PredictionResponse(prediction=prediction, base64=encoded_image)

    def update(self, prediction: Prediction) -> Prediction:
        if not self.repository.search_prediction("_id", ObjectId(prediction.id)):
            raise HTTPException(status_code=404, detail="Prediction not found")
        return self.repository.update(prediction)
    
    def delete(self, _id: str) -> bool:
        if not self.repository.search_prediction("_id", ObjectId(_id)):
            raise HTTPException(status_code=404, detail="Prediction not found")
        return self.repository.delete(_id)
    
    async def process_and_create(self, file: UploadFile, user_id: str, models: List, pickle_file: BufferedReader) -> Prediction:
        content = await file.read()

        # Preprocess the image for the model
        img_tensor, img_rgb = preprocess_image(content)

        # Perform object detection
        detector_output = models[0](img_tensor)
        boxes = detector_output['detection_boxes'].numpy()[0]
        class_ids = detector_output['detection_classes'].numpy()[0].astype(int)
        scores = detector_output['detection_scores'].numpy()[0]

        # Filter banana detections
        banana_boxes, banana_scores = filter_banana_detections(boxes, class_ids, scores)
        banana_boxes, banana_scores = non_max_suppression(banana_boxes, banana_scores, threshold=0.5)
        banana_boxes, banana_scores = post_process_detections(banana_boxes, banana_scores, threshold=0.5)

        img_with_boxes = img_rgb.copy()
        img_with_boxes = draw_and_classify_bananas(img_rgb, banana_boxes, models[1], ['Banana', 'Banana Lady Finger', 'Banana Red'])

        banana_count = len(banana_boxes)
        prediction_result = banana_count

        informative_response = pickle_file.get("banana")

        prediction = Prediction(
            id=None,
            user_id=user_id,
            response=informative_response, 
            image=file.filename,  
            created_at=datetime.now().isoformat()
        )
    
        return self.create(prediction, content)
        