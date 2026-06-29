import re

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
