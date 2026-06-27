import os
from fastapi import HTTPException
from app.db.mongodb import get_database
from app.ingestion.cloner import get_repo_path
from app.ingestion.language_detector import detect_language

async def get_file_content(repo_id: str, file_path: str) -> dict:
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    repo_doc = await db["repositories"].find_one({"repo_id": repo_id})
    if not repo_doc:
        raise HTTPException(status_code=404, detail="Repository not found")
        
    github_url = repo_doc.get("github_url")
    if not github_url:
        raise HTTPException(status_code=404, detail="Repository URL not found")
        
    repo_path = get_repo_path(github_url)
    if not repo_path:
        raise HTTPException(status_code=404, detail="Cloned repository not found")
        
    full_path = os.path.join(repo_path, file_path)
    
    # Path traversal protection
    if not os.path.abspath(full_path).startswith(os.path.abspath(repo_path)):
        raise HTTPException(status_code=400, detail="Invalid file path")
        
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(full_path, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read file: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {e}")
        
    language = detect_language(full_path)
    
    return {
        "content": content,
        "language": language.lower() if language else "plaintext"
    }
