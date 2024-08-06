from fastapi import APIRouter, UploadFile, File, Depends, Request
import io
from PIL import Image
from datetime import datetime
import cv2
import numpy as np
import tensorflow as tf
from typing import List, Collection

from application.ml import post_process_detections, non_max_suppression, classify_banana_type, draw_boxes
from application.auth import authenticate_user
from application.predictions.prediction_service import PredictionService
from application.users.user_service import UserService
from domain.users import User
from domain.predictions.prediction_schema import create_prediction
import infrastructure.database.client as db
from domain.predictions import Prediction

router = APIRouter()

def get_database(request: Request) -> Collection:
    return request.app.state.db

def get_models(request: Request):
    return request.app.state.detector_model, request.app.state.classification_model, request.app.state.coco_model


@router.get("/predictions", status_code=200, response_model=list[Prediction])
async def predictions(db: Collection = Depends(get_database)):
    service = PredictionService(db.local)
    return service.get_all()


@router.get("/predictions/{user_id}", status_code=200, response_model=list[Prediction])
async def predictions_by_id(user_id: str, db: Collection = Depends(get_database)):
    service = PredictionService(db.local)
    return service.get_all_by_id(user_id)


# Path
@router.get("/prediction/{_id}", status_code=200, response_model=Prediction)
async def prediction(_id: str, db: Collection = Depends(get_database)):
    service = PredictionService(db.local)
    return service.get_prediction_by_id(_id)


@router.post("/predict", response_model=Prediction, status_code=201)
async def predict_image(
    file: UploadFile = File(...), 
    db: Collection = Depends(get_database),
    username: str = Depends(authenticate_user),
    models: List = Depends(get_models)
    ):

    user_service = UserService(db.local)
    prediction_service = PredictionService(db.local)

    content = await file.read()

    # Define banana type labels (adjust according to your model's classes)
    banana_type_labels = ['Banana', 'Banana Lady Finger', 'Banana Red'] 

    # Preprocess the image for the model
    img = Image.open(io.BytesIO(content))
    img_rgb = np.array(img)
    img_resized = cv2.resize(img_rgb, (320, 320))
    img_tensor = tf.convert_to_tensor(img_resized, dtype=tf.uint8)
    img_tensor = tf.expand_dims(img_tensor, 0)

    # Perform object detection
    detector_output = models[0](img_tensor)
    boxes = detector_output['detection_boxes'].numpy()[0]
    class_ids = detector_output['detection_classes'].numpy()[0].astype(int)
    scores = detector_output['detection_scores'].numpy()[0]

    # Filter banana detections
    class_names = [models[2][class_id] for class_id in class_ids]
    banana_boxes = boxes[class_ids == 52]
    banana_scores = scores[class_ids == 52]

    # Apply Non-Maximum Suppression
    banana_boxes, banana_scores = non_max_suppression(banana_boxes, banana_scores, threshold=0.5)
    banana_boxes, banana_scores = post_process_detections(banana_boxes, banana_scores, threshold=0.5)

    # Draw bounding boxes and classify each banana
    img_with_boxes = img_rgb.copy()
    for box in banana_boxes:
        ymin, xmin, ymax, xmax = box
        ymin, xmin, ymax, xmax = int(ymin * img_rgb.shape[0]), int(xmin * img_rgb.shape[1]), int(ymax * img_rgb.shape[0]), int(xmax * img_rgb.shape[1])
        banana_image = img_rgb[ymin:ymax, xmin:xmax]
        banana_type = classify_banana_type(banana_image, models[1], banana_type_labels)
        img_with_boxes = draw_boxes(img_rgb, [box], [banana_type], [1.0])

    # Count bananas
    banana_count = len(banana_boxes)
    prediction_result = banana_count


    prediction = Prediction(
        id=None,
        user_id=user_service.get_user_by_username(username).id,
        response=prediction_result, 
        image=file.filename,  
        created_at=datetime.now().isoformat()
    )
    
    created_prediction = prediction_service.create(prediction)
    
    return created_prediction


@router.put("/prediction", response_model=Prediction, status_code=201)
async def update_prediction(prediction: Prediction, db: Collection = Depends(get_database)):
    service = PredictionService(db.local)
    return service.update(prediction)


@router.delete("/prediction/{_id}")
async def delete_prediction(_id: str, db: Collection = Depends(get_database)):
    service = PredictionService(db.local)
    return service.delete(_id)
