from pymongo import MongoClient
from .config import settings

MONGO_URL = settings.mongo_url
MONGO_DB = settings.mongo_db

async def get_db() -> MongoClient:
    client = MongoClient(f"{MONGO_URL}/{MONGO_DB}")
    db = client.get_database()
    return db