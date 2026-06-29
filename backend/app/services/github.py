import httpx
from typing import Dict, Any
from app.config import settings
from app.ingestion.cloner import validate_github_url, CloneError

def fetch_repo_metadata(github_url: str) -> Dict[str, Any]:
    """Fetch repository metadata using the GitHub API."""
    try:
        owner, repo = validate_github_url(github_url)
    except CloneError as e:
        raise ValueError(str(e))
        
    auth = None
    if settings.github_client_id and settings.github_client_secret:
        auth = (settings.github_client_id, settings.github_client_secret)
        
    headers = {"Accept": "application/vnd.github.v3+json"}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"
    
    with httpx.Client(auth=auth, headers=headers) as client:
        # Fetch basic metadata
        repo_response = client.get(f"https://api.github.com/repos/{owner}/{repo}",follow_redirects=True)
        if repo_response.status_code != 200:
            raise RuntimeError(f"GitHub API error fetching repo: {repo_response.text}",)
        repo_data = repo_response.json()
        
        # Fetch languages
        lang_response = client.get(f"https://api.github.com/repos/{owner}/{repo}/languages",follow_redirects=True)
        if lang_response.status_code != 200:
            raise RuntimeError(f"GitHub API error fetching languages: {lang_response.text}")
        languages = lang_response.json()
        
        # Fetch file count via git tree
        default_branch = repo_data.get("default_branch", "main")
        tree_response = client.get(f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1",follow_redirects=True)
        file_count = 0
        if tree_response.status_code == 200:
            tree_data = tree_response.json()
            file_count = sum(1 for item in tree_data.get("tree", []) if item.get("type") == "blob")
            
    return {
        "owner": repo_data.get("owner", {}).get("login"),
        "repo_name": repo_data.get("name"),
        "description": repo_data.get("description"),
        "stars": repo_data.get("stargazers_count", 0),
        "forks": repo_data.get("forks_count", 0),
        "primary_language": repo_data.get("language"),
        "languages": languages,
        "file_count": file_count
    }
