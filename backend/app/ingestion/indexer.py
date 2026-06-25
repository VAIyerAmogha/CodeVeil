import os
import hashlib
import pickle
import uuid
from typing import List, Dict, Optional, Any
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

from app.db.chromadb import get_chroma_client
from app.db.mongodb import get_database
from app.ingestion.language_detector import detect_language, is_ast_supported
from app.ingestion.ast_chunker import chunk_repo
from app.ingestion.fallback_chunker import chunk_file_fallback
from app.ingestion.enricher import enrich_chunks
from app.services.indexing_job import update_progress, set_status

# 1. Embedding model singleton
# BAAI/bge-small-en-v1.5 via SentenceTransformer at module level
# NEVER instantiated inside a function or per request
embedding_model = SentenceTransformer("BAAI/bge-small-en-v1.5")


def _embed(texts: List[str]) -> List[List[float]]:
    """Embed a list of texts using the singleton embedding model."""
    if not texts:
        return []
    embeddings = embedding_model.encode(texts)
    return embeddings.tolist()


# 2. ChromaDB writes
def get_or_create_collection(repo_id: str):
    """Get or create a ChromaDB collection for a given repo."""
    client = get_chroma_client()
    return client.get_or_create_collection(name=repo_id)


def store_chunks_in_chroma(repo_id: str, chunks: List[Dict[str, Any]]) -> None:
    """
    Embed chunk source_code, upsert into ChromaDB with chunk metadata.
    Note: As per rules, chunk metadata is kept in MongoDB, so we only
    upsert ID and embeddings (and documents) to Chroma.
    """
    if not chunks:
        return

    collection = get_or_create_collection(repo_id)

    ids = []
    documents = []
    
    texts_to_embed = []
    for chunk in chunks:
        if "chroma_id" not in chunk:
            chunk["chroma_id"] = str(uuid.uuid4())
            
        texts_to_embed.append(chunk.get("source_code", ""))

    embeddings = _embed(texts_to_embed)

    for chunk in chunks:
        ids.append(chunk["chroma_id"])
        documents.append(chunk.get("source_code", ""))

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
    )


# 3. BM25 index
def build_and_save_bm25(repo_id: str, chunks: List[Dict[str, Any]]) -> None:
    """Build a BM25 index from chunk source_code texts and save to disk."""
    if not chunks:
        return

    texts = [chunk.get("source_code", "") for chunk in chunks]
    # Basic tokenization by splitting on whitespace
    tokenized_corpus = [doc.split() for doc in texts]
    bm25 = BM25Okapi(tokenized_corpus)

    save_dir = "/tmp/codeveil_bm25"
    os.makedirs(save_dir, exist_ok=True)

    file_path = os.path.join(save_dir, f"{repo_id}.pkl")
    with open(file_path, "wb") as f:
        pickle.dump(bm25, f)


# 4. MongoDB writes
async def store_chunks_in_mongo(repo_id: str, chunks: List[Dict[str, Any]]) -> None:
    """
    Insert chunk documents into MongoDB.
    Expects chroma_id to be set by store_chunks_in_chroma.
    """
    if not chunks:
        return

    db = get_database()
    if db is None:
        return

    chunks_collection = db["chunks"]

    documents_to_insert = []
    for chunk in chunks:
        doc = chunk.copy()
        doc["repo_id"] = repo_id
        documents_to_insert.append(doc)

    if documents_to_insert:
        await chunks_collection.insert_many(documents_to_insert)


# 5. SHA256 cache
def compute_sha256(file_path: str) -> str:
    """Compute the SHA256 hash of a file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


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


# 6. Main entry point
async def index_repo(repo_id: str, clone_path: str, job_id: str) -> Dict[str, int]:
    """
    Walk all files in clone_path.
    Detect language, check SHA cache, chunk, enrich, embed, store.
    """
    files_processed = 0
    chunks_generated = 0
    embeddings_created = 0

    all_repo_chunks = []

    try:
        await set_status(job_id, "running")

        # Load all cached SHAs in a single query to prevent N round-trips over the network
        cached_shas = await get_all_cached_shas(repo_id)

        for root, dirs, files in os.walk(clone_path):
            # Skip common build/dependency directories
            dirs[:] = [d for d in dirs if d not in {".git", "node_modules", ".venv", "venv", "__pycache__", ".next", ".pytest_cache", ".codex", ".agents", "dist", "build"}]
                
            for file in files:
                file_path = os.path.join(root, file)
                # Use relative path for storage
                rel_file_path = os.path.relpath(file_path, clone_path)

                language = detect_language(file_path)
                if not language:
                    continue

                files_processed += 1
                # Batch progress updates to avoid hitting DB rate limits/latency on every single file
                if files_processed % 100 == 0 or files_processed == 1:
                    await update_progress(job_id, files_processed=files_processed)
                
                try:
                    current_sha = compute_sha256(file_path)
                except OSError:
                    continue

                cached_sha = cached_shas.get(rel_file_path)
                if current_sha == cached_sha:
                    continue

                if is_ast_supported(language):
                    try:
                        file_chunks = chunk_repo(file_path, language)
                    except Exception:
                        file_chunks = chunk_file_fallback(file_path, language)
                else:
                    file_chunks = chunk_file_fallback(file_path, language)

                if not file_chunks:
                    continue

                for chunk in file_chunks:
                    chunk["file_path"] = rel_file_path
                    chunk["sha256"] = current_sha

                all_repo_chunks.extend(file_chunks)

        # Update final processed count
        await update_progress(job_id, files_processed=files_processed)

        if all_repo_chunks:
            # Batch enrich all missing summaries concurrently
            all_repo_chunks = await enrich_chunks(all_repo_chunks)
            
            chunks_generated = len(all_repo_chunks)
            await update_progress(job_id, chunks_generated=chunks_generated)

            # 1. Store in Chroma (also sets chroma_id on chunks)
            store_chunks_in_chroma(repo_id, all_repo_chunks)
            embeddings_created = chunks_generated
            await update_progress(job_id, embeddings_created=embeddings_created)

            # 2. Build BM25
            build_and_save_bm25(repo_id, all_repo_chunks)

            # 3. Store in Mongo
            await store_chunks_in_mongo(repo_id, all_repo_chunks)

        await set_status(job_id, "complete")
        return {
            "files_processed": files_processed,
            "chunks_generated": chunks_generated,
            "embeddings_created": embeddings_created
        }
        
    except Exception as e:
        await set_status(job_id, "failed", str(e))
        raise
