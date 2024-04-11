from fastapi import APIRouter, HTTPException, status, Depends
from ..database import get_db
from pymongo import MongoClient
from typing import List
from ..schemas.services import ReviewOut


router = APIRouter(
    prefix="/service-providers",
    tags=["Reviews"]
)


@router.get("/{sp_username}/services/{service_name}/reviews", response_model=List[ReviewOut])
def get_reviews_of_service(sp_username: str, service_name: str, db: MongoClient = Depends(get_db)):
    service_provider = db["serviceProviders"].find_one({"username": sp_username})
    
    if not service_provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ServiceProvider '{sp_username}' not found"
        )
    
    services = service_provider.get("services", [])
    matching_service = None
    for service in services:
        if service.get("name") == service_name:
            matching_service = service
            break
    
    if not matching_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service '{service_name}' not found for serviceProvider '{sp_username}'"
        )
    
    reviews = matching_service.get("reviews", [])

    return reviews