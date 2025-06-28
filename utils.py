import os
import uuid
import re
import shutil
from typing import Optional

MEDIA_DIR = "media"

def ensure_media_dir():
    if not os.path.exists(MEDIA_DIR):
        os.makedirs(MEDIA_DIR)

def sanitize_filename(filename: str) -> str:
    # Remove unsafe characters for filenames
    return re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)

def generate_uuid_filename(ext: str) -> str:
    return f"{uuid.uuid4()}.{ext}"

def cleanup_file(filepath: str):
    try:
        os.remove(filepath)
    except Exception:
        pass

def get_media_path(filename: str) -> str:
    return os.path.join(MEDIA_DIR, filename)

def clear_media_dir():
    shutil.rmtree(MEDIA_DIR, ignore_errors=True)
    os.makedirs(MEDIA_DIR)