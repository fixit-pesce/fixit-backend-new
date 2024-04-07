from pydantic import BaseModel

class Category(BaseModel):
    category_name: str
    icon: str