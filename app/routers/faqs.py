from fastapi import APIRouter, HTTPException, status, Depends
from ..database import get_db
from pymongo import MongoClient
from ..schemas.services import FAQ
from typing import List


router = APIRouter(
    prefix="/service-providers",
    tags=["FAQs"]
)


@router.get("/{sp_username}/services/{service_name}/faqs", response_model=List[FAQ])
def get_faqs_by_service(sp_username: str, service_name: str, db: MongoClient = Depends(get_db)):
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
    
    faqs = matching_service.get("faqs", [])

    return faqs