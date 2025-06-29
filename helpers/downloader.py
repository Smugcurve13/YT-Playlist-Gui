import yt_dlp
import ffmpeg
from .file_utils import generate_uuid_filename, get_media_path, cleanup_file
from .job_manager import update_job_progress
from .media_cleanup import write_metadata
import os
import json
from datetime import datetime


def download_and_convert(url, fmt, quality):
    ext = fmt
    filename = generate_uuid_filename(ext)
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
                target_file_id = generate_uuid_filename("mp3")
                target_path = get_media_path(target_file_id)
                (
                    ffmpeg
                    .input(downloaded_path)
                    .output(target_path, audio_bitrate=f"{quality}k" if quality else "320k", format="mp3", acodec="libmp3lame")
                    .run(overwrite_output=True, quiet=True)
                )
                cleanup_file(downloaded_path)
                write_metadata(target_file_id)
                return target_file_id
            elif fmt == "mp4":
                target_file_id = generate_uuid_filename("mp4")
                target_path = get_media_path(target_file_id)
                (
                    ffmpeg
                    .input(downloaded_path)
                    .output(target_path, video_bitrate=f"{quality}k" if quality else None, format="mp4", vcodec="libx264", acodec="aac")
                    .run(overwrite_output=True, quiet=True)
                )
                cleanup_file(downloaded_path)
                write_metadata(target_file_id)
                return target_file_id
            else:
                raise ValueError("Invalid format")
    except Exception as e:
        raise Exception(f"Download/convert error: {e}")


def download_playlist(url, fmt, quality, job_id):
    ydl_opts = {
        "extract_flat": True,
        "quiet": True,
        "ignoreerrors": True,
    }
    video_urls = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if "entries" in info:
                for entry in info["entries"]:
                    if entry and "id" in entry:
                        video_urls.append(f"https://www.youtube.com/watch?v={entry['id']}")
    except Exception as e:
        update_job_progress(job_id, 100, results=[{"error": f"Failed to extract playlist: {e}"}])
        return

    results = []
    total = len(video_urls)
    for idx, vurl in enumerate(video_urls):
        try:
            file_id = download_and_convert(vurl, fmt, quality)
            results.append({"url": vurl, "file_id": file_id, "status": "success"})
        except Exception as e:
            results.append({"url": vurl, "error": str(e), "status": "failed"})
        progress = int(((idx + 1) / total) * 100) if total else 100
        update_job_progress(job_id, progress, results=results)
    update_job_progress(job_id, 100, results=results)


def download_batch(urls, fmt, quality, job_id):
    results = []
    total = len(urls)
    for idx, url in enumerate(urls):
        try:
            file_id = download_and_convert(url, fmt, quality)
            results.append({"url": url, "file_id": file_id, "status": "success"})
        except Exception as e:
            results.append({"url": url, "error": str(e), "status": "failed"})
        progress = int(((idx + 1) / total) * 100) if total else 100
        update_job_progress(job_id, progress, results=results)
    update_job_progress(job_id, 100, results=results)