from fastapi import FastAPI
from infrastructure import application
from routers import prediction
from presentation import auth_routes, users


app: FastAPI = application.create(
    rest_routers=[prediction.router, auth_routes.router, users.router],
    startup_tasks=[],
    shutdown_tasks=[],
)

@app.get("/")
def root():
    return { "name": "route" }  