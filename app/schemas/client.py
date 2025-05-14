from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from uuid import UUID
from .base import BaseSchema
from .project import Project

class ClientBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None

class Client(ClientBase, BaseSchema):
    pass

class ClientWithProjects(Client):
    projects: List[Project] = [] 