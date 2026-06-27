from fastapi import APIRouter, Depends, HTTPException
from app.core.auth.dependencies import get_current_user
from app.db.mongodb import get_database

router = APIRouter()

@router.get("/me")
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    db = get_database()
    user_doc = await db["users"].find_one({"_id": current_user["user_id"]})
    
    if not user_doc:
        # Fallback to checking by string if user_id in token is stored differently
        from bson.objectid import ObjectId
        try:
            user_doc = await db["users"].find_one({"_id": ObjectId(current_user["user_id"])})
        except Exception:
            pass
            
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
        
    user_id = str(user_doc["_id"])
    return {
        "id": user_id,
        "email": user_doc["email"],
        "name": user_doc.get("name", ""),
        "usage": user_doc.get("usage", {})
    }
