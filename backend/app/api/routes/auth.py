from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from urllib.parse import urlencode

from app.db.models.user import UserCreate
from app.services.auth_service import create_user, authenticate_user, process_google_callback
from app.config import settings

router = APIRouter()

class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/signup")
async def signup(user: UserCreate):
    user_response, token = await create_user(user)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_response
    }

@router.post("/login")
async def login(credentials: UserLogin):
    user_response, token = await authenticate_user(credentials.email, credentials.password)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_response
    }

@router.get("/google")
async def google_login(request: Request):
    redirect_uri = "http://localhost:8000/auth/google/callback"
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline"
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return RedirectResponse(url)

@router.get("/google/callback")
async def google_callback(code: str, request: Request):
    redirect_uri = "http://localhost:8000/auth/google/callback"
    token = await process_google_callback(code, redirect_uri)
    return RedirectResponse(url=f"http://localhost:3000/auth/callback?token={token}")
