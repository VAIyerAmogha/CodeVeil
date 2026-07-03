import logging
import asyncio
from typing import List, Dict, Any
from app.db.mongodb import get_database
from app.retrieval.bm25_retriever import retrieve_bm25
from app.retrieval.dense_retriever import retrieve_dense

logger = logging.getLogger(__name__)


def merge_results(
    bm25_results: List[Dict[str, Any]],
    dense_results: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Merge BM25 and Dense retrieval results by chunk_id.
    Dense results already carry full metadata; BM25 results have only chunk_id + score.
    Priority: dense metadata wins when available (richer and already fetched).
    """
    # Index dense results for O(1) lookup
    dense_map: Dict[str, Dict[str, Any]] = {r["chunk_id"]: r for r in dense_results}

    merged_map: Dict[str, Dict[str, Any]] = {}

    # Start with dense results (they carry full metadata)
    for r in dense_results:
        cid = r["chunk_id"]
        if not cid:
            continue
        merged_map[cid] = {
            "chunk_id": cid,
            "bm25_score": 0.0,
            "dense_score": r["score"],
            "source_code": r.get("source_code", ""),
            "file_path": r.get("file_path"),
            "start_line": r.get("start_line"),
            "end_line": r.get("end_line"),
            "function_name": r.get("function_name"),
            "parent_class": r.get("parent_class"),
            "language": r.get("language"),
            "chunk_type": r.get("chunk_type"),
            "summary": r.get("summary"),
        }

    # Layer in BM25 scores
    for r in bm25_results:
        cid = r["chunk_id"]
        if not cid:
            continue
        if cid in merged_map:
            merged_map[cid]["bm25_score"] = r["score"]
        else:
            # BM25-only hit — metadata must be fetched from MongoDB later
            merged_map[cid] = {
                "chunk_id": cid,
                "bm25_score": r["score"],
                "dense_score": 0.0,
                "source_code": "",       # filled in below
                "file_path": None,
                "start_line": None,
                "end_line": None,
                "function_name": None,
                "parent_class": None,
                "language": None,
                "chunk_type": None,
                "summary": None,
            }

    return list(merged_map.values())


def rerank(
    query: str,
    chunks: List[Dict[str, Any]],
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Combined-score reranker.
    dense_score (primary, 0-1) + normalised bm25_score (secondary).
    Sorts descending. Returns top_k with rerank_score attached.
    """
    if not chunks:
        return []

    # Normalise BM25 scores to [0, 1] so they don't swamp dense scores
    bm25_max = max((c.get("bm25_score", 0.0) for c in chunks), default=1.0) or 1.0

    for chunk in chunks:
        bm25_norm = chunk.get("bm25_score", 0.0) / bm25_max
        dense = chunk.get("dense_score", 0.0)
        chunk["rerank_score"] = float(dense * 0.75 + bm25_norm * 0.25)

    chunks.sort(key=lambda x: x["rerank_score"], reverse=True)
    return chunks[:top_k]


async def hybrid_retrieve(
    repo_id: str,
    query: str,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Parallel BM25 + Dense retrieval → merge → fill missing metadata → rerank → top_k.

    Dense results already carry full metadata from the $project stage.
    BM25-only hits need a single batched MongoDB fetch to hydrate their metadata.
    """
    # ── 1. Run both retrievers in parallel ────────────────────────────────────
    bm25_results, dense_results = await asyncio.gather(
        retrieve_bm25(repo_id, query, top_k=20),
        retrieve_dense(repo_id, query, top_k=20),
        return_exceptions=True,
    )

    # Graceful degradation if one leg fails
    if isinstance(bm25_results, Exception):
        logger.warning(f"BM25 retrieval failed: {bm25_results}")
        bm25_results = []
    if isinstance(dense_results, Exception):
        logger.warning(f"Dense retrieval failed: {dense_results}")
        dense_results = []

    if not bm25_results and not dense_results:
        return []

    # ── 2. Merge ───────────────────────────────────────────────────────────────
    merged = merge_results(bm25_results, dense_results)

    # ── 3. Hydrate BM25-only chunks that have no metadata yet ─────────────────
    bm25_only_ids = [
        c["chunk_id"] for c in merged
        if c["dense_score"] == 0.0 and not c.get("source_code")
    ]

    if bm25_only_ids:
        db = get_database()
        if db is not None:
            cursor = db["chunks"].find(
                {"repo_id": repo_id, "chroma_id": {"$in": bm25_only_ids}},
                {
                    "chroma_id": 1,
                    "source_code": 1,
                    "file_path": 1,
                    "start_line": 1,
                    "end_line": 1,
                    "function_name": 1,
                    "parent_class": 1,
                    "language": 1,
                    "chunk_type": 1,
                    "summary": 1,
                }
            )
            id_to_doc: Dict[str, Dict] = {}
            async for doc in cursor:
                id_to_doc[doc["chroma_id"]] = doc

            # Patch in the metadata
            for chunk in merged:
                cid = chunk["chunk_id"]
                if cid in id_to_doc:
                    doc = id_to_doc[cid]
                    chunk["source_code"]   = doc.get("source_code", "")
                    chunk["file_path"]     = doc.get("file_path")
                    chunk["start_line"]    = doc.get("start_line")
                    chunk["end_line"]      = doc.get("end_line")
                    chunk["function_name"] = doc.get("function_name")
                    chunk["parent_class"]  = doc.get("parent_class")
                    chunk["language"]      = doc.get("language")
                    chunk["chunk_type"]    = doc.get("chunk_type")
                    chunk["summary"]       = doc.get("summary")

    # ── 4. Drop chunks that still have no source code (couldn't hydrate) ──────
    merged = [c for c in merged if c.get("source_code")]

    if not merged:
        return []

    # ── 5. Rerank and return top_k ─────────────────────────────────────────────
    return rerank(query, merged, top_k=top_k)
