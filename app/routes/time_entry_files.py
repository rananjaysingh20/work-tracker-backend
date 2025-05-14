from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from uuid import UUID
from ..services.database import db, supabase_storage
from .auth import get_current_user_and_token
from ..schemas.user import User
import uuid
import datetime

router = APIRouter(tags=["time_entry_files"])

BUCKET_NAME = "task-files"

@router.post("/time-entries/{time_entry_id}/files")
async def upload_time_entry_file(
    time_entry_id: UUID,
    file: UploadFile = File(...),
    user_and_token: tuple = Depends(get_current_user_and_token)
):
    current_user, token = user_and_token

    # Save file to Supabase Storage
    file_ext = file.filename.split('.')[-1]
    file_id = str(uuid.uuid4())
    storage_path = f"{time_entry_id}/{file_id}.{file_ext}"

    supabase_storage.auth.session = token
    content = await file.read()
    try:
        res = supabase_storage.storage.from_(BUCKET_NAME).upload(storage_path, content, {"content-type": file.content_type})
        if hasattr(res, 'error') and res.error:
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {res.error.message}")
    except Exception as e:
        raise HTTPException(status_code=413, detail=str(e))

    file_url = f"{supabase_storage.storage_url}/object/public/{BUCKET_NAME}/{storage_path}"

    # Save file record in DB
    file_record = {
        "id": file_id,
        "time_entry_id": str(time_entry_id),
        "file_name": file.filename,
        "file_url": file_url,
        "uploaded_at": datetime.datetime.utcnow().isoformat(),
        "user_id": str(current_user.id),
    }
    db.supabase.table("time_entry_files").insert(file_record).execute()
    return file_record

@router.get("/time-entries/{time_entry_id}/files")
async def list_time_entry_files(
    time_entry_id: UUID,
    user_and_token: tuple = Depends(get_current_user_and_token)
):
    # Only allow access if user owns the time entry (optional: add check)
    files = db.supabase.table("time_entry_files").select("*").eq("time_entry_id", str(time_entry_id)).order("uploaded_at", desc=True).execute()
    return files.data

@router.delete("/time-entries/{time_entry_id}/files/{file_id}")
async def delete_time_entry_file(
    time_entry_id: UUID,
    file_id: UUID,
    user_and_token: tuple = Depends(get_current_user_and_token)
):
    current_user, token = user_and_token

    # Get file record
    files = db.supabase.table("time_entry_files").select("*").eq("id", str(file_id)).execute()
    file_record = files.data[0] if files.data else None
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    # Delete from Supabase Storage
    file_ext = file_record['file_name'].split('.')[-1]
    storage_path = f"{time_entry_id}/{file_id}.{file_ext}"
    supabase_storage.auth.session = token
    res = supabase_storage.storage.from_(BUCKET_NAME).remove([storage_path])
    if res and isinstance(res, list) and len(res) > 0:
        raise HTTPException(status_code=500, detail=f"Failed to delete file from storage: {res}")

    # Delete from DB
    db.supabase.table("time_entry_files").delete().eq("id", str(file_id)).execute()
    return {"message": "File deleted"} 