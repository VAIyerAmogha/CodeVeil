import logging
from typing import List, Dict, Any
from app.db.chromadb import get_chroma_client
from app.db.mongodb import get_database
from app.ingestion.indexer import embedding_model

logger = logging.getLogger(__name__)


async def retrieve_dense(repo_id: str, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
    """
    Embed the query using the SentenceTransformer singleton from indexer.py.
    Query ChromaDB collection for this repo_id.
    Fetch corresponding metadata from MongoDB chunks collection.
    Return top_k results.
    Each result: {chunk_id, score, metadata} where score is cosine similarity.
    """
    client = get_chroma_client()
    try:
        collection = client.get_collection(name=repo_id)
    except Exception as e:
        logger.error(f"Failed to retrieve ChromaDB collection for repo {repo_id}: {e}")
        raise ValueError(f"ChromaDB collection for repository '{repo_id}' does not exist.")

    # Embed the query using the singleton SentenceTransformer
    query_vector = embedding_model.encode(query).tolist()

    # Query ChromaDB (returns distances sorted ascending, i.e., most similar first)
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["distances"]
    )

    if not results or not results["ids"] or not results["ids"][0]:
        return []

    chroma_ids = results["ids"][0]
    distances = results["distances"][0]

    # Fetch chunk metadata from MongoDB
    db = get_database()
    if db is None:
        raise RuntimeError("Database connection not available to fetch metadata")

    chunks_cursor = db["chunks"].find(
        {"repo_id": repo_id, "chroma_id": {"$in": chroma_ids}}
    )

    chunk_metadata_map = {}
    async for chunk in chunks_cursor:
        meta = {
            "file_path": chunk.get("file_path"),
            "function_name": chunk.get("function_name"),
            "parent_class": chunk.get("parent_class"),
            "start_line": chunk.get("start_line"),
            "end_line": chunk.get("end_line"),
            "language": chunk.get("language"),
            "chunk_type": chunk.get("chunk_type"),
            "summary": chunk.get("summary"),
        }
        chunk_metadata_map[chunk["chroma_id"]] = meta

    # Reconstruct top_k results matching ChromaDB's order
    top_results = []
    for chroma_id, distance in zip(chroma_ids, distances):
        # Calculate cosine similarity score (ChromaDB returns cosine distance: 1.0 - cosine_similarity)
        score = 1.0 - distance

        metadata = chunk_metadata_map.get(chroma_id, {})
        top_results.append({
            "chunk_id": chroma_id,
            "score": float(score),
            "metadata": metadata
        })

    return top_results
