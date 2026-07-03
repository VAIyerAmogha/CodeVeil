import tempfile
import hashlib
import re
import asyncio
import uuid
import os
from typing import List, Dict, Optional, Any
from pymongo import UpdateOne
from datetime import datetime
from pathlib import Path

from app.db.mongodb import get_database
from app.ingestion.language_detector import detect_language, is_ast_supported
from app.ingestion.ast_chunker import chunk_repo
from app.ingestion.fallback_chunker import chunk_file_fallback, chunk_content_fallback
from app.services.indexing_job import update_progress, set_status
from app.ingestion.embedder import embed_texts
from app.ingestion.github_fetcher import fetch_all_files
from app.ingestion.cloner import validate_github_url


def tokenize_code(text: str) -> list[str]:
    """
    Tokenize source code text for BM25 indexing.
    Splits on whitespace, camelCase, and snake_case boundaries so that
    identifiers like 'getUserById' or 'fetch_all_files' produce meaningful tokens.
    """
    tokens = []
    for word in re.split(r'\s+', text):
        # Split camelCase: getUserById → get User By Id
        word = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', word)
        # Normalize non-alphanumeric characters (underscores, dots, parens, etc.) to spaces
        word = re.sub(r'[^a-zA-Z0-9]+', ' ', word)
        tokens.extend(word.lower().split())
    # Drop single-character tokens (noise)
    return [t for t in tokens if len(t) > 1]


async def store_chunks_with_embeddings(repo_id: str, chunks: List[Dict[str, Any]]) -> None:
    if not chunks:
        return

    # Call embedder to get embeddings for all source codes
    embeddings = await embed_texts([chunk.get("source_code", "") for chunk in chunks])

    db = get_database()
    if db is None:
        return
    chunks_collection = db["chunks"]
    
    operations = []
    for i, chunk in enumerate(chunks):
        chunk["embedding"] = embeddings[i]
        chunk["repo_id"] = repo_id
        if "chroma_id" not in chunk:
            chunk["chroma_id"] = str(uuid.uuid4())
            
        # Upsert into MongoDB chunks collection
        filter_query = {
            "repo_id": repo_id,
            "file_path": chunk["file_path"],
            "function_name": chunk.get("function_name")
        }
        update_query = {"$set": chunk}
        
        operations.append(UpdateOne(filter_query, update_query, upsert=True))
        
    if operations:
        await chunks_collection.bulk_write(operations)


async def build_and_save_bm25_mongo(repo_id: str, chunks: List[Dict]) -> None:
    corpus = [tokenize_code(c.get("source_code", "")) for c in chunks]
    chunk_ids = [c.get("chroma_id", "") for c in chunks]
    db = get_database()
    await db["bm25_indexes"].update_one(
        {"repo_id": repo_id},
        {"$set": {
            "repo_id": repo_id,
            "corpus": corpus,
            "chunk_ids": chunk_ids,
            "created_at": datetime.utcnow()
        }},
        upsert=True
    )


def compute_sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


async def get_cached_sha(repo_id: str, file_path: str) -> Optional[str]:
    """Look up existing sha from MongoDB chunks collection."""
    db = get_database()
    if db is None:
        return None

    chunks_collection = db["chunks"]
    doc = await chunks_collection.find_one(
        {"repo_id": repo_id, "file_path": file_path},
        projection={"sha256": 1}
    )
    if doc:
        return doc.get("sha256")
    return None


async def get_all_cached_shas(repo_id: str) -> Dict[str, str]:
    """Look up all existing shas from MongoDB chunks collection for a given repo."""
    db = get_database()
    if db is None:
        return {}

    chunks_collection = db["chunks"]
    cursor = chunks_collection.find(
        {"repo_id": repo_id},
        projection={"file_path": 1, "sha256": 1}
    )
    cached_shas = {}
    async for doc in cursor:
        file_path = doc.get("file_path")
        sha = doc.get("sha256")
        if file_path and sha:
            cached_shas[file_path] = sha
    return cached_shas


async def is_file_changed(repo_id: str, file_path: str, current_sha: str) -> bool:
    """Compare current SHA to cached — True if changed or new."""
    cached_sha = await get_cached_sha(repo_id, file_path)
    return current_sha != cached_sha


async def index_repo(repo_id: str, github_url: str, job_id: str) -> Dict[str, int]:
    owner, repo = validate_github_url(github_url)
    cached_shas = await get_all_cached_shas(repo_id)
    files = await fetch_all_files(owner, repo)
    files_processed = 0
    all_repo_chunks = []
    
    await set_status(job_id, "running")

    for file_dict in files:
        path = file_dict["path"]
        content_bytes = file_dict["content"]
        sha = file_dict["sha"]

        language = detect_language(path)
        if not language:
            continue

        files_processed += 1
        if files_processed % 100 == 0 or files_processed == 1:
            await update_progress(job_id, files_processed=files_processed)

        # SHA cache check (use github tree sha as cache key)
        if cached_shas.get(path) == sha:
            continue

        if is_ast_supported(language):
            # Bridge: write to tempfile for ast_chunker
            suffix = Path(path).suffix
            try:
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                    tmp.write(content_bytes)
                    tmp_path = tmp.name
                try:
                    file_chunks = chunk_repo(tmp_path, language)
                except Exception:
                    content_str = content_bytes.decode("utf-8", errors="replace")
                    file_chunks = chunk_content_fallback(content_str, path, language)
                finally:
                    os.unlink(tmp_path)
            except Exception:
                continue
        else:
            content_str = content_bytes.decode("utf-8", errors="replace")
            file_chunks = chunk_content_fallback(content_str, path, language)

        for chunk in file_chunks:
            chunk["file_path"] = path   # use GitHub path not tmp path
            chunk["sha256"] = sha

        all_repo_chunks.extend(file_chunks)

    await update_progress(job_id, files_processed=files_processed)

    if all_repo_chunks:
        chunks_generated = len(all_repo_chunks)
        await update_progress(job_id, chunks_generated=chunks_generated)

        await store_chunks_with_embeddings(repo_id, all_repo_chunks)
        await update_progress(job_id, embeddings_created=chunks_generated)
        await build_and_save_bm25_mongo(repo_id, all_repo_chunks)

    await set_status(job_id, "complete")
    return {
        "files_processed": files_processed,
        "chunks_generated": len(all_repo_chunks),
        "embeddings_created": len(all_repo_chunks)
    }

