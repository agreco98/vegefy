from fastapi import APIRouter, UploadFile, File, Depends
from bson import ObjectId
import io
from PIL import Image
from datetime import datetime
import cv2
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

from application.ml import post_process_detections, non_max_suppression, classify_banana_type, draw_boxes
from application.auth import authenticate_user
from domain.users import User
from application.predictions.prediction import predictions_schema, search_prediction, create_prediction
import infrastructure.database.client as db
from domain.predictions import Prediction
from tensorflow.keras.models import load_model

router = APIRouter()

detector = hub.load("https://tfhub.dev/tensorflow/ssd_mobilenet_v2/2")
model = load_model(r'C:\Users\Milagros\Documents\Vegefly\backend\banana_recognition_model.h5')
# Load the banana type classification model
banana_type_model = load_model(r'C:\Users\Milagros\Documents\Vegefly\backend\banana_recognition_model.h5')

# Load class labels for COCO dataset (common object categories)
coco_labels = {
    1: 'person', 2: 'bicycle', 3: 'car', 4: 'motorcycle', 5: 'airplane', 6: 'bus',
    7: 'train', 8: 'truck', 9: 'boat', 10: 'traffic light', 11: 'fire hydrant',
    13: 'stop sign', 14: 'parking meter', 15: 'bench', 16: 'bird', 17: 'cat',
    18: 'dog', 19: 'horse', 20: 'sheep', 21: 'cow', 22: 'elephant', 23: 'bear',
    24: 'zebra', 25: 'giraffe', 27: 'backpack', 28: 'umbrella', 31: 'handbag',
    32: 'tie', 33: 'suitcase', 34: 'frisbee', 35: 'skis', 36: 'snowboard',
    37: 'sports ball', 38: 'kite', 39: 'baseball bat', 40: 'baseball glove',
    41: 'skateboard', 42: 'surfboard', 43: 'tennis racket', 44: 'bottle',
    46: 'wine glass', 47: 'cup', 48: 'fork', 49: 'knife', 50: 'spoon',
    51: 'bowl', 52: 'banana', 53: 'apple', 54: 'sandwich', 55: 'orange',
    56: 'broccoli', 57: 'carrot', 58: 'hot dog', 59: 'pizza', 60: 'donut',
    61: 'cake', 62: 'chair', 63: 'couch', 64: 'potted plant', 65: 'bed',
    67: 'dining table', 70: 'toilet', 72: 'tv', 73: 'laptop', 74: 'mouse',
    75: 'remote', 76: 'keyboard', 77: 'cell phone', 78: 'microwave',
    79: 'oven', 80: 'toaster', 81: 'sink', 82: 'refrigerator', 84: 'book',
    85: 'clock', 86: 'vase', 87: 'scissors', 88: 'teddy bear', 89: 'hair drier',
    90: 'toothbrush'
}


@router.get("/predictions", response_model=list[Prediction])
async def predictions(current_user: User = Depends(authenticate_user)):
    return predictions_schema(current_user.id)


# Path
@router.get("/predictions/{id}", response_model=Prediction)
async def prediction(id: str):
    return search_prediction("_id", ObjectId(id))


@router.post("/predict", response_model=Prediction, status_code=201)
async def predict_image(file: UploadFile = File(...), current_user: User = Depends(authenticate_user)):
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
    detector_output = detector(img_tensor)
    boxes = detector_output['detection_boxes'].numpy()[0]
    class_ids = detector_output['detection_classes'].numpy()[0].astype(int)
    scores = detector_output['detection_scores'].numpy()[0]

    # Filter banana detections
    class_names = [coco_labels[class_id] for class_id in class_ids]
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
        banana_type = classify_banana_type(banana_image, banana_type_model, banana_type_labels)
        img_with_boxes = draw_boxes(img_rgb, [box], [banana_type], [1.0])

    # Count bananas
    banana_count = len(banana_boxes)
    prediction_result = banana_count


    prediction = Prediction(
        id=None,
        user_id=current_user.id,
        response=prediction_result, 
        image=file.filename,  
        created_at=datetime.now().isoformat()
    )
    
    created_prediction = create_prediction(prediction)
    
    return created_prediction
