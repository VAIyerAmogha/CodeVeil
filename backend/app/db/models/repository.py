from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
from enum import Enum

class IndexedStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"

class Repository(BaseModel):
    id: Optional[str] = None
    user_id: str
    github_url: str
    owner: str
    repo_name: str
    stars: int
    forks: int
    primary_language: str
    languages: Dict[str, int]
    file_count: int
    indexed_status: IndexedStatus
    last_indexed_at: Optional[datetime] = None
    chroma_collection_id: Optional[str] = None
    ai_summary: Optional[str] = None
