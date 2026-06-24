from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserUsage(BaseModel):
    repos_indexed: int = 0
    queries_made: int = 0
    last_active: Optional[datetime] = None

class UserBase(BaseModel):
    email: str
    name: str
    oauth_provider: Optional[str] = None
    oauth_id: Optional[str] = None

class UserCreate(UserBase):
    password_hash: Optional[str] = None

class UserInDB(UserBase):
    id: str
    password_hash: Optional[str] = None
    created_at: datetime
    usage: UserUsage

class UserPublic(UserBase):
    id: str
    created_at: datetime
    usage: UserUsage
