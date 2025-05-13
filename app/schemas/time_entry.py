from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from .base import BaseSchema
from .task import Task

class TimeEntryBase(BaseModel):
    task_id: UUID
    user_id: UUID
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None  # Duration in minutes

class TimeEntryCreate(TimeEntryBase):
    pass

class TimeEntryUpdate(BaseModel):
    description: Optional[str] = None
    end_time: Optional[datetime] = None
    duration: Optional[int] = None

class TimeEntry(TimeEntryBase, BaseSchema):
    task: Optional[Task] = None 