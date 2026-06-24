from motor.motor_asyncio import AsyncIOMotorClient  # type: ignore[import-not-found]
from app.config import settings

_client: AsyncIOMotorClient | None = None
if settings.mongodb_url:
    _client = AsyncIOMotorClient(settings.mongodb_url)

def get_database():
    if _client is not None:
        return _client[settings.mongodb_db_name]
    return None

async def ping() -> bool:
    if _client is None:
        return False
    try:
        await _client.admin.command('ping')
        return True
    except Exception:
        return False