async def _append_bm25_mongo(repo_id: str, chunks: List[Dict]) -> None:
    """Append new chunks to existing BM25 corpus in MongoDB."""
    db = get_database()
    new_corpus = [tokenize_code(c.get("source_code", "")) for c in chunks]
    new_ids = [c.get("chroma_id", "") for c in chunks]
    existing = await db["bm25_indexes"].find_one({"repo_id": repo_id})
    if existing:
        corpus = existing.get("corpus", []) + new_corpus
        chunk_ids = existing.get("chunk_ids", []) + new_ids
    else:
        corpus = new_corpus
        chunk_ids = new_ids
    await db["bm25_indexes"].update_one(
        {"repo_id": repo_id},
        {"$set": {
            "corpus": corpus,
            "chunk_ids": chunk_ids,
            "created_at": datetime.utcnow()
        }},
        upsert=True
    )

async def prepare_index(repo_id: str, github_url: str, job_id: str) -> int:
    """Fetch file tree from GitHub, filter by language + SHA cache, save to job's pending_files. Returns total file count."""
    from app.ingestion.github_fetcher import fetch_repo_tree
    from app.services.indexing_job import set_pending_files
    owner, repo_name = validate_github_url(github_url)
    tree = await fetch_repo_tree(owner, repo_name)
    # Filter to only files with a detectable language
    filtered = [f for f in tree if detect_language(f["path"]) is not None]
    # SHA cache check — skip already indexed unchanged files
    cached_shas = await get_all_cached_shas(repo_id)
    pending = [f for f in filtered if cached_shas.get(f["path"]) != f.get("sha")]
    await set_pending_files(job_id, pending)
    return len(pending)

async def _fetch_and_chunk_file(
    client: Any,
    sem: asyncio.Semaphore,
    owner: str,
    repo_name: str,
    file_info: dict,
) -> List[Dict]:
    """
    Fetch one file from GitHub and chunk it, inside a semaphore.
    Returns list of chunks (empty on any error).
    """
    from app.ingestion.github_fetcher import fetch_file_content

    async with sem:
        path = file_info["path"]
        sha = file_info.get("sha", "")
        language = detect_language(path)
        if not language:
            return []

        content_bytes = await fetch_file_content(client, owner, repo_name, path)
        if not content_bytes:
            return []

        if is_ast_supported(language):
            suffix = Path(path).suffix
            try:
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                    tmp.write(content_bytes)
                    tmp_path = tmp.name
                try:
                    file_chunks = chunk_repo(tmp_path, language)
                except Exception:
                    content_str = content_bytes.decode("utf-8", errors="replace")
                    file_chunks = chunk_content_fallback(content_str, path, language)
                finally:
                    os.unlink(tmp_path)
            except Exception:
                return []
        else:
            content_str = content_bytes.decode("utf-8", errors="replace")
            file_chunks = chunk_content_fallback(content_str, path, language)

        for chunk in file_chunks:
            chunk["file_path"] = path
            chunk["sha256"] = sha

        return file_chunks


async def process_batch(repo_id: str, github_url: str, job_id: str) -> Dict:
    """
    Fetch content for one batch concurrently, chunk, embed, store.
    Returns {"done": bool, "processed": int}

    All files in the batch are fetched in parallel (Semaphore cap=10),
    replacing the previous sequential for-loop.
    """
    from app.services.indexing_job import pop_batch, set_status, get_job, update_progress
    from app.config import settings
    import httpx

    batch = await pop_batch(job_id, batch_size=20)
    if not batch:
        await set_status(job_id, "complete")
        return {"done": True, "processed": 0}

    owner, repo_name = validate_github_url(github_url)
    sem = asyncio.Semaphore(10)

    async with httpx.AsyncClient(
        headers={
            "Accept": "application/vnd.github+json",
            **({} if not settings.github_token else {"Authorization": f"Bearer {settings.github_token}"})
        },
        timeout=30.0
    ) as client:
        tasks = [
            _fetch_and_chunk_file(client, sem, owner, repo_name, f)
            for f in batch
        ]
        results = await asyncio.gather(*tasks)

    # Flatten list-of-lists
    all_chunks = [chunk for file_chunks in results for chunk in file_chunks]

    if all_chunks:
        await store_chunks_with_embeddings(repo_id, all_chunks)
        await _append_bm25_mongo(repo_id, all_chunks)

    job_doc = await get_job(job_id)
    if job_doc:
        await update_progress(job_id, files_processed=job_doc.get("processed_file_count", 0))
    return {"done": False, "processed": len(batch)}

