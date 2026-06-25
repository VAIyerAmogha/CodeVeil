import os
import pickle
import logging
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
from app.db.mongodb import get_database

logger = logging.getLogger(__name__)

BM25_INDEX_DIR = "/tmp/codeveil_bm25"

# Module-level cache: {repo_id: (bm25_instance, list_of_chroma_ids)}
_bm25_cache: Dict[str, tuple[BM25Okapi, List[str]]] = {}


async def load_bm25(repo_id: str) -> BM25Okapi:
    """
    Load pickled BM25 index from disk for this repo.
    Also fetches and caches the ordered chroma_ids from MongoDB.
    Raises FileNotFoundError with clear message if index is missing.
    """
    global _bm25_cache
    if repo_id in _bm25_cache:
        return _bm25_cache[repo_id][0]

    file_path = os.path.join(BM25_INDEX_DIR, f"{repo_id}.pkl")
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"BM25 index not found for repository '{repo_id}' at path '{file_path}'"
        )

    try:
        with open(file_path, "rb") as f:
            bm25 = pickle.load(f)
    except Exception as e:
        logger.error(f"Failed to unpickle BM25 index for repo {repo_id}: {e}")
        raise

    # Fetch the chunk chroma_ids from MongoDB in insertion order (by _id)
    db = get_database()
    if db is None:
        raise RuntimeError("Database connection not available to load chunk IDs")

    chunks_cursor = db["chunks"].find(
        {"repo_id": repo_id}, 
        projection={"chroma_id": 1}
    ).sort("_id", 1)
    
    chroma_ids = [doc["chroma_id"] async for doc in chunks_cursor]

    if not chroma_ids:
        raise ValueError(f"No chunks found in database for repository '{repo_id}'")

    if len(chroma_ids) != bm25.corpus_size:
        logger.warning(
            f"Chroma IDs count ({len(chroma_ids)}) does not match BM25 corpus size ({bm25.corpus_size}) "
            f"for repository {repo_id}"
        )

    _bm25_cache[repo_id] = (bm25, chroma_ids)
    return bm25


async def retrieve_bm25(repo_id: str, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
    """
    Tokenize query (split on whitespace).
    Score all chunks, return top_k.
    Each result: {chunk_id, score, rank} where score is raw BM25 score.
    """
    # Ensure BM25 index and chroma_ids are loaded and cached
    bm25 = await load_bm25(repo_id)
    _, chroma_ids = _bm25_cache[repo_id]

    # Tokenize query by splitting on whitespace
    tokenized_query = query.split()
    scores = bm25.get_scores(tokenized_query)

    # Pair each chroma_id with its score
    scored_results = []
    for idx, score in enumerate(scores):
        if idx < len(chroma_ids):
            scored_results.append({
                "chunk_id": chroma_ids[idx],
                "score": float(score)
            })

    # Sort descending by score
    scored_results.sort(key=lambda x: x["score"], reverse=True)

    # Select top_k and assign 1-based ranks
    top_results = []
    for rank, res in enumerate(scored_results[:top_k], start=1):
        top_results.append({
            "chunk_id": res["chunk_id"],
            "score": res["score"],
            "rank": rank
        })

    return top_results
