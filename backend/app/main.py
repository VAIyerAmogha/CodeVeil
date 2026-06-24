from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

routers = []

for router in routers:
    app.include_router(router)


from app.db import mongodb, chromadb

@app.get("/health")
async def health() -> dict[str, str]:
    mongo_status = "ok" if await mongodb.ping() else "error"
    chroma_status = "ok" if chromadb.ping() else "error"
    return {"mongodb": mongo_status, "chromadb": chroma_status}