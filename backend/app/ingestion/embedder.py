import logging
import asyncio
from typing import List
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

HF_EMBED_URL = (
    "https://router.huggingface.co/hf-inference/models/"
    "BAAI/bge-base-en-v1.5/pipeline/feature-extraction"
)
EMBED_DIM = 768


async def _call_hf_embed(
    client: httpx.AsyncClient, inputs: list[str], max_retries: int = 6
) -> list[list[float]]:
    headers = {"Authorization": f"Bearer {settings.hf_token}"}
    payload = {"inputs": inputs}

    for attempt in range(max_retries):
        try:
            response = await client.post(
                HF_EMBED_URL, headers=headers, json=payload
            )

            if response.status_code == 503:
                # Model loading (cold start)
                try:
                    data = response.json()
                    wait_time = data.get("estimated_time", 20)
                except Exception:
                    wait_time = 20
                logger.warning(
                    f"HF model cold start, waiting {wait_time}s "
                    f"(attempt {attempt + 1}/{max_retries})"
                )
                await asyncio.sleep(min(wait_time + 1, 30))
                continue

            if response.status_code == 429:
                wait_time = 10 * (attempt + 1)
                logger.warning(
                    f"HF rate limited. Waiting {wait_time}s "
                    f"(attempt {attempt + 1}/{max_retries})"
                )
                await asyncio.sleep(wait_time)
                continue

            response.raise_for_status()
            result = response.json()
            # bge models return embeddings directly as list of lists,
            # or sometimes wrapped as [batch][tokens][dim] - handle both
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], list) and isinstance(result[0][0], list):
                    # Mean pool token-level embeddings if returned 3D
                    return [
                        [sum(dim) / len(dim) for dim in zip(*tokens)]
                        for tokens in result
                    ]
                return result
            raise RuntimeError(f"Unexpected HF response shape: {result}")

        except httpx.HTTPStatusError as e:
            err_text = e.response.text if e.response else str(e)
            logger.error(f"HF embedding HTTP error: {err_text}")
            if attempt == max_retries - 1:
                raise RuntimeError(f"HF embedding failed: {err_text}")
            await asyncio.sleep(5 * (attempt + 1))
        except Exception as e:
            logger.error(f"HF embedding error: {e}")
            if attempt == max_retries - 1:
                raise RuntimeError(f"HF embedding failed: {e}")
            await asyncio.sleep(5 * (attempt + 1))

    raise RuntimeError("HF embedding failed after all retries")


async def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed document chunks for indexing."""
    if not texts:
        return []

    all_embeddings = []
    batch_size = 50

    async with httpx.AsyncClient(timeout=60.0) as client:
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            embeddings = await _call_hf_embed(client, batch)
            all_embeddings.extend(embeddings)

    return all_embeddings


async def embed_query(text: str) -> List[float]:
    """Embed a user query for retrieval."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        embeddings = await _call_hf_embed(client, [text])
        return embeddings[0]
