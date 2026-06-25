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
routers = [repositories_router]

for router in routers:
    app.include_router(router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}