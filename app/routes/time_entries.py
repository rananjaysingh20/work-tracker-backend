from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any
from ..schemas.time_entry import TimeEntry, TimeEntryCreate, TimeEntryUpdate
from ..schemas.user import User
from ..services.database import db
from .auth import get_current_user
from datetime import datetime

router = APIRouter()

@router.get("/task/{task_id}", response_model=List[TimeEntry])
async def get_time_entries(
    task_id: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    # Verify task exists and user has access
    task = await db.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Verify project access
    project = await db.get_project(task["project_id"])
    if project["user_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    time_entries = await db.get_task_time_entries(task_id)
    return time_entries

@router.post("/task/{task_id}", response_model=TimeEntry)
async def create_time_entry(
    task_id: str,
    time_entry: TimeEntryCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    # Verify task exists and user has access
    task = await db.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Verify project access
    project = await db.get_project(task["project_id"])
    if project["user_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    def to_iso(val):
        if isinstance(val, datetime):
            return val.isoformat()
        return val
    time_entry_data = {k: to_iso(v) for k, v in time_entry.dict().items()}
    time_entry_data["task_id"] = task_id
    time_entry_data["user_id"] = str(current_user.id)
    return await db.create_time_entry(task_id, time_entry_data)

@router.put("/{time_entry_id}", response_model=TimeEntry)
async def update_time_entry(
    time_entry_id: str,
    time_entry: TimeEntryUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    # Get existing time entry
    existing_entry = await db.get_time_entry(time_entry_id)
    if not existing_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found"
        )
    
    # Verify task exists and user has access
    task = await db.get_task(existing_entry["task_id"])
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Verify project access
    project = await db.get_project(task["project_id"])
    if project["user_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Verify user owns the time entry
    if existing_entry["user_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    time_entry_data = time_entry.dict(exclude_unset=True)
    return await db.update_time_entry(time_entry_id, time_entry_data)

@router.delete("/{time_entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_time_entry(
    time_entry_id: str,
    current_user: User = Depends(get_current_user)
) -> None:
    # Get existing time entry
    existing_entry = await db.get_time_entry(time_entry_id)
    if not existing_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found"
        )
    
    # Verify task exists and user has access
    task = await db.get_task(existing_entry["task_id"])
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Verify project access
    project = await db.get_project(task["project_id"])
    if project["user_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Verify user owns the time entry
    if existing_entry["user_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    await db.delete_time_entry(time_entry_id) 