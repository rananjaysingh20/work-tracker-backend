from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from enum import Enum
from .base import BaseSchema

class ReportType(str, Enum):
    TIME_TRACKING = "time_tracking"
    PROJECT_STATS = "project_stats"
    TEAM_PRODUCTIVITY = "team_productivity"
    CLIENT_BILLING = "client_billing"

class TimeRange(str, Enum):
    TODAY = "today"
    YESTERDAY = "yesterday"
    THIS_WEEK = "this_week"
    LAST_WEEK = "last_week"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    CUSTOM = "custom"

class ReportBase(BaseModel):
    name: str
    type: ReportType
    time_range: TimeRange
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    project_ids: Optional[List[UUID]] = None
    team_member_ids: Optional[List[UUID]] = None
    client_ids: Optional[List[UUID]] = None
    include_inactive: bool = False
    group_by: Optional[str] = None  # project, team_member, client, date
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "desc"

class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    name: Optional[str] = None
    time_range: Optional[TimeRange] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    project_ids: Optional[List[UUID]] = None
    team_member_ids: Optional[List[UUID]] = None
    client_ids: Optional[List[UUID]] = None
    include_inactive: Optional[bool] = None
    group_by: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None

class Report(ReportBase, BaseSchema):
    user_id: UUID
    last_generated: Optional[datetime] = None
    data: Optional[Dict[str, Any]] = None

class TimeTrackingReport(BaseModel):
    total_hours: float
    billable_hours: float
    non_billable_hours: float
    entries: List[Dict[str, Any]]
    summary: Dict[str, Any]

class ProjectStatsReport(BaseModel):
    total_projects: int
    active_projects: int
    completed_projects: int
    total_hours: float
    billable_amount: float
    projects: List[Dict[str, Any]]

class TeamProductivityReport(BaseModel):
    total_members: int
    total_hours: float
    average_hours_per_member: float
    members: List[Dict[str, Any]]

class ClientBillingReport(BaseModel):
    total_clients: int
    total_billable_amount: float
    total_hours: float
    clients: List[Dict[str, Any]] 