from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from .base import BaseSchema

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: UUID
    status: str = "todo"
    priority: str = "medium"
    assigned_to: Optional[UUID] = None
    due_date: Optional[datetime] = None
    category_id: Optional[UUID] = None

    @validator('due_date', pre=True)
    def parse_due_date(cls, value):
        if isinstance(value, str) and value:
            # If the string contains only a date (no time component)
            if 'T' not in value and ' ' not in value:
                return datetime.strptime(value, '%Y-%m-%d')
        return value

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[UUID] = None
    due_date: Optional[datetime] = None
    category_id: Optional[UUID] = None

    @validator('due_date', pre=True)
    def parse_due_date(cls, value):
        if isinstance(value, str) and value:
            # If the string contains only a date (no time component)
            if 'T' not in value and ' ' not in value:
                return datetime.strptime(value, '%Y-%m-%d')
        return value

class Task(TaskBase, BaseSchema):
    pass

class TaskWithTimeEntries(Task):
    time_entries: List["TimeEntry"] = [] 