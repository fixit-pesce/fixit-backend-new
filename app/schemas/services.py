from pydantic import BaseModel
from datetime import datetime


class ReviewBase(BaseModel):
    username: str
    rating: float
    description: str


class ReviewOut(ReviewBase):
    company_name: str
    created_at: datetime
    updated_at: datetime | None = None


class FAQ(BaseModel):
    question: str
    answer: str


class Location (BaseModel):
    locality: str
    city: str

class Service(BaseModel):
    name: str
    description: str
    price: float
    category: str
    location: Location


class ServiceOut(Service):
    serviceProvider: str
    spCompanyName: str
    avg_rating: float
    total_reviews: int
    total_bookings: int


class ServicesUpdate(Service):
    pass


class BookServiceIn(BaseModel):
    service_name: str
    company_name: str
    category: str
    price: int
    username: str
    phone_no: str
    payment_method: dict


class BookService(BookServiceIn):
    booking_id: str
    status: str
    booked_at: datetime
    completed_at: datetime | None