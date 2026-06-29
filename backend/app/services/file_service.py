import os
from fastapi import HTTPException
from app.db.mongodb import get_database
from app.ingestion.cloner import validate_github_url
from app.ingestion.language_detector import detect_language
from app.ingestion.github_fetcher import fetch_file_content
from app.config import settings
import httpx

async def get_file_content(repo_id: str, file_path: str) -> dict:
    if ":" in file_path:
        file_path = file_path.split(":")[0]

    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    repo_doc = await db["repositories"].find_one({"repo_id": repo_id})
    if not repo_doc:
        raise HTTPException(status_code=404, detail="Repository not found")
        
    github_url = repo_doc.get("github_url")
    if not github_url:
        raise HTTPException(status_code=404, detail="Repository URL not found")
        
    try:
        owner, repo_name = validate_github_url(github_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    async with httpx.AsyncClient(
        headers={"Accept": "application/vnd.github+json",
                 **({} if not settings.github_token else {"Authorization": f"Bearer {settings.github_token}"})}
    ) as client:
        content_bytes = await fetch_file_content(client, owner, repo_name, file_path)
        
    if not content_bytes:
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        content = content_bytes.decode('utf-8')
    except UnicodeDecodeError:
        try:
            content = content_bytes.decode('latin-1')
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read file: {e}")
            
    language = detect_language(file_path)
    
    return {
        "content": content,
        "language": language.lower() if language else "plaintext"
    }
