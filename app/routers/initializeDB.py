from fastapi import APIRouter, Depends
from ..database import get_db
from .. import utils
from pymongo import MongoClient
from app.database import get_db
from app.config import settings
import csv


router = APIRouter(
    prefix = "/initializeDB",
    tags=['Initialize DB']
)


def insert_admin(db: MongoClient):
    admin_data = {
        "username": settings.admin_username,
        "password": utils.hash(settings.admin_password),
        "email": settings.admin_email
    }

    db["admins"].insert_one(admin_data)


def insert_service_providers(db: MongoClient):
    service_providers_data = []

    with open('extras/serviceProviders.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row["username"] = "sp-" + row["username"]
            row["password"] = utils.hash("123")
            service_providers_data.append(row)

    db["serviceProviders"].insert_many(service_providers_data)


def insert_categories(db: MongoClient):
    categories_data = []

    with open('extras/categories.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            categories_data.append(row)

    db["categories"].insert_many(categories_data)


def insert_users(db: MongoClient):
    users_data = []

    with open('extras/users.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row["password"] = utils.hash("123")
            users_data.append(row)

    db["users"].insert_many(users_data)


@router.get("/")
def initializeDB(db: MongoClient = Depends(get_db)):
    # db.drop_database(settings.mongo_db) # Comment this out if the database has not been initialized yet
    
    insert_admin(db)
    insert_users(db)
    insert_service_providers(db)
    insert_categories(db)

    return {"message": "DB initialized"}
