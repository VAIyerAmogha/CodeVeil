import asyncio
import os
import uuid
import pickle
from pprint import pprint

from app.ingestion.indexer import index_repo
from app.services.indexing_job import create_job, get_job
from app.db import mongodb
from app.db.mongodb import get_database
from app.db.chromadb import get_chroma_client
from app.config import settings
from motor.motor_asyncio import AsyncIOMotorClient

async def test_indexer():
    print("--- STARTING PHASE 2.5 INDEXER TEST ---")
    
    # Re-initialize the motor client inside the event loop
    if settings.mongodb_url:
        mongodb._client = AsyncIOMotorClient(settings.mongodb_url)
    
    # 1. Setup mock repo data
    repo_id = str(uuid.uuid4())
    github_url = "https://github.com/mock/repo"
    clone_path = "/home/amg/Desktop/PreFlight/" # Make sure this exists on your machine
    
    if not os.path.exists(clone_path):
        print(f"Error: clone_path {clone_path} does not exist. Please update test.py with a valid path.")
        return

    # 2. Create the job in MongoDB (so index_repo can update progress)
    job_id = await create_job(repo_id, github_url)
    print(f"Created job in MongoDB with ID: {job_id}")

    # 3. Run the indexer
    print("\nRunning index_repo...")
    result = await index_repo(repo_id=repo_id, clone_path=clone_path, job_id=job_id)
    print("index_repo completed with result:")
    pprint(result)

    # 4. Verify Job Status
    print("\nVerifying Job Document in MongoDB:")
    job_doc = await get_job(job_id)
    pprint(job_doc)
    
    db = get_database()
    if db is None:
        print("Database not connected.")
        return

    # 5. Verify MongoDB Chunks
    mongo_chunks = await db["chunks"].count_documents({"repo_id": repo_id})
    print(f"\nMongoDB verification: Found {mongo_chunks} chunks inserted for repo_id: {repo_id}")

    # 6. Verify ChromaDB Embeddings
    chroma_client = get_chroma_client()
    try:
        collection = chroma_client.get_collection(name=repo_id)
        chroma_count = collection.count()
        print(f"ChromaDB verification: Found {chroma_count} embeddings in collection '{repo_id}'")
        
        # Peek at one embedding to prove it's there
        if chroma_count > 0:
            peek = collection.peek(1)
            print("Successfully retrieved a sample document from ChromaDB!")
    except Exception as e:
        print(f"ChromaDB verification failed: {e}")

    # 7. Verify BM25 Index
    bm25_path = f"/tmp/codeveil_bm25/{repo_id}.pkl"
    if os.path.exists(bm25_path):
        with open(bm25_path, "rb") as f:
            bm25 = pickle.load(f)
        print(f"BM25 verification: Successfully loaded BM25 index with {len(bm25.corpus_size if hasattr(bm25, 'corpus_size') else bm25.doc_freqs)} documents from {bm25_path}")
    else:
        print(f"BM25 verification failed: File not found at {bm25_path}")
        
    print("\n--- TEST COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(test_indexer())