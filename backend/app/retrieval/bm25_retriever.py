import logging
import re
from typing import List, Dict, Any, Tuple, Optional
from rank_bm25 import BM25Okapi
from app.db.mongodb import get_database
from app.ingestion.indexer import tokenize_code

logger = logging.getLogger(__name__)

# In-memory cache: repo_id -> (BM25Okapi, chunk_ids, updated_at_str)
_bm25_cache: Dict[str, Tuple[BM25Okapi, List[str], str]] = {}


async def load_bm25(repo_id: str) -> Optional[BM25Okapi]:
    """
    Load BM25 index from MongoDB, using an in-memory cache keyed on the
    index's `created_at` timestamp so re-indexing a repo always invalidates
    the stale in-memory copy.
    """
    db = get_database()
    if db is None:
        return None

    doc = await db["bm25_indexes"].find_one(
        {"repo_id": repo_id},
        {"corpus": 1, "chunk_ids": 1, "created_at": 1}
    )
    if not doc:
        logger.warning(f"No BM25 index in MongoDB for {repo_id}, skipping keyword search")
        return None

    # Use created_at as a cache-bust key so re-indexing invalidates stale cache
    db_timestamp = str(doc.get("created_at", ""))
    cached = _bm25_cache.get(repo_id)
    if cached and cached[2] == db_timestamp:
        return cached[0]

    # Rebuild from DB
    corpus = doc.get("corpus", [])
    chunk_ids = doc.get("chunk_ids", [])
    if not corpus:
        return None

    bm25 = BM25Okapi(corpus)
    _bm25_cache[repo_id] = (bm25, chunk_ids, db_timestamp)
    logger.info(f"Loaded BM25 index for {repo_id}: {len(corpus)} docs")
    return bm25


async def retrieve_bm25(repo_id: str, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
    bm25 = await load_bm25(repo_id)
    if bm25 is None:
        return []

    _, chunk_ids, _ = _bm25_cache[repo_id]
    tokenized = tokenize_code(query)
    scores = bm25.get_scores(tokenized)

    scored = [
        {"chunk_id": chunk_ids[i], "score": float(scores[i])}
        for i in range(min(len(scores), len(chunk_ids)))
        if float(scores[i]) > 0  # Skip zero-score chunks — they add noise
    ]
    scored.sort(key=lambda x: x["score"], reverse=True)
    return [
        {**r, "rank": idx + 1}
        for idx, r in enumerate(scored[:top_k])
    ]
