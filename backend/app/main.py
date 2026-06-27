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

from app.api.routes.repositories import router as repositories_router
from app.api.routes.query import router as query_router

app.include_router(repositories_router)
app.include_router(query_router, prefix="/query", tags=["query"])


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}