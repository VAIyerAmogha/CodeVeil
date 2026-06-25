import uuid
import datetime
from typing import Dict, Any, Optional
from app.db.mongodb import get_database

async def create_job(repo_id: str, github_url: str) -> str:
    db = get_database()
    job_id = str(uuid.uuid4())
    doc = {
        "job_id": job_id,
        "repo_id": repo_id,
        "github_url": github_url,
        "status": "pending",
        "progress": {
            "files_processed": 0,
            "chunks_generated": 0,
            "embeddings_created": 0
        },
        "error": None,
        "created_at": datetime.datetime.now(datetime.timezone.utc),
        "updated_at": datetime.datetime.now(datetime.timezone.utc)
    }
    if db is not None:
        await db["jobs"].insert_one(doc)
    return job_id

async def update_progress(job_id: str, **fields: Any) -> None:
    db = get_database()
    if db is None:
        return
    update_doc = {f"progress.{k}": v for k, v in fields.items()}
    update_doc["updated_at"] = datetime.datetime.now(datetime.timezone.utc)
    await db["jobs"].update_one(
        {"job_id": job_id},
        {"$set": update_doc}
    )

async def set_status(job_id: str, status: str, error: Optional[str] = None) -> None:
    db = get_database()
    if db is None:
        return
    update_doc: Dict[str, Any] = {
        "status": status,
        "updated_at": datetime.datetime.now(datetime.timezone.utc)
    }
    if error is not None:
        update_doc["error"] = error
        
    await db["jobs"].update_one(
        {"job_id": job_id},
        {"$set": update_doc}
    )

async def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    db = get_database()
    if db is None:
        return None
    doc = await db["jobs"].find_one({"job_id": job_id})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc
