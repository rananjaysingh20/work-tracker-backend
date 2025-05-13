from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from typing import List, Any
from uuid import UUID
from ..services.database import db
from ..schemas.user import User
from .auth import get_current_user_and_token
import uuid

router = APIRouter()

@router.post("/clients/{client_id}/files", status_code=201)
async def upload_client_file(
    client_id: UUID,
    file: UploadFile = File(...),
    user_and_token: tuple = Depends(get_current_user_and_token)
) -> Any:
    current_user, token = user_and_token
    file_id = str(uuid.uuid4())
    file_ext = file.filename.split('.')[-1]
    storage_path = f"client_files/{client_id}/{file_id}.{file_ext}"
    content = await file.read()
    from ..services.database import supabase_storage
    # Set the user's JWT for RLS
    supabase_storage.auth.session = token
    res = supabase_storage.storage.from_("client-files").upload(storage_path, content, {"content-type": file.content_type})
    if not res:
        raise HTTPException(status_code=500, detail="Failed to upload file to storage.")
    public_url = supabase_storage.storage.from_("client-files").get_public_url(storage_path)
    if not public_url:
        raise HTTPException(status_code=500, detail="Failed to get public URL for file.")
    file_record = await db.create_client_file({
        "client_id": str(client_id),
        "file_name": file.filename,
        "file_url": public_url
    })
    return file_record

@router.get("/clients/{client_id}/files", response_model=List[dict])
async def list_client_files(
    client_id: UUID,
    user_and_token: tuple = Depends(get_current_user_and_token)
) -> Any:
    files = await db.get_client_files(str(client_id))
    return files

@router.delete("/clients/{client_id}/files/{file_id}", status_code=204)
async def delete_client_file(
    client_id: UUID,
    file_id: UUID,
    user_and_token: tuple = Depends(get_current_user_and_token)
) -> None:
    current_user, token = user_and_token
    # Look up the file record
    files = await db.get_client_files(str(client_id))
    file_record = next((f for f in files if str(f['id']) == str(file_id)), None)
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    # Parse the file extension from the file name
    file_ext = file_record['file_name'].split('.')[-1]
    storage_path = f"client_files/{client_id}/{file_id}.{file_ext}"
    from ..services.database import supabase_storage
    supabase_storage.auth.session = token
    # Delete from Supabase Storage
    res = supabase_storage.storage.from_("client-files").remove([storage_path])
    if res and isinstance(res, list) and len(res) > 0:
        raise HTTPException(status_code=500, detail=f"Failed to delete file from storage: {res}")
    # Delete from DB
    await db.delete_client_file(str(file_id))
    return 