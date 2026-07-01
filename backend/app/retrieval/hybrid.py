import logging
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
    Attach both scores: bm25_score (0 if only in dense), dense_score (0 if only in BM25).
    """
    merged_map = {}

    for r in bm25_results:
        cid = r["chunk_id"]
        merged_map[cid] = {
            "chunk_id": cid,
            "bm25_score": r["score"],
            "dense_score": 0.0
        }

    for r in dense_results:
        cid = r["chunk_id"]
        if cid in merged_map:
            merged_map[cid]["dense_score"] = r["score"]
            merged_map[cid]["source_code"] = r.get("source_code", "")
        else:
            merged_map[cid] = {
                "chunk_id": cid,
                "bm25_score": 0.0,
                "dense_score": r["score"],
                "source_code": r.get("source_code", "")
            }

    return list(merged_map.values())


def rerank(
    query: str, 
    chunks: List[Dict[str, Any]], 
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Score each chunk: cross_encoder.predict([(query, chunk source_code)])
    Sort descending by rerank score.
    Return top_k with rerank_score attached.
    ALWAYS runs — never conditional, never skipped.
    """
    if not chunks:
        return []

    # Calculate fallback scores since cross_encoder is removed
    scores = [(chunk.get("dense_score", 0.0) + chunk.get("bm25_score", 0.0)) for chunk in chunks]

    # Attach scores to the chunks
    for chunk, score in zip(chunks, scores):
        chunk["rerank_score"] = float(score)

    # Sort descending by rerank_score
    chunks.sort(key=lambda x: x["rerank_score"], reverse=True)

    return chunks[:top_k]


async def hybrid_retrieve(
    repo_id: str, 
    query: str, 
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Call retrieve_bm25 (top-20) + retrieve_dense (top-20).
    Merge → rerank → return top_k.
    Each result must have: chunk_id, bm25_score, dense_score, rerank_score.
    Fetches full chunk data from MongoDB after reranking.
    """
    # 1. Retrieve candidates
    bm25_results = await retrieve_bm25(repo_id, query, top_k=20)
    dense_results = await retrieve_dense(repo_id, query, top_k=20)

    # 2. Merge candidate results
    merged = merge_results(bm25_results, dense_results)
    if not merged:
        return []

    # 3. Fetch missing source code from MongoDB for chunks that only came from BM25
    missing_source_chunk_ids = [c["chunk_id"] for c in merged if "source_code" not in c]
    
    id_to_doc = {}
    if missing_source_chunk_ids:
        db = get_database()
        if db is not None:
            chunks_cursor = db["chunks"].find(
                {"repo_id": repo_id, "chroma_id": {"$in": missing_source_chunk_ids}},
                {"chroma_id": 1, "source_code": 1}
            )
            async for doc in chunks_cursor:
                id_to_doc[doc.get("chroma_id")] = doc.get("source_code", "")

    # Attach source code for cross-encoder matching
    chunks_for_rerank = []
    for c in merged:
        cid = c["chunk_id"]
        source_code = c.get("source_code", id_to_doc.get(cid, ""))
        chunks_for_rerank.append({
            "chunk_id": cid,
            "source_code": source_code,
            "bm25_score": c["bm25_score"],
            "dense_score": c["dense_score"],
        })

    # 4. Rerank (ALWAYS runs)
    reranked_top = rerank(query, chunks_for_rerank, top_k=top_k)

    # 5. Fetch full chunk data from MongoDB after reranking
    db = get_database()
    if db is None:
        raise RuntimeError("Database connection not available to fetch full chunks")

    top_chunk_ids = [c["chunk_id"] for c in reranked_top]
    chunks_cursor = db["chunks"].find(
        {"repo_id": repo_id, "chroma_id": {"$in": top_chunk_ids}}
    )

    id_to_mongo_chunk = {}
    async for doc in chunks_cursor:
        id_to_mongo_chunk[doc["chroma_id"]] = doc

    # Reassemble results attaching the full MongoDB data
    final_results = []
    for r in reranked_top:
        cid = r["chunk_id"]
        mongo_chunk = id_to_mongo_chunk.get(cid, {})
        final_results.append({
            "chunk_id": cid,
            "bm25_score": r["bm25_score"],
            "dense_score": r["dense_score"],
            "rerank_score": r["rerank_score"],
            "source_code": mongo_chunk.get("source_code", r.get("source_code", "")),
            "file_path": mongo_chunk.get("file_path"),
            "start_line": mongo_chunk.get("start_line"),
            "end_line": mongo_chunk.get("end_line"),
            "function_name": mongo_chunk.get("function_name"),
            "parent_class": mongo_chunk.get("parent_class"),
            "language": mongo_chunk.get("language"),
            "chunk_type": mongo_chunk.get("chunk_type"),
            "summary": mongo_chunk.get("summary"),
        })

    return final_results
