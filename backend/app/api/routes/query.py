from fastapi import APIRouter
from pydantic import BaseModel

from app.services.query_service import run_query

router = APIRouter()

class QueryRequest(BaseModel):
    repo_id: str
    question: str

@router.post("")
async def post_query(request: QueryRequest) -> dict:
    # TODO: Require auth via dependencies.py (skip auth guard for now if auth not yet wired)
    # user_id will be extracted from auth token once wired
    user_id = None
    
    result = await run_query(request.repo_id, request.question, user_id)
    return result
