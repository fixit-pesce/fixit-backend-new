from pymongo import MongoClient
from .config import settings

MONGO_URL = settings.mongo_url
MONGO_DB = settings.mongo_db

client = MongoClient(MONGO_URL)
db = client[MONGO_DB]

async def get_db() -> MongoClient:
    return db