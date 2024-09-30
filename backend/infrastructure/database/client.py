from fastapi import FastAPI
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from gridfs import GridFSBucket
from config import settings


async def connect_to_mongo(app: FastAPI):
    client = MongoClient(settings.database.mongo_url)
    app.state.client = client
    app.state.db = client.get_database(settings.database.mongo_db_name)
    app.state.fs = GridFSBucket(app.state.db)


async def close_mongo_connection(app: FastAPI):
    app.state.db.close()