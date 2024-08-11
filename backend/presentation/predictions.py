from fastapi import APIRouter, UploadFile, File, Depends, Request
from PIL import Image
from typing import List, Collection
from gridfs import GridFS

from application.auth.auth import get_current_user
from application.predictions.prediction_service import PredictionService
from application.users.user_service import UserService
from domain.predictions import Prediction, PredictionResponse
from domain.users.user_model import User

router = APIRouter()

def get_database(request: Request) -> Collection:
    return request.app.state.db

def get_gridfs(request: Request) -> GridFS:
    return request.app.state.fs

def get_models(request: Request):
    return request.app.state.detector_model, request.app.state.classification_model, request.app.state.coco_model


@router.get("/predictions", status_code=200, response_model=list[Prediction])
async def predictions(user: User = Depends(get_current_user), db: Collection = Depends(get_database)):
    service = PredictionService(db.local)
    return service.get_all()


@router.get("/predictions/{user_id}", status_code=200, response_model=list[Prediction])
async def predictions_by_id(user_id: str, user: User = Depends(get_current_user), db: Collection = Depends(get_database)):
    service = PredictionService(db.local)
    return service.get_all_by_id(user_id)


# Path
@router.get("/prediction/{_id}", status_code=200, response_model=PredictionResponse)
async def prediction(_id: str, user: User = Depends(get_current_user), db: Collection = Depends(get_database), fs: GridFS = Depends(get_gridfs)):
    service = PredictionService(db.local, fs)
    return service.get_prediction_by_id(_id)


@router.post("/predict", response_model=Prediction, status_code=201)
async def predict_image(
    file: UploadFile = File(...), 
    db: Collection = Depends(get_database),
    user: User = Depends(get_current_user),
    models: List = Depends(get_models),
    fs: GridFS = Depends(get_gridfs)
    ):
    
    prediction_service = PredictionService(db.local, fs)
    return await prediction_service.process_and_create(file, user.id, models)


@router.put("/prediction", response_model=Prediction, status_code=201)
async def update_prediction(prediction: Prediction, user: User = Depends(get_current_user), db: Collection = Depends(get_database)):
    service = PredictionService(db.local)
    return service.update(prediction)


@router.delete("/prediction/{_id}")
async def delete_prediction(_id: str, user: User = Depends(get_current_user), db: Collection = Depends(get_database)):
    service = PredictionService(db.local)
    return service.delete(_id)
