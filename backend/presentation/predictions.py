from fastapi import APIRouter, UploadFile, File

from infrastructure.globals import DatabaseDependency, ModelsDependency, GridFSDependency, CurrentUser
from application.predictions.prediction_service import PredictionService
from domain.predictions import Prediction, PredictionResponse


router = APIRouter(tags=["predictions"])


@router.get("/predictions", status_code=200, response_model=list[Prediction])
async def predictions(db: DatabaseDependency, current_user: CurrentUser):
    service = PredictionService(db.local)
    return service.get_all()


@router.get("/predictions/{user_id}", status_code=200, response_model=list[Prediction])
async def predictions_by_id(user_id: str, db: DatabaseDependency, current_user: CurrentUser):
    service = PredictionService(db.local)
    return service.get_all_by_id(user_id)


# Path
@router.get("/prediction/{_id}", status_code=200, response_model=PredictionResponse)
async def prediction(_id: str, db: DatabaseDependency, fs: GridFSDependency, current_user: CurrentUser):
    service = PredictionService(db.local, fs)
    return service.get_prediction_by_id(_id)


@router.post("/predict", response_model=Prediction, status_code=201)
async def predict_image(
    db: DatabaseDependency,
    models: ModelsDependency,
    fs: GridFSDependency,
    current_user: CurrentUser,
    file: UploadFile = File(...)
    ):
    
    prediction_service = PredictionService(db.local, fs)
    return await prediction_service.process_and_create(file, current_user.id, models)


@router.put("/prediction", response_model=Prediction, status_code=201)
async def update_prediction(prediction: Prediction, db: DatabaseDependency, current_user: CurrentUser):
    service = PredictionService(db.local)
    return service.update(prediction)


@router.delete("/prediction/{_id}")
async def delete_prediction(_id: str, db: DatabaseDependency, current_user: CurrentUser):
    service = PredictionService(db.local)
    return service.delete(_id)
