from api import convert, playlist, batch, status, download
from fastapi import APIRouter

router = APIRouter()

router.include_router(convert.router, prefix="/api")
router.include_router(playlist.router, prefix="/api")
router.include_router(batch.router, prefix="/api")
router.include_router(status.router, prefix="/api")
router.include_router(download.router, prefix="/api")
