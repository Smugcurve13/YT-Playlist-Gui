from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from helpers.downloader import download_and_convert

router = APIRouter()

class ConvertRequest(BaseModel):
    url: str
    format: str
    quality: str = None

@router.post("/convert")
async def convert(request: ConvertRequest, background_tasks: BackgroundTasks):
    try:
        file_path = download_and_convert(request.url, request.format, request.quality)
        return {"status": "success", "download_url": f"/api/download/{file_path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))