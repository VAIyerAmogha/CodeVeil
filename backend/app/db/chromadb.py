import chromadb
from chromadb.config import Settings as ChromaSettings  # type: ignore[import-not-found]
from app.config import settings

_client = chromadb.HttpClient(
    host=settings.chroma_host,
    port=settings.chroma_port,
    settings=ChromaSettings(anonymized_telemetry=False)
)

def get_chroma_client():
    return _client

def ping() -> bool:
    try:
        _client.heartbeat()
        return True
    except Exception:
        return False
