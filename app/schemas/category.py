from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from .base import BaseSchema

class CategoryBase(BaseModel):
    name: str
    color: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None

class Category(CategoryBase, BaseSchema):
    pass 