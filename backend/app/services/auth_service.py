from datetime import datetime, timezone
import httpx
import bcrypt
from fastapi import HTTPException
from app.db.mongodb import get_database
from app.db.models.user import UserCreate, UserResponse, UserUsage
from app.core.auth.jwt import create_access_token
from app.config import settings

async def create_user(user: UserCreate) -> tuple[dict, str]:
    db = get_database()
    users_collection = db["users"]
    
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    now = datetime.now(timezone.utc)
    new_user = {
        "email": user.email,
        "name": user.name,
        "password_hash": hashed_password,
        "oauth_provider": None,
        "oauth_id": None,
        "created_at": now,
        "usage": {
            "repos_indexed": 0,
            "queries_made": 0,
            "last_active": now
        }
    }
    
    result = await users_collection.insert_one(new_user)
    user_id = str(result.inserted_id)
    
    token = create_access_token({"user_id": user_id, "email": user.email})
    
    user_response = {
        "id": user_id,
        "email": user.email,
        "name": user.name,
        "usage": new_user["usage"]
    }
    
    return user_response, token

async def authenticate_user(email: str, password: str) -> tuple[dict, str]:
    db = get_database()
    users_collection = db["users"]
    
    user = await users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.get("password_hash") or not bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user_id = str(user["_id"])
    token = create_access_token({"user_id": user_id, "email": user["email"]})
    
    user_response = {
        "id": user_id,
        "email": user["email"],
        "name": user.get("name", ""),
        "usage": user.get("usage", {"repos_indexed": 0, "queries_made": 0, "last_active": datetime.now(timezone.utc)})
    }
    
    return user_response, token

async def process_google_callback(code: str, redirect_uri: str) -> str:
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri
    }
    
    async with httpx.AsyncClient() as client:
        token_res = await client.post(token_url, data=data)
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange token with Google")
            
        token_data = token_res.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token returned from Google")
            
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        userinfo_res = await client.get(userinfo_url, headers=headers)
        
        if userinfo_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch user info from Google")
            
        user_info = userinfo_res.json()
        
    google_id = user_info.get("sub")
    email = user_info.get("email")
    name = user_info.get("name", "")
    
    if not google_id or not email:
        raise HTTPException(status_code=400, detail="Incomplete user info from Google")
        
    db = get_database()
    users_collection = db["users"]
    
    existing_user = await users_collection.find_one({"oauth_id": google_id})
    now = datetime.now(timezone.utc)
    
    if existing_user:
        await users_collection.update_one(
            {"_id": existing_user["_id"]},
            {"$set": {"usage.last_active": now}}
        )
        user_id = str(existing_user["_id"])
    else:
        new_user = {
            "email": email,
            "name": name,
            "oauth_provider": "google",
            "oauth_id": google_id,
            "created_at": now,
            "usage": {
                "repos_indexed": 0,
                "queries_made": 0,
                "last_active": now
            }
        }
        result = await users_collection.insert_one(new_user)
        user_id = str(result.inserted_id)
        
    token = create_access_token({"user_id": user_id, "email": email})
    return token
