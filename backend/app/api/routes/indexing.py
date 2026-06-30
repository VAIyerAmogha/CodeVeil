from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.indexing_job import get_job
from app.ingestion.indexer import process_batch
from app.db.mongodb import get_database

router = APIRouter(prefix="/indexing", tags=["indexing"])

class BatchRequest(BaseModel):
    job_id: str

@router.post("/batch")
async def run_batch(request: BatchRequest) -> dict:
    job = await get_job(request.job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if job.get("status") == "complete":
        return {"done": True, "processed": 0}
    result = await process_batch(
        job["repo_id"], job["github_url"], request.job_id
    )
    return result


@router.get("/status/{job_id}")
async def get_batch_status(job_id: str) -> dict:
    job = await get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    pending_count = len(job.get("pending_files", []))
    processed_count = job.get("processed_file_count", 0)
    return {
        "job_id": job_id,
        "status": job.get("status"),
        "batch_status": job.get("batch_status"),
        "pending_files": pending_count,
        "processed_files": processed_count,
        "progress": job.get("progress", {})
    }
