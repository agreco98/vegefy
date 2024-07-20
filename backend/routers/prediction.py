import io
from fastapi import APIRouter, UploadFile, File
from PIL import Image

router = APIRouter()
#model =

@router.post("/predict/image")
async def predict_api(file: UploadFile = File(...)):
    content = await file.read()
    img = Image.open(io.BytesIO(content))
    #prediction = model.predict(img)
    return {"filename": file.filename}