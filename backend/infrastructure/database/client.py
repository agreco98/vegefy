from fastapi import FastAPI
from pymongo import MongoClient
from gridfs import GridFS


async def connect_to_mongo(app: FastAPI):
    client = MongoClient()
    app.state.db = client
    app.state.fs = GridFS(app.state.db.local)


async def close_mongo_connection(app: FastAPI):
    app.state.db.close()