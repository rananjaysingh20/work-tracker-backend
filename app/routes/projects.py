from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any
from ..schemas.project import Project, ProjectCreate, ProjectUpdate
from ..schemas.user import User
from ..services.database import db
from .auth import get_current_user
from postgrest.exceptions import APIError

router = APIRouter()

@router.get("/", response_model=List[Project])
async def get_projects(current_user: User = Depends(get_current_user)) -> Any:
    projects = await db.get_projects(str(current_user.id))
    return projects

@router.post("/", response_model=Project)
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    project_data = project.dict()
    project_data["user_id"] = str(current_user.id)
    return await db.create_project(project_data)

@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    project = await db.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if project["user_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return project

@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    project: ProjectUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    existing_project = await db.get_project(project_id)
    if not existing_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if existing_project["user_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    project_data = project.dict(exclude_unset=True)
    return await db.update_project(project_id, project_data)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user)
) -> None:
    project = await db.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if project["user_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        await db.delete_project(project_id)
    except APIError as e:
        error_data = e.json()
        if error_data.get('code') == '23503' and 'tasks_project_id_fkey' in error_data.get('message', ''):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete project because it has associated tasks. Please delete or reassign the tasks first."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project. Please try again."
        ) 