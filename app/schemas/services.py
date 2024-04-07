from pydantic import BaseModel
from typing import List
from pymongo import MongoClient


class ReviewBase(BaseModel):
    username: str
    rating: float
    description: str

    
class ReviewOut(ReviewBase):
    created_at: str
    updated_at: str

class FAQ(BaseModel):
    question: str
    answer: str


class ServiceBase(BaseModel):
    name: str
    description: str
    price: float
    category: str
    serviceProvider: str
    avg_rating: float | None = 0
    total_reviews: int | None = 0
    total_bookings: int | None = 0


class ServiceOut(ServiceBase):
    _id: str
    reviews: List[ReviewOut] | None = None