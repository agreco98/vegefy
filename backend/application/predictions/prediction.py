from domain.predictions import Prediction
import infrastructure.database.client as db


def prediction_schema(prediction) -> dict:
    return {"id": str(prediction["_id"]),
            "user_id": prediction["user_id"],
            "response": prediction["response"],
            "image": prediction["image"],
            "created_at": prediction["created_at"]
    }

def predictions_schema(user_id: str) -> list:
    predictions = db.client.local.predictions.find({"user_id": user_id})
    return [prediction_schema(prediction) for prediction in predictions]


def search_prediction(field: str, key) -> Prediction:
    try:
        prediction = db.client.local.predictions.find_one({field: key})
        return Prediction(**prediction_schema(prediction))
    except:
        return {"error": "User was not found"}
    

def create_prediction(prediction: Prediction) -> Prediction:
    prediction_dict = dict(prediction)
    del prediction_dict["id"]

    id = db.client.local.predictions.insert_one(prediction_dict).inserted_id

    new_prediction = prediction_schema(db.client.local.predictions.find_one({"_id": id}))

    return Prediction(**new_prediction)