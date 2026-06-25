import uuid
import asyncio
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic import BaseModel

from app.services.indexing_job import create_job
from app.ingestion.cloner import validate_github_url, clone_repository, CloneError
from app.services.github import fetch_repo_metadata
from app.db.mongodb import get_database
from app.ingestion.indexer import index_repo

router = APIRouter(prefix="/repositories", tags=["repositories"])

class IndexRequest(BaseModel):
    github_url: str

async def _run_pipeline(job_id: str, repo_id: str, github_url: str) -> None:
    from app.services.indexing_job import set_status
    try:
        # Run clone in executor since it's synchronous
        loop = asyncio.get_event_loop()
        clone_path = await loop.run_in_executor(None, clone_repository, github_url)
        # Index
        await index_repo(repo_id, clone_path, job_id)
    except Exception as e:
        await set_status(job_id, "failed", str(e))

@router.post("/index", status_code=status.HTTP_202_ACCEPTED)
async def index_repository(request: IndexRequest, background_tasks: BackgroundTasks) -> dict:
    # Validate URL
    try:
        validate_github_url(request.github_url)
    except CloneError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Fetch metadata (running sync function in executor)
    loop = asyncio.get_event_loop()
    try:
        metadata = await loop.run_in_executor(None, fetch_repo_metadata, request.github_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    existing_repo = await db["repositories"].find_one({"github_url": request.github_url})
    if existing_repo:
        repo_id = existing_repo["repo_id"]
    else:
        repo_id = str(uuid.uuid4())
        repo_doc = {
            "repo_id": repo_id,
            "github_url": request.github_url,
            "name": metadata.get("repo_name"),
            "owner": metadata.get("owner"),
            "stars": metadata.get("stars", 0),
            "primary_language": metadata.get("primary_language")
        }
        await db["repositories"].insert_one(repo_doc)

    job_id = await create_job(repo_id, request.github_url)
    background_tasks.add_task(_run_pipeline, job_id, repo_id, request.github_url)

    return {"job_id": job_id, "repo_id": repo_id}


@router.get("/{repo_id}/status")
async def get_repository_status(repo_id: str) -> dict:
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    job_doc = await db["jobs"].find_one({"repo_id": repo_id}, sort=[("created_at", -1)])
    if not job_doc:
        raise HTTPException(status_code=404, detail="No job found for this repository")
    
    job_doc["_id"] = str(job_doc["_id"])
    return job_doc

@router.get("/{repo_id}")
async def get_repository(repo_id: str) -> dict:
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    repo_doc = await db["repositories"].find_one({"repo_id": repo_id})
    if not repo_doc:
        raise HTTPException(status_code=404, detail="Repository not found")
        
    repo_doc["_id"] = str(repo_doc["_id"])
    chunks_count = await db["chunks"].count_documents({"repo_id": repo_id})
    
    return {
        "repository": repo_doc,
        "stats": {
            "total_chunks": chunks_count
        }
    }
