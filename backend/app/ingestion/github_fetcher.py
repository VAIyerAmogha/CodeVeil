import base64
import asyncio
import logging
from typing import List, Dict, Any
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__",
    ".next", ".pytest_cache", "dist", "build", ".agents", ".codex"
}
MAX_FILE_BYTES = 500_000
CONCURRENT_LIMIT = 10

def _get_headers() -> dict:
    headers = {"Accept": "application/vnd.github+json"}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"
    return headers

async def fetch_repo_tree(owner: str, repo: str) -> List[Dict]:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=_get_headers())
        if response.status_code != 200:
            raise RuntimeError(f"GitHub tree API error: {response.status_code}")
        
        data = response.json()
        tree = data.get("tree", [])
        
        filtered = []
        for item in tree:
            if item.get("type") != "blob":
                continue
            path = item.get("path", "")
            if any(seg in SKIP_DIRS for seg in path.split("/")):
                continue
            if item.get("size", 0) > MAX_FILE_BYTES:
                continue
            filtered.append(item)
            
        return filtered

async def fetch_file_content(client: httpx.AsyncClient, owner: str, repo: str, path: str) -> bytes:
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{path}"
    try:
        response = await client.get(url)
        if response.status_code == 404:
            # Fallback to API
            api_url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}"
            api_response = await client.get(api_url)
            if api_response.status_code == 404:
                return b""
            api_response.raise_for_status()
            data = api_response.json()
            if "content" in data:
                return base64.b64decode(data["content"])
            return b""
            
        response.raise_for_status()
        return response.content
    except Exception as e:
        logger.warning(f"Error fetching {path}: {e}")
        return b""

async def fetch_with_sem(sem: asyncio.Semaphore, client: httpx.AsyncClient, owner: str, repo: str, file_item: dict) -> Dict[str, Any]:
    async with sem:
        path = file_item["path"]
        content = await fetch_file_content(client, owner, repo, path)
        return {
            "path": path,
            "content": content,
            "sha": file_item.get("sha")
        }

async def fetch_all_files(owner: str, repo: str) -> List[Dict[str, Any]]:
    tree = await fetch_repo_tree(owner, repo)
    sem = asyncio.Semaphore(CONCURRENT_LIMIT)
    fetched_count = 0
    
    async def fetch_and_count(client, item):
        nonlocal fetched_count
        res = await fetch_with_sem(sem, client, owner, repo, item)
        fetched_count += 1
        if fetched_count % 50 == 0:
            logger.info(f"Fetched {fetched_count}/{len(tree)} files")
        return res

    async with httpx.AsyncClient(headers=_get_headers(), timeout=30.0) as client:
        tasks = [fetch_and_count(client, f) for f in tree]
        results = await asyncio.gather(*tasks)
        
    return [r for r in results if r["content"] != b""]
