from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from helpers.downloader import download_playlist
from helpers.job_manager import create_job

router = APIRouter()

class PlaylistRequest(BaseModel):
    url: str
    format: str
    quality: str = None

@router.post("/convert/playlist")
async def convert_playlist(request: PlaylistRequest, background_tasks: BackgroundTasks):
    job_id = create_job()
    background_tasks.add_task(download_playlist, request.url, request.format, request.quality, job_id)
    return {"job_id": job_id}