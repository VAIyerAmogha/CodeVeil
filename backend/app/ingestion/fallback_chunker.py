import os
from typing import List, Dict, Any

AST_SUPPORTED = {"Python", "JavaScript", "TypeScript", "Java"}

def chunk_file_fallback(file_path: str, language: str, chunk_size: int = 100, overlap: int = 10) -> List[Dict[str, Any]]:
    """
    Fallback chunker for languages without AST support.
    Splits the file by lines with a fixed chunk size and overlap.
    """
    if language in AST_SUPPORTED:
        raise RuntimeError(f"fallback_chunker must NEVER be called for {language}. Use ast_chunker instead.")
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return []
    except UnicodeDecodeError:
        return []

    if not lines:
        return []

    chunks = []
    total_lines = len(lines)
    
    # Process chunks with overlap
    start_idx = 0
    while start_idx < total_lines:
        end_idx = min(start_idx + chunk_size, total_lines)
        
        chunk_lines = lines[start_idx:end_idx]
        source_code = "".join(chunk_lines)
        
        chunks.append({
            "file_path": file_path,
            "start_line": start_idx + 1,
            "end_line": end_idx,
            "language": language,
            "chunk_type": "fallback",
            "function_name": None,
            "parent_class": None,
            "source_code": source_code,
        })
        
        # Advance by chunk_size - overlap, but guarantee we move forward
        step = chunk_size - overlap
        if step <= 0:
            step = chunk_size
            
        start_idx += step
        
        # Prevent trailing overlapping chunks if we already reached the end
        if start_idx >= total_lines:
            break

    return chunks

def chunk_content_fallback(content: str, file_path: str, language: str, chunk_size: int = 100, overlap: int = 10) -> List[Dict[str, Any]]:
    """
    Fallback chunker for languages without AST support.
    Splits the content string by lines with a fixed chunk size and overlap.
    """
    if language in AST_SUPPORTED:
        raise RuntimeError(f"fallback_chunker must NEVER be called for {language}. Use ast_chunker instead.")
        
    lines = content.splitlines(keepends=True)
    if not lines:
        return []

    chunks = []
    total_lines = len(lines)
    
    start_idx = 0
    while start_idx < total_lines:
        end_idx = min(start_idx + chunk_size, total_lines)
        
        chunk_lines = lines[start_idx:end_idx]
        source_code = "".join(chunk_lines)
        
        chunks.append({
            "file_path": file_path,
            "start_line": start_idx + 1,
            "end_line": end_idx,
            "language": language,
            "chunk_type": "fallback",
            "function_name": None,
            "parent_class": None,
            "source_code": source_code,
        })
        
        step = chunk_size - overlap
        if step <= 0:
            step = chunk_size
            
        start_idx += step
        
        if start_idx >= total_lines:
            break

    return chunks
