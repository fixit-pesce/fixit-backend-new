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


@router.get("/most-rated-services")
def get_most_rated_services(db: MongoClient = Depends(get_db)):
    mostRatedServices = dict()

    service_providers = db["serviceProviders"].find()

    for service_provider in service_providers:
        for service in service_provider.get("services", []):
            avgRating = 0
            for review in service.get("reviews", []):
                avgRating += review.get("rating", 0)

            avgRating /= len(service.get("reviews", []))

            avgRating = round(avgRating, 2)

            if service["name"] in mostRatedServices:
                if avgRating > mostRatedServices[service["name"]]:
                    mostRatedServices[service["name"]] = avgRating
            else:
                mostRatedServices[service["name"]] = avgRating

    return mostRatedServices


@router.get("/most-booked-services")
def get_most_booked_services(db: MongoClient = Depends(get_db)):
    mostBookedServices = dict()

    bookings = db["bookings"].find()

    for booking in bookings:
        service = booking["service_name"]
        if service in mostBookedServices:
            mostBookedServices[service] += 1
        else:
            mostBookedServices[service] = 1

    return mostBookedServices


@router.get("/users-with-most-bookings")
def get_users_with_most_bookings(db: MongoClient = Depends(get_db)):
    usersWithMostBookings = dict()

    bookings = db["bookings"].find()

    for booking in bookings:
        user = booking["username"]
        if user in usersWithMostBookings:
            usersWithMostBookings[user] += 1
        else:
            usersWithMostBookings[user] = 1

    return usersWithMostBookings


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


@router.get("/most-rated-services")
def get_most_rated_services(db: MongoClient = Depends(get_db)):
    mostRatedServices = dict()

    service_providers = db["serviceProviders"].find()

    for service_provider in service_providers:
        for service in service_provider.get("services", []):
            avgRating = 0
            for review in service.get("reviews", []):
                avgRating += review.get("rating", 0)

            avgRating /= len(service.get("reviews", []))

            avgRating = round(avgRating, 2)

            if service["name"] in mostRatedServices:
                if avgRating > mostRatedServices[service["name"]]:
                    mostRatedServices[service["name"]] = avgRating
            else:
                mostRatedServices[service["name"]] = avgRating

    return mostRatedServices


@router.get("/most-booked-services")
def get_most_booked_services(db: MongoClient = Depends(get_db)):
    mostBookedServices = dict()

    bookings = db["bookings"].find()

    for booking in bookings:
        service = booking["service_name"]
        if service in mostBookedServices:
            mostBookedServices[service] += 1
        else:
            mostBookedServices[service] = 1

    return mostBookedServices


@router.get("/users-with-most-bookings")
def get_users_with_most_bookings(db: MongoClient = Depends(get_db)):
    usersWithMostBookings = dict()

    bookings = db["bookings"].find()

    for booking in bookings:
        user = booking["username"]
        if user in usersWithMostBookings:
            usersWithMostBookings[user] += 1
        else:
            usersWithMostBookings[user] = 1

    return usersWithMostBookings