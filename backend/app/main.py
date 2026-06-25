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


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}