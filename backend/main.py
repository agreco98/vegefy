from fastapi import FastAPI
from infrastructure import application
from routers import prediction


app: FastAPI = application.create(
    rest_routers=[prediction.router],
    startup_tasks=[],
    shutdown_tasks=[],
)

@app.get("/")
def root():
    return { "name": "route" }  