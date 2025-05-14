from pydantic import BaseModel, Field, validator
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

    @validator('start_date', 'end_date', pre=True)
    def parse_dates(cls, value):
        if isinstance(value, str):
            try:
                # First try parsing as datetime
                return datetime.fromisoformat(value)
            except ValueError:
                try:
                    # If that fails, try parsing as date and convert to datetime
                    return datetime.strptime(value, '%Y-%m-%d')
                except ValueError:
                    raise ValueError("Invalid date format. Expected YYYY-MM-DD or ISO datetime format")
        return value

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