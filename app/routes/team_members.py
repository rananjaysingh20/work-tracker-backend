from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any
from ..schemas.team_member import (
    TeamMember, TeamMemberCreate, TeamMemberUpdate,
    TeamMemberWithUser, TeamMemberWithProject, TeamMemberWithDetails
)
from ..schemas.user import User
from ..schemas.project import Project
from ..services.database import db
from .auth import get_current_user

router = APIRouter()

@router.get("/project/{project_id}", response_model=List[TeamMemberWithUser])
async def get_project_team_members(
    project_id: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    # Verify project exists and user has access
    project = await db.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user is a team member
    team_members = await db.get_project_team_members(project_id)
    user_is_member = any(member["user_id"] == str(current_user.id) for member in team_members)
    
    if not user_is_member and project["user_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return team_members

@router.post("/project/{project_id}", response_model=TeamMember)
async def add_team_member(
    project_id: str,
    team_member: TeamMemberCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    # Verify project exists
    project = await db.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Only project owner or admin can add team members
    team_members = await db.get_project_team_members(project_id)
    user_member = next((m for m in team_members if m["user_id"] == str(current_user.id)), None)
    
    if project["user_id"] != str(current_user.id) and (not user_member or user_member["role"] != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if user is already a team member
    existing_member = next((m for m in team_members if m["user_id"] == str(team_member.user_id)), None)
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a team member"
        )
    
    team_member_data = team_member.dict()
    team_member_data["project_id"] = project_id
    return await db.create_team_member(team_member_data)

@router.put("/{team_member_id}", response_model=TeamMember)
async def update_team_member(
    team_member_id: str,
    team_member: TeamMemberUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    existing_member = await db.get_team_member(team_member_id)
    if not existing_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )
    
    # Verify project access
    project = await db.get_project(existing_member["project_id"])
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Only project owner or admin can update team members
    team_members = await db.get_project_team_members(project["id"])
    user_member = next((m for m in team_members if m["user_id"] == str(current_user.id)), None)
    
    if project["user_id"] != str(current_user.id) and (not user_member or user_member["role"] != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    team_member_data = team_member.dict(exclude_unset=True)
    return await db.update_team_member(team_member_id, team_member_data)

@router.delete("/{team_member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_member(
    team_member_id: str,
    current_user: User = Depends(get_current_user)
) -> None:
    existing_member = await db.get_team_member(team_member_id)
    if not existing_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )
    
    # Verify project access
    project = await db.get_project(existing_member["project_id"])
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Only project owner or admin can remove team members
    team_members = await db.get_project_team_members(project["id"])
    user_member = next((m for m in team_members if m["user_id"] == str(current_user.id)), None)
    
    if project["user_id"] != str(current_user.id) and (not user_member or user_member["role"] != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Prevent removing the last admin
    if existing_member["role"] == "admin":
        admin_count = sum(1 for m in team_members if m["role"] == "admin")
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the last admin"
            )
    
    await db.delete_team_member(team_member_id) 