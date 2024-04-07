from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from .. import utils,oauth2
from ..schemas import categories

from pymongo import MongoClient
from typing import List
from ..database import get_db

router = APIRouter(
    prefix = "/categories",
    tags=['Categories'])


@router.get("/")
def get_categories(db: MongoClient = Depends(get_db)):
    categories = db["categories"].find()
    return categories


@router.post("/")
def create_category(category: categories.Category, db: MongoClient = Depends(get_db)):
    if db["categories"].find_one({"categoryName": category.categoryName}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")
    
    category = db["categories"].insert_one(category.__dict__)

    return {"message": "Category created"}


@router.delete("/{category_name}")
def delete_category(category_name: str, db: MongoClient = Depends(get_db)):
    category = db["categories"].delete_one({"categoryName": category_name})
    if category.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    return {"message": "Category deleted"}


@router.patch("/{category_name}")
def update_category(category_name: str, category: categories.Category, db: MongoClient = Depends(get_db)):
    if not db["categories"].find_one({"categoryName": category_name}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    category = db["categories"].update_one({"category_name": category_name}, {"$set": category.dict()})

    return {"message": "Category updated"}
