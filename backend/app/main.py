from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","https://code-veil.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.routes.repositories import router as repositories_router
from app.api.routes.query import router as query_router
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router

app.include_router(repositories_router)
app.include_router(query_router, prefix="/query", tags=["query"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])

from app.api.routes.indexing import router as indexing_router
app.include_router(indexing_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}