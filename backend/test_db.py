import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["codeveil"]
    doc = await db.queries.find_one({})
    if doc:
        print("Query:", doc.get("question"))
        print("Citations:", doc.get("citations"))
    else:
        print("No queries found")

asyncio.run(main())
