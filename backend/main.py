from fastapi import FastAPI

from infrastructure import application
from presentation import auth_routes, users, predictions
from infrastructure.database.client import connect_to_mongo, close_mongo_connection
from infrastructure.ml.load_ml import load_ml_models, unload_ml_models
from infrastructure.ml.load_pickle import load_pickle
from infrastructure.middleware.middleware import DailyRateLimitMiddleware


app: FastAPI = application.create(
    rest_routers=[predictions.router, auth_routes.router, users.router],
    startup_tasks=[connect_to_mongo, load_ml_models, load_pickle],
    shutdown_tasks=[close_mongo_connection, unload_ml_models],
    middlewares=[DailyRateLimitMiddleware]
)

@app.get("/")
def root():
    return { "name": "route" }  