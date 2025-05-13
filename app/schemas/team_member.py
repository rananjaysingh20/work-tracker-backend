from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from enum import Enum
from .base import BaseSchema
from .user import User
from .project import Project

class TeamRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"

class TeamMemberBase(BaseModel):
    project_id: UUID
    user_id: UUID
    role: TeamRole = TeamRole.MEMBER
    is_active: bool = True

class TeamMemberCreate(TeamMemberBase):
    pass

class TeamMemberUpdate(BaseModel):
    role: Optional[TeamRole] = None
    is_active: Optional[bool] = None

class TeamMember(TeamMemberBase, BaseSchema):
    pass

class TeamMemberWithUser(TeamMember):
    user: User

class TeamMemberWithProject(TeamMember):
    project: Project

class TeamMemberWithDetails(TeamMember):
    user: User
    project: Project 