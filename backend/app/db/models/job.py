from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JobProgress(BaseModel):
    files_processed: int = 0
    functions_extracted: int = 0
    chunks_generated: int = 0
    embeddings_created: int = 0
    total_files: int = 0

class Job(BaseModel):
    id: Optional[str] = None
    repo_id: str
    github_url: str
    status: str
    progress: JobProgress
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
