from fastapi import APIRouter, HTTPException
from helpers.job_manager import get_job_status

router = APIRouter()

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    status = get_job_status(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return status