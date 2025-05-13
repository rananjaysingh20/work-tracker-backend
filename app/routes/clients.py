from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any
from ..schemas.client import Client, ClientCreate, ClientUpdate, ClientWithProjects
from ..schemas.user import User
from ..services.database import db
from .auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[Client])
async def get_clients(current_user: User = Depends(get_current_user)) -> Any:
    clients = await db.get_clients(str(current_user.id))
    return clients

@router.post("/", response_model=Client)
async def create_client(
    client: ClientCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    client_data = client.dict()
    client_data["user_id"] = str(current_user.id)
    return await db.create_client(client_data)

@router.get("/{client_id}", response_model=Client)
async def get_client(
    client_id: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    client = await db.get_client(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    if client["user_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return client

@router.get("/{client_id}/projects", response_model=ClientWithProjects)
async def get_client_with_projects(
    client_id: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    client = await db.get_client(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    if client["user_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    projects = await db.get_client_projects(client_id)
    client["projects"] = projects
    return client

@router.put("/{client_id}", response_model=Client)
async def update_client(
    client_id: str,
    client: ClientUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    existing_client = await db.get_client(client_id)
    if not existing_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    if existing_client["user_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    client_data = client.dict(exclude_unset=True)
    return await db.update_client(client_id, client_data)

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: str,
    current_user: User = Depends(get_current_user)
) -> None:
    client = await db.get_client(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    if client["user_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if client has any projects
    projects = await db.get_client_projects(client_id)
    if projects:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete client with existing projects"
        )
    
    await db.delete_client(client_id) 