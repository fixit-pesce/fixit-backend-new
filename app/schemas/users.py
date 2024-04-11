from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name:str

class UserIn(User):
    password: str | bytes


class UserUpdate(BaseModel):
    email: EmailStr | None = ...
    first_name: str | None = ...
    last_name: str | None = ...


class UserUpdatePassowrd(BaseModel):
    current_password: str
    new_password: str


class Review(BaseModel):
    rating: float
    description: str


class ReviewOut(Review):
    created_at: str | None = None
    updated_at: str | None = None