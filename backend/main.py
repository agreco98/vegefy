from fastapi import FastAPI

from infrastructure import application
from presentation import auth_routes, users, predictions
from infrastructure.database.client import connect_to_mongo, close_mongo_connection


app: FastAPI = application.create(
    rest_routers=[predictions.router, auth_routes.router, users.router],
    startup_tasks=[connect_to_mongo],
    shutdown_tasks=[close_mongo_connection],
)

@app.get("/")
def root():
    return { "name": "route" }  