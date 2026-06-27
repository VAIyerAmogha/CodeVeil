import time
from datetime import datetime

from app.retrieval.classifier import classify_query
from app.retrieval.hybrid import hybrid_retrieve
from app.retrieval.context_builder import build_context
from app.generation.responder import generate_answer
from app.db.mongodb import get_database


async def run_query(repo_id: str, question: str, user_id: str | None = None) -> dict:
    start_time = time.perf_counter()

    # 1. Classify query
    query_type = classify_query(question)

    # 2. Hybrid retrieve
    chunks = await hybrid_retrieve(repo_id, question, top_k=5)

    # 3. Build context
    context_str, final_chunks = await build_context(chunks, query_type, repo_id)

    # 4. Generate answer
    result = generate_answer(question, context_str, query_type, final_chunks)

    # Record latency
    latency_ms = int((time.perf_counter() - start_time) * 1000)

    # Calculate retrieval scores
    retrieval_scores = {
        "bm25_top": chunks[0].get("bm25_score", 0.0) if chunks else 0.0,
        "dense_top": chunks[0].get("dense_score", 0.0) if chunks else 0.0,
        "rerank_top": chunks[0].get("rerank_score", 0.0) if chunks else 0.0,
        "chunks_retrieved": 40,  # 20 BM25 + 20 dense before dedup
        "chunks_used": result.get("chunks_used", 0)
    }

    final_result = {
        "user_id": user_id,
        "repo_id": repo_id,
        "question": question,
        "query_type": query_type,
        "answer": result.get("answer", ""),
        "citations": result.get("citations", []),
        "retrieval_scores": retrieval_scores,
        "latency_ms": latency_ms,
        "pinned": False,
        "created_at": datetime.utcnow()
    }

    # Save to MongoDB
    db = get_database()
    if db is not None:
        doc = dict(final_result)
        result_id = await db["queries"].insert_one(doc)
        final_result["id"] = str(result_id.inserted_id)
        
    return final_result

async def get_queries_for_repo(repo_id: str) -> list[dict]:
    db = get_database()
    if db is None:
        return []
        
    cursor = db["queries"].find({"repo_id": repo_id}).sort("created_at", -1).limit(20)
    queries = await cursor.to_list(length=20)
    
    for q in queries:
        q["id"] = str(q.pop("_id"))
        if isinstance(q.get("created_at"), datetime):
            q["created_at"] = q["created_at"].isoformat() + "Z"
            
    return queries
