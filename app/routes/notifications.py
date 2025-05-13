from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Any, Optional
from ..schemas.notification import (
    Notification, NotificationCreate, NotificationUpdate,
    NotificationPreference, NotificationPreferenceCreate,
    NotificationPreferenceUpdate
)
from ..schemas.user import User
from ..services.database import db
from .auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[Notification])
async def get_notifications(
    is_read: Optional[bool] = None,
    is_archived: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user)
) -> Any:
    return await db.get_user_notifications(
        str(current_user.id),
        is_read=is_read,
        is_archived=is_archived,
        limit=limit,
        offset=offset
    )

@router.post("/", response_model=Notification)
async def create_notification(
    notification: NotificationCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    # Only allow creating notifications for the current user
    if str(notification.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create notifications for other users"
        )
    
    notification_data = notification.dict()
    return await db.create_notification(notification_data)

@router.get("/{notification_id}", response_model=Notification)
async def get_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    notification = await db.get_notification(notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    if notification["user_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return notification

@router.put("/{notification_id}", response_model=Notification)
async def update_notification(
    notification_id: str,
    notification: NotificationUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    existing_notification = await db.get_notification(notification_id)
    if not existing_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    if existing_notification["user_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    notification_data = notification.dict(exclude_unset=True)
    return await db.update_notification(notification_id, notification_data)

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user)
) -> None:
    notification = await db.get_notification(notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    if notification["user_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    await db.delete_notification(notification_id)

@router.post("/mark-read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_notifications_as_read(
    notification_ids: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user)
) -> None:
    await db.mark_notifications_as_read(str(current_user.id), notification_ids)

@router.post("/archive", status_code=status.HTTP_204_NO_CONTENT)
async def archive_notifications(
    notification_ids: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user)
) -> None:
    await db.archive_notifications(str(current_user.id), notification_ids)

@router.get("/preferences", response_model=NotificationPreference)
async def get_notification_preferences(
    current_user: User = Depends(get_current_user)
) -> Any:
    preferences = await db.get_notification_preference(str(current_user.id))
    if not preferences:
        # Create default preferences if they don't exist
        default_preferences = NotificationPreferenceCreate(user_id=current_user.id)
        preferences = await db.create_notification_preference(default_preferences.dict())
    return preferences

@router.post("/preferences", response_model=NotificationPreference)
async def create_notification_preferences(
    preferences: NotificationPreferenceCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    # Only allow creating preferences for the current user
    if str(preferences.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create preferences for other users"
        )
    
    # Check if preferences already exist
    existing_preferences = await db.get_notification_preference(str(current_user.id))
    if existing_preferences:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Notification preferences already exist"
        )
    
    preferences_data = preferences.dict()
    return await db.create_notification_preference(preferences_data)

@router.put("/preferences", response_model=NotificationPreference)
async def update_notification_preferences(
    preferences: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    existing_preferences = await db.get_notification_preference(str(current_user.id))
    if not existing_preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification preferences not found"
        )
    
    preferences_data = preferences.dict(exclude_unset=True)
    return await db.update_notification_preference(str(current_user.id), preferences_data) 