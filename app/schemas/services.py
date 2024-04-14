from pydantic import BaseModel
from typing import List
from datetime import datetime


class ReviewBase(BaseModel):
    username: str
    rating: float
    description: str


class ReviewOut(ReviewBase):
    created_at: datetime
    updated_at: datetime | None = None


class FAQ(BaseModel):
    question: str
    answer: str


class Service(BaseModel):
    name: str
    description: str
    price: float
    category: str


class ServiceOut(Service):
    serviceProvider: str
    avg_rating: float
    total_reviews: int
    total_bookings: int


class ServicesUpdate(Service):
    pass
