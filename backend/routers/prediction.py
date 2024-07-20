import io
from fastapi import APIRouter, UploadFile, File, Depends
from PIL import Image

from application.auth import authenticate_user
from domain.users import UserDB


router = APIRouter()
#model =

@router.post("/predict/image")
async def predict_api(file: UploadFile = File(...), current_user: UserDB = Depends(authenticate_user)):
    content = await file.read()
    img = Image.open(io.BytesIO(content))
    #prediction = model.predict(img)
    return {"filename": file.filename}