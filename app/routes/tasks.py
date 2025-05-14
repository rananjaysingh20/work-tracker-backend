from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..schemas.task import Task, TaskCreate, TaskUpdate
from ..services.database import db
from .auth import get_current_user
from ..schemas.user import User
from postgrest.exceptions import APIError
from datetime import datetime

router = APIRouter(tags=["tasks"])

@router.get("/project/{project_id}", response_model=List[Task])
async def get_project_tasks(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all tasks for a specific project"""
    try:
        tasks = await db.get_project_tasks(project_id)
        
        # Ensure due_date is returned as a datetime object
        for task in tasks:
            if 'due_date' in task and isinstance(task['due_date'], str):
                task['due_date'] = datetime.fromisoformat(task['due_date'])
        
        return tasks
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/project/{project_id}", response_model=Task)
async def create_task(
    project_id: str,
    task: TaskCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new task for a project"""
    try:
        # Check project ownership
        project = await db.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if project["user_id"] != str(current_user.id):
            raise HTTPException(status_code=403, detail="You do not have permission to add tasks to this project.")
        
        # Convert task to dict and ensure datetime is properly formatted
        task_data = task.dict()
        if task_data.get('due_date'):
            task_data['due_date'] = db.to_serializable(task_data['due_date'])
            
        result = await db.create_task(project_id, task_data)
        return result
    except Exception as e:
        import traceback
        print('Error creating task:', e)
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/active", response_model=List[Task])
async def get_active_tasks(current_user: User = Depends(get_current_user)):
    """Get all active tasks for all projects of the current user"""
    print(f"Getting active tasks for user: {current_user.id}")
    projects = await db.get_projects(str(current_user.id))
    project_ids = [p['id'] for p in projects]
    if not project_ids:
        return []
    active_tasks = await db.get_active_tasks_for_projects(project_ids)
    
    # Ensure due_date is returned as a datetime object
    for task in active_tasks:
        if 'due_date' in task and isinstance(task['due_date'], str):
            task['due_date'] = datetime.fromisoformat(task['due_date'])
    
    return active_tasks

@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific task by ID"""
    try:
        task = await db.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: str,
    task: TaskUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a task"""
    try:
        # Convert task to dict and ensure datetime is properly formatted
        task_data = task.dict(exclude_unset=True)
        if task_data.get('due_date'):
            task_data['due_date'] = db.to_serializable(task_data['due_date'])
            
        updated_task = await db.update_task(task_id, task_data)
        if not updated_task:
            raise HTTPException(status_code=404, detail="Task not found")
        return updated_task
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a task"""
    try:
        success = await db.delete_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"message": "Task deleted successfully"}
    except APIError as e:
        error_data = e.json()
        if error_data.get('code') == '23503' and 'time_entries_task_id_fkey' in error_data.get('message', ''):
            raise HTTPException(
                status_code=400,
                detail="Cannot delete task because it has associated time entries. Please delete or reassign the time entries first."
            )
        raise HTTPException(status_code=500, detail="Failed to delete task. Please try again.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))