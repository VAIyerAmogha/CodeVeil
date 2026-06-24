from pydantic import BaseModel
from typing import Optional
from enum import Enum

class ChunkType(str, Enum):
    FUNCTION = "function"
    CLASS = "class"
    DOCSTRING = "docstring"
    FALLBACK = "fallback"

class Chunk(BaseModel):
    id: Optional[str] = None
    repo_id: str
    file_path: str
    function_name: Optional[str] = None
    parent_class: Optional[str] = None
    start_line: int
    end_line: int
    language: str
    chunk_type: ChunkType
    sha256: str
    summary: Optional[str] = None
    chroma_id: Optional[str] = None
