import logging
from typing import List, Dict, Any
from app.db.mongodb import get_database
from app.ingestion.embedder import embed_query

logger = logging.getLogger(__name__)

async def retrieve_dense(repo_id: str, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
    """
    Retrieve top-k semantically similar chunks via MongoDB Atlas Vector Search.
    Returns flat dicts with: chunk_id, score, source_code, file_path,
    start_line, end_line, function_name, parent_class, language,
    chunk_type, summary.
    """
    query_vector = await embed_query(query)

    db = get_database()
    if db is None:
        raise RuntimeError("Database connection not available to fetch metadata")

    pipeline = [
        {
            "$vectorSearch": {
                "index": "chunks_vector_index",
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 150,
                "limit": top_k,
                "filter": {"repo_id": {"$eq": repo_id}}
            }
        },
        {
            "$project": {
                "_id": 0,
                "score": {"$meta": "vectorSearchScore"},
                "chunk_id": "$chroma_id",
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
        }
    ]

    cursor = db["chunks"].aggregate(pipeline)

    top_results = []
    async for chunk in cursor:
        top_results.append({
            "chunk_id": chunk.get("chunk_id", ""),
            "score": float(chunk.get("score", 0.0)),
            "source_code": chunk.get("source_code", ""),
            "file_path": chunk.get("file_path"),
            "start_line": chunk.get("start_line"),
            "end_line": chunk.get("end_line"),
            "function_name": chunk.get("function_name"),
            "parent_class": chunk.get("parent_class"),
            "language": chunk.get("language"),
            "chunk_type": chunk.get("chunk_type"),
            "summary": chunk.get("summary"),
        })

    return top_results
