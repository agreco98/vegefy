from fastapi import APIRouter, UploadFile, File, Depends
from bson import ObjectId
import io
from PIL import Image
from datetime import datetime

from application.auth import authenticate_user
from domain.users import User
from application.predictions.prediction import predictions_schema, search_prediction, create_prediction
import infrastructure.database.client as db
from domain.predictions import Prediction

router = APIRouter()


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
    img = Image.open(io.BytesIO(content))
    #prediction_result = model.predict(img)

    prediction_result = "im a result"

    prediction = Prediction(
        id=None,
        user_id=current_user.id,
        response=prediction_result, 
        image=file.filename,  
        created_at=datetime.now().isoformat()
    )
    
    created_prediction = create_prediction(prediction)
    
    return created_prediction
