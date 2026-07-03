import re
import time
import asyncio
import logging
from datetime import datetime

from app.retrieval.classifier import classify_and_expand
from app.retrieval.hybrid import hybrid_retrieve
from app.retrieval.context_builder import build_context
from app.generation.responder import generate_answer
from app.db.mongodb import get_database

logger = logging.getLogger(__name__)

# Hard wall-clock budget for the entire query pipeline (embed + retrieve + LLM)
QUERY_TIMEOUT_SECONDS = 90


def _tokenize_simple(text: str) -> list[str]:
    """Lightweight tokenizer for keyword overlap — no external deps."""
    tokens = []
    for word in re.split(r'\s+', text):
        word = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', word)
        word = re.sub(r'[^a-zA-Z0-9]+', ' ', word)
        tokens.extend(word.lower().split())
    return [t for t in tokens if len(t) > 1]


def _compute_confidence(chunks: list, question_tokens: list[str]) -> dict:
    """
    Multi-factor confidence score: semantic similarity + chunk coverage + keyword overlap.

    Returns {"score": 0-100, "level": "high"|"medium"|"low"|"none"}

    The score drives both:
      - The reliability bar in RetrievalStats
      - The CONFIDENCE_ADDENDUM injected into the LLM system prompt
    """
    if not chunks:
        return {"score": 0, "level": "none"}

    # Factor 1 (60%): dense_score of best chunk — cosine similarity [0,1]
    top_dense = max(c.get("dense_score", 0.0) for c in chunks)

    # Factor 2 (20%): chunk coverage — how many relevant chunks surfaced?
    coverage = min(len(chunks) / 6.0, 1.0)

    # Factor 3 (20%): keyword overlap — does the retrieved code actually
    # contain the identifiers the user asked about?
    query_token_set = set(question_tokens)
    combined_code = " ".join(c.get("source_code", "") for c in chunks[:3])
    chunk_token_set = set(_tokenize_simple(combined_code))
    if query_token_set:
        overlap = len(query_token_set & chunk_token_set) / len(query_token_set)
    else:
        overlap = 0.5

    raw = (top_dense * 0.60) + (coverage * 0.20) + (overlap * 0.20)

    score = max(5, min(99, round(raw * 115 - 12)))

    if score >= 68:
        level = "high"
    elif score >= 38:
        level = "medium"
    else:
        level = "low"

    return {"score": score, "level": level}


async def _run_query_pipeline(repo_id: str, question: str) -> dict:
    """
    Core query pipeline. Separated so we can wrap it with a timeout.
    All LLM and I/O calls are fully async — never blocking the event loop.
    """
    # 1. Classify query and get expanded search version (async Groq call)
    query_type, expanded_query = await classify_and_expand(question)

    # 2. Hybrid retrieve — top_k scales with query complexity
    top_k_map = {"lookup": 5, "explanation": 8, "architectural": 12}
    top_k = top_k_map.get(query_type, 6)
    chunks = await hybrid_retrieve(repo_id, expanded_query, top_k=top_k)

    # 3. Compute multi-factor confidence BEFORE building context
    question_tokens = _tokenize_simple(question)
    confidence_data = _compute_confidence(chunks, question_tokens)
    confidence_score = confidence_data["score"]
    confidence_level = confidence_data["level"]

    # 4. Build context string
    context_str, final_chunks = await build_context(chunks, query_type, repo_id)

    # 5. Generate answer — LLM is aware of its own context quality (async)
    result = await generate_answer(question, context_str, query_type, final_chunks, confidence_level)

    retrieval_scores = {
        "bm25_top": chunks[0].get("bm25_score", 0.0) if chunks else 0.0,
        "dense_top": chunks[0].get("dense_score", 0.0) if chunks else 0.0,
        "rerank_top": chunks[0].get("rerank_score", 0.0) if chunks else 0.0,
        "chunks_retrieved": len(chunks),
        "chunks_used": result.get("chunks_used", 0),
        "confidence": confidence_score,
        "confidence_level": confidence_level,
    }

    return {
        "query_type": query_type,
        "answer": result.get("answer", ""),
        "citations": result.get("citations", []),
        "retrieval_scores": retrieval_scores,
    }


async def run_query(repo_id: str, question: str, user_id: str | None = None, save_to_db: bool = True) -> dict:
    start_time = time.perf_counter()

    fallback_answer = (
        "The query timed out or an unexpected error occurred. "
        "Please try again or rephrase your question."
    )

    try:
        pipeline_result = await asyncio.wait_for(
            _run_query_pipeline(repo_id, question),
            timeout=QUERY_TIMEOUT_SECONDS
        )
    except asyncio.TimeoutError:
        logger.error(f"Query pipeline timed out after {QUERY_TIMEOUT_SECONDS}s for: {question!r}")
        pipeline_result = {
            "query_type": "explanation",
            "answer": fallback_answer,
            "citations": [],
            "retrieval_scores": {
                "bm25_top": 0.0, "dense_top": 0.0, "rerank_top": 0.0,
                "chunks_retrieved": 0, "chunks_used": 0,
                "confidence": 0, "confidence_level": "none",
            },
        }
    except Exception as e:
        logger.error(f"Query pipeline error: {e}", exc_info=True)
        pipeline_result = {
            "query_type": "explanation",
            "answer": fallback_answer,
            "citations": [],
            "retrieval_scores": {
                "bm25_top": 0.0, "dense_top": 0.0, "rerank_top": 0.0,
                "chunks_retrieved": 0, "chunks_used": 0,
                "confidence": 0, "confidence_level": "none",
            },
        }

    latency_ms = int((time.perf_counter() - start_time) * 1000)

    final_result = {
        "user_id": user_id,
        "repo_id": repo_id,
        "question": question,
        "query_type": pipeline_result["query_type"],
        "answer": pipeline_result["answer"],
        "citations": pipeline_result["citations"],
        "retrieval_scores": pipeline_result["retrieval_scores"],
        "latency_ms": latency_ms,
        "pinned": False,
        "created_at": datetime.utcnow()
    }

    # Save to MongoDB
    if save_to_db:
        db = get_database()
        if db is not None:
            try:
                doc = dict(final_result)
                result_id = await db["queries"].insert_one(doc)
                final_result["id"] = str(result_id.inserted_id)
            except Exception as e:
                logger.error(f"Failed to save query to DB: {e}")

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
