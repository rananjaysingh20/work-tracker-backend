from pydantic import BaseModel, Field
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

class Task(TaskBase, BaseSchema):
    pass

class TaskWithTimeEntries(Task):
    time_entries: List["TimeEntry"] = [] 