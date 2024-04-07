from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from .. import utils,oauth2
from ..schemas import serviceProviders

from pymongo import MongoClient
from typing import List
from ..database import get_db


router = APIRouter(
    prefix = "/service-providers",
    tags=['Service Providers']
)


@router.get("/", response_model=List[serviceProviders.ServiceProviderOut])
def get_service_providers(db: MongoClient = Depends(get_db)):
    serviceProviders = db["serviceProviders"].find()
    return serviceProviders


@router.get("/{username}", response_model=serviceProviders.ServiceProviderOut)
def get_service_provider(username: str, db: MongoClient = Depends(get_db)):
    serviceProvider = db["serviceProviders"].find_one({"username": username})
    if not serviceProvider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service Provider not found")
    return serviceProvider


@router.post("/", status_code = status.HTTP_201_CREATED)
def create_service_provider(serviceProvider: serviceProviders.ServiceProviderCreate, db: MongoClient = Depends(get_db)):
    if not serviceProvider.username.startswith("sp-"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid username format")
    
    if db["serviceProviders"].find_one({"username": serviceProvider.username}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    if db["serviceProviders"].find_one({"serviceProviderName": serviceProvider.company_name}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Service Provider already exists")
    
    serviceProvider = db["serviceProviders"].insert_one(serviceProvider.__dict__)

    return {"message": "Service Provider created"}


@router.delete("/{username}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service_provider(username: str, db: MongoClient = Depends(get_db)):
    serviceProvider = db["serviceProviders"].delete_one({"username": username})
    if serviceProvider.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service Provider not found")
    
    return {"message": "Service Provider deleted"}


@router.patch("/{username}", status_code=status.HTTP_200_OK)
def update_service_provider(username: str, serviceProvider: serviceProviders.ServiceProviderUpdate, db: MongoClient = Depends(get_db)):
    if not db["serviceProviders"].find_one({"username": username}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service Provider not found")
    
    existing_provider = db["serviceProviders"].find_one({"company_name": serviceProvider.company_name})

    if existing_provider:
        # Check if the existing company name corresponds to the same service provider
        if existing_provider["username"] != username:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Service Provider already exists")
        

    existing_provider = db["serviceProviders"].find_one({"email": serviceProvider.email})

    if existing_provider:
        # Check if the existing email corresponds to the same service provider
        if existing_provider["username"] != username:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists for another service provider")

    
    serviceProvider = db["serviceProviders"].update_one({"username": username}, {"$set": serviceProvider.dict()})

    return {"message": "Service Provider updated"}