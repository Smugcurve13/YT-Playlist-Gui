from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from helpers.file_utils import get_media_path
import os

router = APIRouter()

@router.get("/download/{file_id}")
async def download_file(file_id: str):
    file_path = get_media_path(file_id)
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="application/octet-stream", filename=file_id)