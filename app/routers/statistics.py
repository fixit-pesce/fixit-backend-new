from fastapi import APIRouter, Depends
from pymongo import MongoClient
from ..database import get_db

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/category-distribution")
def get_category_distribution(db: MongoClient = Depends(get_db)):
    categoriesDistribution = dict()

    service_providers = db["serviceProviders"].find()

    for service_provider in service_providers:
        for service in service_provider.get("services", []):
            category = service["category"]
            if category in categoriesDistribution:
                categoriesDistribution[category] += 1
            else:
                categoriesDistribution[category] = 1

    return categoriesDistribution