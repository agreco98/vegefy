from domain.predictions import Prediction
import infrastructure.database.client as db


def prediction_schema(prediction) -> dict:
    return {"id": str(prediction["_id"]),
            "user_id": prediction["user_id"],
            "response": prediction["response"],
            "gemini_response": prediction["gemini_response"],
            "image": prediction["image"],
            "created_at": prediction["created_at"]
    }
    

def create_prediction(prediction: Prediction) -> Prediction:
    prediction_dict = dict(prediction)
    del prediction_dict["id"]

    id = db.client.local.predictions.insert_one(prediction_dict).inserted_id

    new_prediction = prediction_schema(db.client.local.predictions.find_one({"_id": id}))

    return Prediction(**new_prediction)