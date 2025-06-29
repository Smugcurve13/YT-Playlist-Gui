import os
import json
import asyncio
from datetime import datetime, timedelta
from .file_utils import MEDIA_DIR

METADATA_EXT = ".metadata.json"

# Write metadata with timestamp
def write_metadata(file_id):
    metadata = {"timestamp": datetime.utcnow().isoformat()}
    meta_path = os.path.join(MEDIA_DIR, file_id + METADATA_EXT)
    with open(meta_path, "w") as f:
        json.dump(metadata, f)

# Read timestamp from metadata
def read_metadata_timestamp(file_id):
    meta_path = os.path.join(MEDIA_DIR, file_id + METADATA_EXT)
    if not os.path.exists(meta_path):
        return None
    with open(meta_path, "r") as f:
        metadata = json.load(f)
        return datetime.fromisoformat(metadata["timestamp"])

# Async cleanup function
def delete_file_and_metadata(file_path):
    try:
        os.remove(file_path)
    except Exception:
        pass
    meta_path = file_path + METADATA_EXT
    try:
        os.remove(meta_path)
    except Exception:
        pass

async def periodic_media_cleanup(interval_seconds=300, max_age_minutes=30):
    while True:
        now = datetime.utcnow()
        for fname in os.listdir(MEDIA_DIR):
            if fname.endswith(METADATA_EXT):
                continue
            file_path = os.path.join(MEDIA_DIR, fname)
            meta_path = file_path + METADATA_EXT
            if os.path.exists(meta_path):
                with open(meta_path, "r") as f:
                    metadata = json.load(f)
                    ts = datetime.fromisoformat(metadata["timestamp"])
                    if now - ts > timedelta(minutes=max_age_minutes):
                        delete_file_and_metadata(file_path)
        await asyncio.sleep(interval_seconds)
