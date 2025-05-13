from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any
from ..schemas.category import Category, CategoryCreate, CategoryUpdate
from ..schemas.user import User
from ..services.database import db
from .auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[Category])
async def get_categories(current_user: User = Depends(get_current_user)) -> Any:
    categories = await db.get_categories(str(current_user.id))
    return categories

@router.post("/", response_model=Category)
async def create_category(
    category: CategoryCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    category_data = category.dict()
    category_data["user_id"] = str(current_user.id)
    return await db.create_category(category_data)

@router.get("/{category_id}", response_model=Category)
async def get_category(
    category_id: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    category = await db.get_category(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    if category["user_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return category

@router.put("/{category_id}", response_model=Category)
async def update_category(
    category_id: str,
    category: CategoryUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    existing_category = await db.get_category(category_id)
    if not existing_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    if existing_category["user_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    category_data = category.dict(exclude_unset=True)
    return await db.update_category(category_id, category_data)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    current_user: User = Depends(get_current_user)
) -> None:
    category = await db.get_category(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    if category["user_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    await db.delete_category(category_id) 