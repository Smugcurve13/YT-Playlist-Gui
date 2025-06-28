import os
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import yt_dlp
import ffmpeg
from utils import (
    ensure_media_dir, sanitize_filename, generate_uuid_filename,
    get_media_path, cleanup_file
)

app = FastAPI()
ensure_media_dir()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

class ConvertRequest(BaseModel):
    url: str
    format: str  # "mp3" or "mp4"
    quality: Optional[str] = None  # e.g., "320" for mp3, "720" for mp4

class BatchRequest(BaseModel):
    urls: List[str]
    format: str
    quality: Optional[str] = None

class PlaylistRequest(BaseModel):
    url: str
    format: str
    quality: Optional[str] = None

def download_and_convert(url, fmt, quality, filename):
    ydl_opts = {
        "outtmpl": get_media_path(filename),
        "format": "bestaudio/best" if fmt == "mp3" else "bestvideo+bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "ignoreerrors": False,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_path = ydl.prepare_filename(info)
            # Conversion if needed
            if fmt == "mp3":
                target_path = get_media_path(generate_uuid_filename("mp3"))
                (
                    ffmpeg
                    .input(downloaded_path)
                    .output(target_path, audio_bitrate=f"{quality}k" if quality else "320k", format="mp3", acodec="libmp3lame")
                    .run(overwrite_output=True, quiet=True)
                )
                cleanup_file(downloaded_path)
                return target_path
            elif fmt == "mp4":
                target_path = get_media_path(generate_uuid_filename("mp4"))
                (
                    ffmpeg
                    .input(downloaded_path)
                    .output(target_path, video_bitrate=f"{quality}k" if quality else None, format="mp4", vcodec="libx264", acodec="aac")
                    .run(overwrite_output=True, quiet=True)
                )
                cleanup_file(downloaded_path)
                return target_path
            else:
                raise ValueError("Invalid format")
    except Exception as e:
        logging.error(f"Download/convert error: {e}")
        raise

@app.post("/api/convert")
async def convert(request: ConvertRequest, background_tasks: BackgroundTasks):
    ensure_media_dir()
    ext = request.format
    filename = generate_uuid_filename(ext)
    try:
        file_path = download_and_convert(request.url, request.format, request.quality, filename)
        public_url = f"/media/{os.path.basename(file_path)}"
        logging.info(f"File ready: {public_url}")
        return {"status": "success", "download_url": public_url}
    except Exception as e:
        logging.error(f"Conversion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/convert/batch")
async def convert_batch(request: BatchRequest, background_tasks: BackgroundTasks):
    ensure_media_dir()
    results = []
    for url in request.urls:
        try:
            ext = request.format
            filename = generate_uuid_filename(ext)
            file_path = download_and_convert(url, request.format, request.quality, filename)
            public_url = f"/media/{os.path.basename(file_path)}"
            results.append({"url": url, "download_url": public_url, "status": "success"})
        except Exception as e:
            results.append({"url": url, "error": str(e), "status": "failed"})
    return {"results": results}

@app.post("/api/convert/playlist")
async def convert_playlist(request: PlaylistRequest, background_tasks: BackgroundTasks):
    # For demo: process synchronously, but you can use Celery for real background jobs
    ensure_media_dir()
    ydl_opts = {
        "extract_flat": True,
        "quiet": True,
        "ignoreerrors": True,
    }
    video_urls = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            if "entries" in info:
                for entry in info["entries"]:
                    if entry and "url" in entry:
                        video_urls.append(f"https://www.youtube.com/watch?v={entry['id']}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract playlist: {e}")

    results = []
    for url in video_urls:
        try:
            ext = request.format
            filename = generate_uuid_filename(ext)
            file_path = download_and_convert(url, request.format, request.quality, filename)
            public_url = f"/media/{os.path.basename(file_path)}"
            results.append({"url": url, "download_url": public_url, "status": "success"})
        except Exception as e:
            results.append({"url": url, "error": str(e), "status": "failed"})
    return {"results": results}

@app.get("/media/{filename}")
async def serve_media(filename: str):
    file_path = get_media_path(filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="application/octet-stream", filename=filename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)