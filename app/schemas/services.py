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


class ServiceBase(BaseModel):
    name: str
    description: str
    price: float
    category: str
    serviceProvider: str
    avg_rating: float | None = 0
    total_reviews: int | None = 0
    total_bookings: int | None = 0


class ServicesUpdate(ServiceBase):
    pass