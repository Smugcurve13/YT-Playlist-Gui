from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List
from helpers.downloader import download_batch
from helpers.job_manager import create_job

router = APIRouter()

class BatchRequest(BaseModel):
    urls: List[str]
    format: str
    quality: str = None

@router.post("/convert/batch")
async def convert_batch(request: BatchRequest, background_tasks: BackgroundTasks):
    job_id = create_job()
    background_tasks.add_task(download_batch, request.urls, request.format, request.quality, job_id)
    return {"job_id": job_id}