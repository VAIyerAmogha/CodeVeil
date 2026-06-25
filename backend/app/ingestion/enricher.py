import logging
import textwrap
import ast
import asyncio
import hashlib
from itertools import cycle
from groq import AsyncGroq
from app.config import settings
from app.db.mongodb import get_database

logger = logging.getLogger(__name__)

keys = []
if settings.groq_api_keys:
    keys = [k.strip() for k in settings.groq_api_keys.split(",") if k.strip()]
elif settings.groq_api_key:
    keys = [settings.groq_api_key.strip()]

# Create a client for each key and cycle through them
groq_clients = [AsyncGroq(api_key=k) for k in keys]
client_cycle = cycle(groq_clients) if groq_clients else None

MODEL_NAME = "llama-3.1-8b-instant"

# Control the concurrency rate for Groq API
# Free tier Groq usually allows ~30 RPM per key.
MAX_CONCURRENT_REQUESTS = 3 * max(1, len(keys))


def has_docstring(source_code: str, language: str) -> bool:
    """
    Checks if a given source code chunk has a docstring/comment.
    Python: checks for a docstring (triple-quote string) as the first statement.
    JS/TS: checks for /** */ or // comment before the function body.
    Java: checks for /** */ javadoc.
    """
    if not source_code:
        return False

    code_trimmed = source_code.strip()

    if language == "python":
        # Try using AST first for accuracy, handle indented methods
        try:
            tree = ast.parse(textwrap.dedent(source_code))
            if tree.body and isinstance(
                tree.body[0], (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            ):
                return ast.get_docstring(tree.body[0]) is not None
        except Exception:
            pass
        # Fallback to string check
        return '"""' in source_code or "'''" in source_code

    elif language in ["javascript", "typescript"]:
        return code_trimmed.startswith("/**") or code_trimmed.startswith("//")

    elif language == "java":
        return code_trimmed.startswith("/**")

    return False


async def enrich_chunk(chunk: dict, semaphore: asyncio.Semaphore) -> str | None:
    """
    Generates a one-line summary for a function chunk using Groq asynchronously.
    Only called for chunks without docstrings. Returns the summary or None on error.
    Handles rate limits using exponential backoff.
    """
    async with semaphore:
        if not client_cycle:
            logger.error("No Groq API keys available.")
            return None

        try:
            source_code = chunk.get("source_code", "")
            
            # 1. Check Cache
            sha256_hash = hashlib.sha256(source_code.encode("utf-8")).hexdigest()
            db = get_database()
            if db is not None:
                cached = await db["summaries_cache"].find_one({"_id": sha256_hash})
                if cached:
                    return cached.get("summary")

            prompt = f"In one sentence, describe what this function does:\n\n{source_code}"

            max_retries = 5
            base_delay = 4

            for attempt in range(max_retries):
                try:
                    # Pick the next client in the round-robin pool
                    current_client = next(client_cycle)
                    
                    response = await current_client.chat.completions.create(
                        messages=[
                            {
                                "role": "user",
                                "content": prompt,
                            }
                        ],
                        model=MODEL_NAME,
                    )
                    
                    # Add a tiny delay on success to prevent instant bursts that trip RPM limits
                    await asyncio.sleep(1.0)
                    
                    summary = response.choices[0].message.content.strip()
                    
                    # 2. Save to Cache
                    if db is not None:
                        await db["summaries_cache"].update_one(
                            {"_id": sha256_hash},
                            {"$set": {"summary": summary}},
                            upsert=True
                        )
                        
                    return summary
                
                except Exception as e:
                    error_msg = str(e).lower()
                    if "rate limit" in error_msg or "429" in error_msg:
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)
                            
                            # Attempt to parse specific wait time from Groq error message
                            import re
                            match = re.search(r"try again in ([0-9.]+)s", error_msg)
                            if match:
                                parsed_delay = float(match.group(1))
                                delay = max(delay, parsed_delay + 0.5)
                                
                            logger.warning(f"Groq API rate limit hit. Retrying in {delay}s...")
                            await asyncio.sleep(delay)
                        else:
                            logger.error(f"Groq API rate limit exceeded after {max_retries} attempts.")
                            return None
                    else:
                        logger.error(f"Groq API error during chunk enrichment: {e}")
                        return None
                        
            return None

        except Exception as e:
            logger.error(f"Unexpected error in enrich_chunk: {e}")
            return None


async def enrich_chunks(chunks: list[dict]) -> list[dict]:
    """
    Iterates over chunks and asynchronously calls enrich_chunk for 'function' chunks that
    lack a docstring. Adds a 'summary' key to each chunk (string or None).
    Uses asyncio.gather to process all missing docstrings concurrently.
    """
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    tasks = []
    chunk_refs = []

    for chunk in chunks:
        # Default summary to None
        chunk["summary"] = None

    if not settings.enable_enrichment:
        return chunks

    for chunk in chunks:
        chunk_type = chunk.get("chunk_type")
        source_code = chunk.get("source_code", "")
        language = chunk.get("language", "")

        if chunk_type == "function" and not has_docstring(source_code, language):
            tasks.append(enrich_chunk(chunk, semaphore))
            chunk_refs.append(chunk)

    if tasks:
        # Process concurrently
        summaries = await asyncio.gather(*tasks, return_exceptions=True)
        for i, summary in enumerate(summaries):
            if not isinstance(summary, Exception):
                chunk_refs[i]["summary"] = summary
            else:
                logger.error(f"Unhandled exception in enrichment task: {summary}")

    return chunks
