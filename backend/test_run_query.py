import sys
import asyncio
sys.path.append("/home/amg/Desktop/CodeVeil/backend")
from app.services.query_service import run_query
from pymongo import MongoClient

async def test():
    client = MongoClient("mongodb+srv://amoghavaiyer_db_user:QTuWfN2oYG37p7iS@cluster0.3a7dkye.mongodb.net/?appName=Cluster0")
    repo = client.codeveil.repositories.find_one()
    if not repo:
        print("No repo")
        return
    repo_id = str(repo["_id"])
    print(f"Using repo: {repo_id}")
    
    try:
        res = await run_query(repo_id, "give me the flow of the retrieval pipeline")
        print(res)
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(test())
