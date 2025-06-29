import uuid

_jobs = {}

def create_job():
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "pending", "progress": 0, "results": []}
    return job_id

def update_job_progress(job_id, progress, results=None):
    if job_id in _jobs:
        _jobs[job_id]["progress"] = progress
        if results is not None:
            _jobs[job_id]["results"] = results
        if progress == 100:
            _jobs[job_id]["status"] = "completed"

def get_job_status(job_id):
    return _jobs.get(job_id)