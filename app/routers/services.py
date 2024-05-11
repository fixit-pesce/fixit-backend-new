from fastapi import APIRouter, Depends, HTTPException, status
from ..database import get_db
from datetime import datetime, UTC
from pymongo import MongoClient
from ..schemas import services
from typing import List
import shortuuid

router = APIRouter(prefix="/service-providers", tags=["Services"])


@router.get("/services", response_model=List[services.ServiceOut])
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
                "serviceProvider": service_provider["username"],
                "spCompanyName": service_provider["company_name"],
                "avg_rating": avg_rating,
                "total_reviews": total_reviews,
                "total_bookings": total_bookings,
                "location": service["location"],
            }

            services.append(service_data)

    return services


@router.get("/{sp_username}/services", response_model=List[services.ServiceOut])
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

    for service in db_sp.get("services", []):
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
            "serviceProvider": sp_username,
            "spCompanyName": db_sp["company_name"],
            "location": service["location"],
            "avg_rating": avg_rating,
            "total_reviews": total_reviews,
            "total_bookings": total_bookings,
        }

        services.append(service_data)

    return services


@router.get(
    "/{sp_username}/services/{service_name}", response_model=services.ServiceOut
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
        "spCompanyName": service_provider["company_name"],
        "location": matching_service["location"],
        "avg_rating": avg_rating,
        "total_reviews": total_reviews,
        "total_bookings": total_bookings,
    }

    return service_data


@router.post("/{sp_username}/services")
def create_service(
    sp_username: str, service: services.Service, db: MongoClient = Depends(get_db)
):

    service_provider = db["serviceProviders"].find_one({"username": sp_username})

    if not service_provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ServiceProvider '{sp_username}' not found",
        )

    service_data = service.__dict__
    service_data["name"] = service.name
    service_data["description"] = service.description
    service_data["price"] = service.price
    service_data["category"] = service.category
    service_data["location"] = {
        "locality": service.location.locality,
        "city": service.location.city,
    }
    service_data["avg_rating"] = 0
    service_data["total_reviews"] = 0
    service_data["total_bookings"] = 0

    db["serviceProviders"].update_one(
        {"username": sp_username}, {"$push": {"services": service_data}}
    )

    return {"message": "Service created"}


@router.put("/{sp_username}/services/{service_name}")
def update_service(
    sp_username: str,
    service_name: str,
    serviceIn: services.ServicesUpdate,
    db: MongoClient = Depends(get_db),
):
    service_provider = db["serviceProviders"].find_one({"username": sp_username})

    if not service_provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ServiceProvider '{sp_username}' not found",
        )

    index = None
    for i, service in enumerate(service_provider["services"]):
        if service.get("name") == service_name:
            index = i
            break

    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with ID '{service_name}' not found",
        )

    update_fields = {
        key: value for key, value in serviceIn.dict().items() if value is not None
    }

    update_query = {
        "$set": {
            f"services.$[elem].{key}": value for key, value in update_fields.items()
        },
    }

    db["serviceProviders"].update_one(
        {"username": sp_username},
        update_query,
        array_filters=[{"elem.name": service_name}],
    )

    if db.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with name '{service_name}' not found",
        )

    return {"message": "Service updated"}


@router.delete("/{sp_username}/services/{service_name}")
def delete_service(
    sp_username: str, service_name: str, db: MongoClient = Depends(get_db)
):
    service = db["serviceProviders"].update_one(
        {"username": sp_username}, {"$pull": {"services": {"name": service_name}}}
    )

    if service.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service not found"
        )

    
    return {"message": "Service deleted"}


@router.post("/{sp_username}/services/{service_name}/bookings", status_code=status.HTTP_201_CREATED)
def book_service(sp_username: str, service_name: str, booking: services.BookServiceIn, db: MongoClient = Depends(get_db)):
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

    new_booking = booking.model_dump()
    new_booking["booked_at"] = datetime.now(UTC)
    new_booking["completed_at"] = None
    new_booking["status"] = "PENDING"
    new_booking["booking_id"] = shortuuid.uuid()
    new_booking["sp_username"] = sp_username

    db["bookings"].insert_one(new_booking)

    return {"message": "Service booked successfully"}


@router.get("/{sp_username}/services/{service_name}/bookings", response_model=List[services.BookService])
def get_service_bookings(sp_username: str, service_name: str, db: MongoClient = Depends(get_db)):
    bookings = db["bookings"].find({"sp_username": sp_username, "service_name": service_name})

    if not bookings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No bookings found for serviceProvider '{sp_username}'",
        )

    return bookings

@router.post("/bookings/{booking_id}/approve")
def approve_service_booking(booking_id: str, db: MongoClient = Depends(get_db)):
    booking = db["bookings"].find_one({"booking_id": booking_id})

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID '{booking_id}' not found",
        )

    db["bookings"].update_one(
        {"booking_id": booking_id}, {"$set": {"status": "APPROVED"}}
    )

    return {"message": "Booking approved"}


@router.post("/bookings/{booking_id}/complete")
def complete_service_booking(booking_id: str, db: MongoClient = Depends(get_db)):
    booking = db["bookings"].find_one({"booking_id": booking_id})

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID '{booking_id}' not found",
        )

    db["bookings"].update_one(
        {"booking_id": booking_id}, {"$set": {"status": "COMPLETED", "completed_at": datetime.now(UTC)}}
    )    

    return {"message": "Booking completed"}


@router.post("/bookings/{booking_id}/cancel")
def cancel_service_booking(booking_id: str, db: MongoClient = Depends(get_db)):
    booking = db["bookings"].find_one({"booking_id": booking_id})

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID '{booking_id}' not found",
        )

    db["bookings"].update_one(
        {"booking_id": booking_id}, {"$set": {"status": "CANCELLED"}}
    )

    return {"message": "Booking cancelled"}