from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.services.query_service import run_query
from app.core.auth.dependencies import get_current_user

router = APIRouter()

class QueryRequest(BaseModel):
    repo_id: str
    question: str

@router.post("")
async def post_query(request: QueryRequest, current_user: dict = Depends(get_current_user)) -> dict:
    user_id = current_user["user_id"]
    
    result = await run_query(request.repo_id, request.question, user_id)
    return result
