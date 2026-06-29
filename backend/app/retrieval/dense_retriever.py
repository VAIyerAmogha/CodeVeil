import logging
from typing import List, Dict, Any
from app.db.mongodb import get_database
from app.ingestion.embedder import embed_query

logger = logging.getLogger(__name__)

async def retrieve_dense(repo_id: str, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
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
                "file_path": 1,
                "function_name": 1,
                "parent_class": 1,
                "start_line": 1,
                "end_line": 1,
                "language": 1,
                "chunk_type": 1,
                "summary": 1,
                "source_code": 1
            }
        }
    ]
    
    cursor = db["chunks"].aggregate(pipeline)
    
    top_results = []
    async for chunk in cursor:
        score = chunk.pop("score", 0.0)
        chunk_id = chunk.pop("chunk_id", "")
        source_code = chunk.get("source_code", "")
        
        top_results.append({
            "chunk_id": chunk_id,
            "score": float(score),
            "source_code": source_code,
            "metadata": chunk
        })
        
    return top_results
