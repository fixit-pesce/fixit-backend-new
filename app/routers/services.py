from fastapi import APIRouter, Depends, HTTPException, status
from ..database import get_db
from pymongo import MongoClient
from ..schemas import services
from typing import List


router = APIRouter(
    prefix = "/services",
    tags=['Services']
)


@router.get("/", response_model=List[services.ServiceOut])
def get_services(db: MongoClient = Depends(get_db)):
    services = db["services"].find()
    return services


@router.get("/{service_id}", response_model=services.ServiceOut)
def get_service(service_id: str, db: MongoClient = Depends(get_db)):
    service = db["services"].find_one({"id": id})
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return service


@router.post("/")
def create_service(service: services.ServiceBase, db: MongoClient = Depends(get_db)):
    if db["services"].find_one({"name": service.name}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Service already exists")
    
    service = db["services"].insert_one(service.__dict__)

    return {"message": "Service created"}


# @router.patch("/{id}")
# def update_service(id: int, service: services.ServicesUpdate, db: MongoClient = Depends(get_db)):
#     if not db["services"].find_one({"id": id}):
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    
#     service = db["services"].update_one({"id": id}, {"$set": service.dict()})

#     return {"message": "Service updated"}


@router.delete("/{id}")
def delete_service(id: int, db: MongoClient = Depends(get_db)):
    service = db["services"].delete_one({"id": id})
    if service.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    
    return {"message": "Service deleted"}