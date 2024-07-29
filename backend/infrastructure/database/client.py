from pymongo import MongoClient
from config import settings

client = None

async def connect_to_mongo():
    global client
    client = MongoClient()


async def close_mongo_connection():
    global client
    if client:
        client.close()