from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from .base import BaseSchema

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    client_id: UUID
    status: str = "active"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    client_id: Optional[UUID] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class Project(ProjectBase, BaseSchema):
    client_name: Optional[str] = None

class ProjectWithTasks(Project):
    tasks: List["Task"] = [] 