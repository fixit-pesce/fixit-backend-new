from pydantic import BaseModel, EmailStr


class ServiceProviderBase(BaseModel):
    email: EmailStr
    username: str
    company_name: str

class ServiceProviderCreate(ServiceProviderBase):
    password: str

class ServiceProviderOut(ServiceProviderBase):
    _id: str


class ServiceProviderUpdate(ServiceProviderBase):
    email: EmailStr | None
    company_name: str | None
    