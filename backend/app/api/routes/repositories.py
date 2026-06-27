import uuid
import asyncio
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic import BaseModel

from app.services.indexing_job import create_job
from app.ingestion.cloner import validate_github_url, clone_repository, CloneError
from app.services.github import fetch_repo_metadata
from app.db.mongodb import get_database
from app.ingestion.indexer import index_repo
from app.services.file_service import get_file_content
from app.services.query_service import get_queries_for_repo

router = APIRouter(prefix="/repositories", tags=["repositories"])

@router.get("/{repo_id}/queries")
async def get_repository_queries(repo_id: str) -> list[dict]:
    return await get_queries_for_repo(repo_id)

@router.get("/{repo_id}/file")
async def get_repository_file(repo_id: str, path: str) -> dict:
    return await get_file_content(repo_id, path)

class IndexRequest(BaseModel):
    github_url: str

@router.get("")
async def get_all_repositories() -> list[dict]:
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    cursor = db["repositories"].find()
    repos = await cursor.to_list(length=100)
    
    # Map _id and missing fields for frontend compatibility
    for repo in repos:
        repo["id"] = repo.get("repo_id") or str(repo["_id"])
        repo["_id"] = str(repo["_id"])
        
        # Normalize fields
        if "repo_name" not in repo and "name" in repo:
            repo["repo_name"] = repo["name"]
        
        # Provide defaults for fields expected by frontend
        repo.setdefault("owner", "Unknown")
        repo.setdefault("repo_name", "Unknown Repo")
        repo.setdefault("stars", 0)
        repo.setdefault("forks", 0)
        repo.setdefault("primary_language", "Unknown")
        repo.setdefault("languages", {})
        repo.setdefault("file_count", 0)
        repo.setdefault("indexed_status", "complete")
        repo.setdefault("last_indexed_at", None)
        repo.setdefault("chroma_collection_id", None)
        repo.setdefault("ai_summary", None)
        
    return repos

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
    
    # Generate summary synchronously using executor or directly since it's an async route but the groq client call is sync in responder right now
    from app.generation.responder import generate_repo_summary
    loop = asyncio.get_event_loop()
    ai_summary = await loop.run_in_executor(
        None, 
        generate_repo_summary, 
        metadata.get("repo_name"), 
        metadata.get("description", ""), 
        metadata.get("languages", {})
    )
    
    if existing_repo:
        repo_id = existing_repo["repo_id"]
        # Update existing repo with latest stats
        await db["repositories"].update_one(
            {"repo_id": repo_id},
            {"$set": {
                "stars": metadata.get("stars", 0),
                "forks": metadata.get("forks", 0),
                "ai_summary": ai_summary if ai_summary != "Summary not yet generated." else existing_repo.get("ai_summary")
            }}
        )
    else:
        repo_id = str(uuid.uuid4())
        repo_doc = {
            "repo_id": repo_id,
            "github_url": request.github_url,
            "name": metadata.get("repo_name"),
            "owner": metadata.get("owner"),
            "stars": metadata.get("stars", 0),
            "forks": metadata.get("forks", 0),
            "primary_language": metadata.get("primary_language"),
            "ai_summary": ai_summary
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
    job_doc["id"] = job_doc.get("job_id") or str(job_doc["_id"])
    
    if "progress" in job_doc:
        p = job_doc["progress"]
        p.setdefault("total_files", p.get("files_processed", 0))
        
        # If chunks_generated is 0 (due to SHA caching), fetch actual count from DB
        chunks_count = await db["chunks"].count_documents({"repo_id": repo_id})
        p["chunks_generated"] = p.get("chunks_generated", 0) or chunks_count
        p["embeddings_created"] = p.get("embeddings_created", 0) or chunks_count
        
        p.setdefault("functions_extracted", p.get("chunks_generated", 0))
        
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
    repo_doc["id"] = repo_doc.get("repo_id") or str(repo_doc["_id"])
    
    if "repo_name" not in repo_doc and "name" in repo_doc:
        repo_doc["repo_name"] = repo_doc["name"]
        
    repo_doc.setdefault("owner", "Unknown")
    repo_doc.setdefault("repo_name", "Unknown Repo")
    repo_doc.setdefault("stars", 0)
    repo_doc.setdefault("forks", 0)
    repo_doc.setdefault("primary_language", "Unknown")
    repo_doc.setdefault("languages", {})
    repo_doc.setdefault("file_count", 0)
    repo_doc.setdefault("indexed_status", "complete")
    repo_doc.setdefault("last_indexed_at", None)
    repo_doc.setdefault("chroma_collection_id", None)
    repo_doc.setdefault("ai_summary", None)
        
    chunks_count = await db["chunks"].count_documents({"repo_id": repo_id})
    
    return {
        "repository": repo_doc,
        "stats": {
            "total_chunks": chunks_count
        }
    }

@router.delete("/{repo_id}")
async def delete_repository(repo_id: str) -> dict:
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    repo_doc = await db["repositories"].find_one({"repo_id": repo_id})
    if not repo_doc:
        raise HTTPException(status_code=404, detail="Repository not found")
        
    # Delete from Mongo
    await db["repositories"].delete_one({"repo_id": repo_id})
    await db["jobs"].delete_many({"repo_id": repo_id})
    await db["chunks"].delete_many({"repo_id": repo_id})
    await db["queries"].delete_many({"repo_id": repo_id})
    
    # Delete from ChromaDB
    from app.db.chromadb import get_chroma_client
    client = get_chroma_client()
    try:
        client.delete_collection(name=repo_id)
    except Exception:
        pass
        
    return {"status": "success", "message": "Repository deleted"}
