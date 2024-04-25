from fastapi import APIRouter, HTTPException, status, Depends
from ..database import get_db
from pymongo import MongoClient
from typing import List
from ..schemas.services import ReviewOut, ReviewBase
from datetime import datetime, UTC


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

    for review in reviews:
        review["company_name"] = service_provider["company_name"]

    return reviews


@router.post("/{sp_username}/services/{service_name}/reviews", status_code=status.HTTP_201_CREATED)
def create_review(sp_username: str, service_name: str, review: ReviewBase, db: MongoClient = Depends(get_db)):
    if review.rating < 1 or review.rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )

    db_user = db["users"].find_one({"username": review.username})

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{sp_username}' not found"
        )


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
    
    new_review = review.model_dump()
    new_review["created_at"] = datetime.now(UTC)
    new_review["updated_at"] = None
    
    db["serviceProviders"].update_one(
        {"username": sp_username, "services.name": service_name},
        {"$push": {"services.$.reviews": new_review}},
    )


    user_review = new_review
    user_review = dict(user_review)
    user_review["service_name"] = service_name
    user_review["sp_username"] = sp_username

    db["users"].update_one(
        {"username": sp_username},
        {"$push": {"reviews": user_review}},
    )

    return {"message": "Review created successfully"}


@router.delete("{sp_username}/services/{service_name}/reviews/{review_id}")
def delete_review(sp_username: str, service_name: str, review_id: str, db: MongoClient = Depends(get_db)):
    db["serviceProviders"].update_one(
        {"username": sp_username, "services.name": service_name},
        {"$pull": {"services.$.reviews": {"_id": review_id}}},
    )

    db["users"].update_one(
        {"username": sp_username},
        {"$pull": {"reviews": {"_id": review_id}}},
    )

    return {"message": "Review deleted successfully"}