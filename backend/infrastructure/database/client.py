from fastapi import FastAPI
from pymongo import MongoClient


async def connect_to_mongo(app: FastAPI):
    client = MongoClient()
    app.state.db = client


async def close_mongo_connection(app: FastAPI):
    app.state.db.close()