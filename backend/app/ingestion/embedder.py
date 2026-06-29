import logging
from typing import List
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

GEMINI_EMBED_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-embedding-001:batchEmbedContents"
)
EMBED_DIM = 768

async def embed_texts(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []
        
    import asyncio
    all_embeddings = []
    chunk_size = 50  # Lowered to stay under 100 requests per minute more gracefully
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for i in range(0, len(texts), chunk_size):
            batch = texts[i:i + chunk_size]
            payload = {
                "requests": [
                    {
                        "model": "models/gemini-embedding-001",
                        "content": {"parts": [{"text": t}]},
                        "outputDimensionality": 768
                    }
                    for t in batch
                ]
            }
            
            retries = 6
            for attempt in range(retries):
                try:
                    response = await client.post(
                        f"{GEMINI_EMBED_URL}?key={settings.gemini_api_key}",
                        json=payload
                    )
                    
                    if response.status_code == 429:
                        if attempt < retries - 1:
                            # Wait for 10s, 20s, 30s etc.
                            await asyncio.sleep(10 * (attempt + 1))
                            continue
                            
                    response.raise_for_status()
                    data = response.json()
                    
                    for item in data.get("embeddings", []):
                        all_embeddings.append(item.get("values", []))
                        
                    break # Success, exit retry loop
                    
                except Exception as e:
                    if attempt < retries - 1 and hasattr(e, 'response') and e.response and e.response.status_code == 429:
                        await asyncio.sleep(10 * (attempt + 1))
                        continue
                        
                    err_text = getattr(e, 'text', str(e))
                    if hasattr(e, 'response') and e.response:
                        err_text = e.response.text
                    logger.error(f"Failed to embed texts with Gemini: {err_text}")
                    raise RuntimeError(f"Failed to embed texts with Gemini: {err_text}")
                    
            # Small delay between successful batches to spread out API load
            await asyncio.sleep(1.5)
            
    return all_embeddings

async def embed_query(text: str) -> List[float]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={settings.gemini_api_key}"
    payload = {
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": text}]},
        "outputDimensionality": 768
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("embedding", {}).get("values", [])
            
        except Exception as e:
            err_text = getattr(e, 'text', str(e))
            if hasattr(e, 'response') and e.response:
                err_text = e.response.text
            logger.error(f"Failed to embed query with Gemini: {err_text}")
            raise RuntimeError(f"Failed to embed query with Gemini: {err_text}")

