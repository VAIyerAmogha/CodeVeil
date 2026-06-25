import os
import re
import uuid
from pathlib import Path
from git import Repo, GitCommandError  # type: ignore

CLONE_BASE_DIR = Path(os.getenv("CLONE_BASE_DIR", "/tmp/codeveil_clones")).resolve()

class CloneError(Exception):
    """Custom exception for all clone-related failures."""
    pass

def validate_github_url(url: str) -> tuple[str, str]:
    """Validate and extract owner and repo from a GitHub URL."""
    pattern = r"^https://github\.com/([\w.-]+)/([\w.-]+)$"
    match = re.match(pattern, url)
    if not match:
        raise CloneError(f"Invalid GitHub URL: {url}. Must match https://github.com/{{owner}}/{{repo}} exactly.")
    return match.group(1), match.group(2)

def clone_repository(github_url: str) -> str:
    """Clone a GitHub repository safely to a temporary directory."""
    owner, repo = validate_github_url(github_url)
    
    unique_id = str(uuid.uuid4())
    clone_path = CLONE_BASE_DIR / owner / f"{repo}_{unique_id}"
    resolved_path = clone_path.resolve()
    
    # Path traversal protection
    if not str(resolved_path).startswith(str(CLONE_BASE_DIR)):
        raise CloneError("Path traversal detected")
        
    try:
        resolved_path.mkdir(parents=True, exist_ok=True)
        Repo.clone_from(github_url, str(resolved_path))
        return str(resolved_path)
    except GitCommandError as e:
        raise CloneError(f"Git clone failed: {str(e)}")
    except Exception as e:
        raise CloneError(f"Unexpected error during clone: {str(e)}")
