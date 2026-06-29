import asyncio
from app.db.mongodb import get_database
from app.ingestion.indexer import process_batch

async def main():
    db = get_database()
    repo = await db["repositories"].find_one({"github_url": "https://github.com/Arjun-1807/Unbind-AI"})
    if repo:
        job = await db["jobs"].find_one({"repo_id": repo["repo_id"]})
        if job:
            try:
                res = await process_batch(repo["repo_id"], "https://github.com/Arjun-1807/Unbind-AI", job["job_id"])
                print("Success:", res)
            except Exception as e:
                import traceback
                traceback.print_exc()
        else:
            print("No job")
    else:
        print("No repo")

asyncio.run(main())
