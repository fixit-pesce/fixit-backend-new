from fastapi import APIRouter, Depends, HTTPException, status

from .. import utils
from ..schemas import users, services

from pymongo import MongoClient
from typing import List
from ..database import get_db

from datetime import datetime, UTC

router = APIRouter(
    prefix = "/users",
    tags=['Users'])

@router.get("/", response_model=List[users.User])
def get_users(db: MongoClient = Depends(get_db)):
    users = db["users"].find()
    return users


@router.get("/{username}", response_model=users.User)
def get_user(username: str, db: MongoClient = Depends(get_db)):
    user = db["users"].find_one({"username": username})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/", status_code = status.HTTP_201_CREATED)
def create_user(user: users.UserIn, db: MongoClient = Depends(get_db)):
    if db["users"].find_one({"username": user.username}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    
    if db["users"].find_one({"email": user.email}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    
    user.password = utils.hash(user.password)

    user = db["users"].insert_one(user.__dict__)

    return {"message": "User created"}

@router.delete("/{username}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(username: str, db: MongoClient = Depends(get_db)):
    user = db["users"].delete_one({"username": username})
    if user.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return {"message": "User deleted"}


@router.patch("/{username}")
def update_user(username: str, user: users.UserUpdate, db: MongoClient = Depends(get_db)):
    if not db["users"].find_one({"username": username}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User with username {username} does not exists")
    
    db_user = db["users"].find_one({"email": user.email})
    
    if not db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User with email {email} does not exist")
    
    if db_user["username"] != username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists for another user")

    user = db["users"].update_one({"username": username}, {"$set": user.model_dump()})

    return {"message": "User updated"}


@router.post("/{username}/booked-services")
def get_user_services(username: str, db: MongoClient = Depends(get_db)):
    user = db["users"].find_one({"username": username})
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user.get("bookings", [])


@router.get("/{username}/reviews", response_model=List[users.ReviewOut])
def user_get_reviews(username: str, db: MongoClient = Depends(get_db)):
    user = db["users"].find_one({"username": username})
    return user["reviews"]


@router.post("/{username}/reviews")
def user_write_review(username: str, review: users.Review, db: MongoClient = Depends(get_db)):
    review = review.__dict__
    review["created_at"] = datetime.now(UTC)
    db["users"].update_one({"username": username}, {"$push": {"reviews": review.__dict__}})
    return {"message": "Review inserted sucessfully"}