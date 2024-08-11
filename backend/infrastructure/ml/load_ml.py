from fastapi import FastAPI
import tensorflow_hub as hub
from tensorflow.keras.models import load_model


async def load_ml_models(app: FastAPI):
    detector_model = hub.load("https://tfhub.dev/tensorflow/ssd_mobilenet_v2/2")
    classification_model = load_model(r'C:\Users\Milagros\Documents\Vegefly\backend\banana_recognition_model.h5')
    coco_model = {
                    52: 'banana',
                    53: 'apple',
                    55: 'orange',
                    56: 'broccoli',
                    57: 'carrot'
                }
    
    app.state.detector_model = detector_model
    app.state.classification_model = classification_model
    app.state.coco_model = coco_model



async def unload_ml_models(app: FastAPI):
    del app.state.detector_model
    del app.state.classification_model
    del app.state.coco_model
