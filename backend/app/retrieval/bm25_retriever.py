import logging
from typing import List, Dict, Any, Tuple
from rank_bm25 import BM25Okapi
from app.db.mongodb import get_database

logger = logging.getLogger(__name__)

_bm25_cache: Dict[str, Tuple[BM25Okapi, List[str]]] = {}

async def load_bm25(repo_id: str):
    if repo_id in _bm25_cache:
        return _bm25_cache[repo_id][0]
    db = get_database()
    doc = await db["bm25_indexes"].find_one({"repo_id": repo_id})
    if not doc:
        logger.warning(f"No BM25 index in MongoDB for {repo_id}, skipping keyword search")
        return None
    bm25 = BM25Okapi(doc["corpus"])
    _bm25_cache[repo_id] = (bm25, doc["chunk_ids"])
    return bm25

async def retrieve_bm25(repo_id: str, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
    bm25 = await load_bm25(repo_id)
    if bm25 is None:
        return []
    _, chunk_ids = _bm25_cache[repo_id]
    tokenized = query.split()
    scores = bm25.get_scores(tokenized)
    scored = [
        {"chunk_id": chunk_ids[i], "score": float(scores[i])}
        for i in range(min(len(scores), len(chunk_ids)))
    ]
    scored.sort(key=lambda x: x["score"], reverse=True)
    return [
        {**r, "rank": idx + 1}
        for idx, r in enumerate(scored[:top_k])
    ]
