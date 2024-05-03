from fastapi import APIRouter, Depends
from ..database import get_db
from .. import utils
from pymongo import MongoClient
from app.database import get_db
from app.config import settings
import csv
from typing import List, Dict
from datetime import datetime, UTC


router = APIRouter(
    prefix = "/initializeDB",
    tags=['Initialize DB']
)


def insert_admin(db: MongoClient):
    admin_data = {
        "username": "a-" + settings.admin_username,
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
            file = open(f"./extras/icons/{row['icons']}", "r")
            category_data = {
                "name": row["categories"],
                "icon": file.read(),
            }
            categories_data.append(category_data)

    db["categories"].insert_many(categories_data)


def parse_review(review: str) -> List[Dict]:
    reviews = []
    review_split = review.split("|")
    
    for i in range(0, len(review_split), 3):
        review_data = {
            "rating": int(review_split[i+2]),
            "username": review_split[i+1],
            "description": review_split[i],
            "created_at": datetime.now(UTC),
            "updated_at": None
        }
        reviews.append(review_data)
    
    return reviews


def insert_users(db: MongoClient):
    users_data = []

    with open('extras/users.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row["password"] = utils.hash("123")
            users_data.append(row)

    db["users"].insert_many(users_data)
    
    insert_user_reviews(db)


def insert_user_reviews(db: MongoClient):
    with open('extras/services.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            reviews = parse_review(row["reviews"])

            for review in reviews:
                username = review["username"]
                del review["username"]
                review["service_name"] = row["name"]

                filter_query = {"username": username}

                update_operation = {
                    "$push": {
                        "reviews": review
                    }
                }

                db["users"].update_one(filter_query, update_operation)


def parse_FAQs(faq: str):
    faq_list = faq.split("|")
    faqs = []

    for i in range(0, len(faq_list)-1, 2):
        faq_data = {
            "question": faq_list[i],
            "answer": faq_list[i+1]
        }
        faqs.append(faq_data)
    
    return faqs


def insert_services(db: MongoClient):
    with open('extras/services.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            service_data = row.copy()
            del service_data["serviceProvider"]
            service_data["price"] = int(row["price"])
            service_data["reviews"] = parse_review(row["reviews"])
            service_data["users_booked"] = row["users_booked"].split(", ")
            service_data["faqs"] = parse_FAQs(row["faqs"])
            service_data["location"] = {
                "locality": row["locality"],
                "city": row["city"]
            }
            del service_data["locality"]
            del service_data["city"]

            filter_query = {"username": f"sp-{row['serviceProvider']}"}

            update_operation = {
                "$push": {
                    "services": service_data
                }
            }

            db["serviceProviders"].update_one(filter_query, update_operation)


@router.get("/")
def initializeDB(db: MongoClient = Depends(get_db)):
    client = MongoClient(f"{settings.mongo_url}")
    client.drop_database(f"{settings.mongo_db}")
    
    insert_admin(db)
    insert_users(db)
    insert_service_providers(db)
    insert_categories(db)
    insert_services(db)

    return {"message": "DB initialized"}
