from fastapi import APIRouter, Depends
from pymongo import MongoClient
from ..database import get_db
from pprint import pprint

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/{search_term}")
def search_service(search_term: str, db: MongoClient = Depends(get_db)):
    query = {
        "$or": [
            {"company_name": {"$regex": search_term, "$options": "i"}},
            {
                "services": {
                    "$elemMatch": {
                        "$or": [
                            {"category": {"$regex": search_term, "$options": "i"}},
                            {"name": {"$regex": search_term, "$options": "i"}},
                        ]
                    }
                }
            },
        ]
    }

    results = db["serviceProviders"].find(query)

    output = []
    for result in results:
        services = result.get("services", [])
        for service in services:
            name = service.get("name", "")
            category = service.get("category", "")
            sp_username = result.get("username")
            output.append([name, category, sp_username])

    return output
