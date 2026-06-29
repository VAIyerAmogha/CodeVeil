import asyncio
from app.db.mongodb import get_database
from app.services.query_service import run_query
import os

async def main():
    db = get_database()
    repo = await db["repositories"].find_one({"github_url": "https://github.com/Arjun-1807/Unbind-AI"})
    if repo:
        repo_id = repo["repo_id"]
        print("Repo ID:", repo_id)
        try:
            res = await run_query(repo_id, "What is this repo about?")
            print("Query Success:", res.get("answer"))
        except Exception as e:
            print("Query Error:", e)
            import traceback
            traceback.print_exc()
    else:
        print("Repo not found")

asyncio.run(main())
