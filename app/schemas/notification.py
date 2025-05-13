from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum
from .base import BaseSchema

class NotificationType(str, Enum):
    TASK_ASSIGNED = "task_assigned"
    TASK_UPDATED = "task_updated"
    TASK_COMPLETED = "task_completed"
    TIME_ENTRY_ADDED = "time_entry_added"
    TIME_ENTRY_UPDATED = "time_entry_updated"
    PROJECT_UPDATED = "project_updated"
    TEAM_MEMBER_ADDED = "team_member_added"
    TEAM_MEMBER_REMOVED = "team_member_removed"
    CLIENT_UPDATED = "client_updated"
    REPORT_GENERATED = "report_generated"

class NotificationChannel(str, Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    BOTH = "both"

class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class NotificationBase(BaseModel):
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.MEDIUM
    data: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    user_id: UUID
    channel: NotificationChannel = NotificationChannel.IN_APP

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_archived: Optional[bool] = None

class Notification(NotificationBase, BaseSchema):
    user_id: UUID
    channel: NotificationChannel
    is_read: bool = False
    is_archived: bool = False
    read_at: Optional[datetime] = None

class NotificationPreferenceBase(BaseModel):
    task_assigned: NotificationChannel = NotificationChannel.BOTH
    task_updated: NotificationChannel = NotificationChannel.IN_APP
    task_completed: NotificationChannel = NotificationChannel.IN_APP
    time_entry_added: NotificationChannel = NotificationChannel.IN_APP
    time_entry_updated: NotificationChannel = NotificationChannel.IN_APP
    project_updated: NotificationChannel = NotificationChannel.BOTH
    team_member_added: NotificationChannel = NotificationChannel.BOTH
    team_member_removed: NotificationChannel = NotificationChannel.BOTH
    client_updated: NotificationChannel = NotificationChannel.IN_APP
    report_generated: NotificationChannel = NotificationChannel.EMAIL

class NotificationPreferenceCreate(NotificationPreferenceBase):
    user_id: UUID

class NotificationPreferenceUpdate(BaseModel):
    task_assigned: Optional[NotificationChannel] = None
    task_updated: Optional[NotificationChannel] = None
    task_completed: Optional[NotificationChannel] = None
    time_entry_added: Optional[NotificationChannel] = None
    time_entry_updated: Optional[NotificationChannel] = None
    project_updated: Optional[NotificationChannel] = None
    team_member_added: Optional[NotificationChannel] = None
    team_member_removed: Optional[NotificationChannel] = None
    client_updated: Optional[NotificationChannel] = None
    report_generated: Optional[NotificationChannel] = None

class NotificationPreference(NotificationPreferenceBase, BaseSchema):
    user_id: UUID 