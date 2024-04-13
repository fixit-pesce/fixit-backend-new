from fastapi import APIRouter, Depends, HTTPException, status
from ..database import get_db
from pymongo import MongoClient
from ..schemas import services
from typing import List

router = APIRouter(prefix="/service-providers", tags=["Services"])


@router.get("/services", response_model=List[services.ServiceBase])
def get_all_services(db: MongoClient = Depends(get_db)):
    services = []

    service_providers = db["serviceProviders"].find()

    for service_provider in service_providers:
        for service in service_provider.get("services", []):
            reviews = service.get("reviews", [])
            total_reviews = len(reviews)
            total_rating = sum(review.get("rating", 0) for review in reviews)
            avg_rating = round(
                total_rating / total_reviews if total_reviews > 0 else 0, 2
            )
            total_bookings = len(service.get("users_booked", []))

            service_data = {
                "name": service["name"],
                "description": service["description"],
                "price": service["price"],
                "category": service["category"],
                "serviceProvider": service_provider["company_name"],
                "avg_rating": avg_rating,
                "total_reviews": total_reviews,
                "total_bookings": total_bookings,
            }

            services.append(service_data)

    return services


@router.get("/{sp_username}/services", response_model=List[services.ServiceBase])
def get_services_of_service_provider(
    sp_username: str, db: MongoClient = Depends(get_db)
):
    if not sp_username.startswith("sp-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username"
        )

    db_sp = db["serviceProviders"].find_one({"username": sp_username})

    if not db_sp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service Provider not found"
        )

    services = []

    for service in db_sp["services"]:
        reviews = service.get("reviews", [])
        total_reviews = len(reviews)
        total_rating = sum(review.get("rating", 0) for review in reviews)
        avg_rating = round(total_rating / total_reviews if total_reviews > 0 else 0, 2)
        total_bookings = len(service.get("users_booked", []))

        service_data = {
            "name": service["name"],
            "description": service["description"],
            "price": service["price"],
            "category": service["category"],
            "serviceProvider": db_sp["company_name"],
            "avg_rating": avg_rating,
            "total_reviews": total_reviews,
            "total_bookings": total_bookings,
        }

        services.append(service_data)

    return services


@router.get(
    "/{sp_username}/services/{service_name}", response_model=services.ServiceBase
)
def get_service(sp_username: str, service_name: str, db: MongoClient = Depends(get_db)):
    service_provider = db["serviceProviders"].find_one({"username": sp_username})

    if not service_provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ServiceProvider '{sp_username}' not found",
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
            detail=f"Service '{service_name}' not found for serviceProvider '{sp_username}'",
        )

    reviews = matching_service.get("reviews", [])
    total_reviews = len(reviews)
    total_rating = sum(review.get("rating", 0) for review in reviews)
    avg_rating = total_rating / total_reviews if total_reviews > 0 else 0
    total_bookings = len(matching_service.get("users_booked", []))

    service_data = {
        "name": matching_service["name"],
        "description": matching_service["description"],
        "price": matching_service["price"],
        "category": matching_service["category"],
        "serviceProvider": sp_username,
        "avg_rating": avg_rating,
        "total_reviews": total_reviews,
        "total_bookings": total_bookings,
    }

    return service_data


@router.post("/{sp_username}/services")
def create_service(
    sp_username: str, service: services.ServiceBase, db: MongoClient = Depends(get_db)
):
    if db["serviceProviders"].find_one({"name": service.name}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Service already exists"
        )

    service = db["services"].insert_one(service.__dict__)

    return {"message": "Service created"}


@router.patch("/{sp_username}/services/{service_name}")
def update_service(
    sp_username: str,
    service_name: str,
    service: services.ServicesUpdate,
    db: MongoClient = Depends(get_db),
):
    if not db["services"].find_one({"id": id}):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service not found"
        )

    service = db["services"].update_one({"id": id}, {"$set": service.dict()})

    return {"message": "Service updated"}


@router.delete("/{sp_username}/services/{service_name}")
def delete_service(
    sp_username: str, service_name: str, db: MongoClient = Depends(get_db)
):
    service = db["serviceProviders"].delete_one(
        {"sp_username": sp_username}, {"services.name": service_name}
    )

    if service.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service not found"
        )

    return {"message": "Service deleted"}
