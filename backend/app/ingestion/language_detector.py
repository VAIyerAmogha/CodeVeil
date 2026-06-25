import os
from typing import Optional

EXTENSION_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".cpp": "C++",
    ".c": "C",
    ".cs": "C#",
    ".php": "PHP"
}

AST_SUPPORTED_LANGUAGES = {"Python", "JavaScript", "TypeScript", "Java"}

def is_ast_supported(language: str) -> bool:
    """Check if the given language is supported by our AST chunker."""
    return language in AST_SUPPORTED_LANGUAGES

def detect_language(file_path: str) -> Optional[str]:
    """Detect language based on the file extension."""
    _, ext = os.path.splitext(file_path)
    return EXTENSION_MAP.get(ext.lower())
