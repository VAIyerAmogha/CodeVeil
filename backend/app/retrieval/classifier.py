import logging
import asyncio
from itertools import cycle
from groq import AsyncGroq
from app.config import settings

logger = logging.getLogger(__name__)

# ── Async Groq client pool ───────────────────────────────────────────────────
keys = []
if settings.groq_api_keys:
    keys = [k.strip() for k in settings.groq_api_keys.split(",") if k.strip()]
elif settings.groq_api_key:
    keys = [settings.groq_api_key.strip()]

# Use AsyncGroq so we never block the event loop during classification
groq_clients = [AsyncGroq(api_key=k) for k in keys]
client_cycle = cycle(groq_clients) if groq_clients else None

MODEL_NAME = "llama-3.1-8b-instant"


async def classify_and_expand(question: str) -> tuple[str, str]:
    """
    Returns (query_type, expanded_query) in a single async Groq call.

    query_type:     'lookup' | 'explanation' | 'architectural'
    expanded_query: a technically enriched rewrite for better retrieval recall.
                    Falls back to the original question on any error.

    Uses AsyncGroq so the event loop is never blocked.
    """
    if not client_cycle:
        logger.error("No Groq API keys available for classification.")
        return "explanation", question

    system_prompt = "You are a code search assistant. Respond in exactly 2 lines, nothing else."
    user_prompt = f"""Given this question about a codebase:
"{question}"

Line 1: Classify it as exactly one of: lookup | explanation | architectural
  - lookup: asking for a specific value, definition, or location
  - explanation: asking how something works or what something does
  - architectural: asking about structure, flow, dependencies, or call chains

Line 2: Rewrite the question using specific technical/code terms to improve search recall.
  Same meaning, more keywords (function names, module names, patterns), max 20 words.

Respond with exactly 2 lines, no labels, no punctuation other than spaces."""

    try:
        current_client = next(client_cycle)
        response = await current_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=MODEL_NAME,
            temperature=0.0,
            max_tokens=60,
        )

        content = response.choices[0].message.content.strip()
        lines = [l.strip() for l in content.splitlines() if l.strip()]

        query_type = lines[0].lower() if lines else "explanation"
        expanded = lines[1] if len(lines) > 1 else question

        valid_categories = {"lookup", "explanation", "architectural"}
        if query_type not in valid_categories:
            logger.warning(
                f"Unexpected classifier response: '{query_type}'. Defaulting to 'explanation'."
            )
            query_type = "explanation"

        if not expanded:
            expanded = question

        return query_type, expanded

    except Exception as e:
        logger.error(f"Error in classify_and_expand: {e}")
        return "explanation", question


def classify_query(question: str) -> str:
    """
    Backward-compat shim. Returns only the query_type synchronously by running
    the async classifier in the current event loop.
    Prefer calling classify_and_expand directly in async contexts.
    """
    try:
        loop = asyncio.get_event_loop()
        query_type, _ = loop.run_until_complete(classify_and_expand(question))
        return query_type
    except Exception:
        return "explanation"
