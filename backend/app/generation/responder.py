import re
import logging
import asyncio
from typing import List, Dict, Any, Optional

from groq import AsyncGroq
from app.config import settings

logger = logging.getLogger(__name__)


def _get_groq_api_key() -> str:
    if settings.groq_api_key:
        return settings.groq_api_key
    if settings.groq_api_keys:
        return settings.groq_api_keys.split(",")[0].strip()
    return ""


# ── Async Groq client (never blocks event loop) ──────────────────────────────
try:
    api_key = _get_groq_api_key()
    if not api_key:
        raise ValueError("No Groq API key found in settings.")
    groq_client: Optional[AsyncGroq] = AsyncGroq(api_key=api_key)
except Exception as e:
    logger.error(f"Failed to initialize AsyncGroq client: {e}")
    groq_client = None

MODEL_NAME = settings.groq_model_generation or "openai/gpt-oss-120b"
ANSWER_TIMEOUT_SECONDS = 45  # Overall wall-clock budget for LLM generation

SYSTEM_PROMPT = """You are CodeVeil, an expert code analysis assistant.
You answer questions about codebases using only the provided code context.

CITATION RULES — non-negotiable:
- Every factual claim MUST be followed by a citation in this exact format: [file/path.py:42]
- Use a SINGLE specific line number — the most representative line inside the block
- NEVER cite a line range like [file.py:20-50] — always one integer, e.g. [file.py:35]
- If you cannot cite something from the provided context, do not state it
- Do not make assumptions about code you have not seen

ANSWER FORMAT:
- Be precise and technical
- Reference specific function names, class names, and line numbers
- For architectural queries, describe the flow step by step
- Keep answers focused — do not pad with unnecessary explanation"""

QUERY_TYPE_ADDENDUM = {
    "lookup": (
        "\n\nThis is a LOOKUP query. The user wants a precise location, definition, or value. "
        "Answer in 1-3 sentences with a single exact citation. Do not elaborate beyond what was asked."
    ),
    "explanation": (
        "\n\nThis is an EXPLANATION query. The user wants to understand how something works. "
        "Walk through the logic step by step. Cite every function or class you reference with [file:line]."
    ),
    "architectural": (
        "\n\nThis is an ARCHITECTURAL query. The user wants to understand system structure or data flow. "
        "Describe the full call chain or pipeline from entry point to output using numbered steps. "
        "Cite every hop with [file:line]. Connect the dots between files explicitly."
    ),
}

CONFIDENCE_ADDENDUM = {
    "high": "",
    "medium": (
        "\n\nCONTEXT COVERAGE: MODERATE — partial code was retrieved. "
        "Where you are inferring beyond what the code explicitly shows, prefix with "
        "'Based on the available context...' or 'The retrieved code suggests...'. "
        "Do not fabricate function signatures or logic you have not seen."
    ),
    "low": (
        "\n\nCONTEXT COVERAGE: LOW — only limited code was found for this query. "
        "Begin your answer by noting that only partial context was retrieved. "
        "Be explicit about what you could NOT find. Do not guess at implementation details. "
        "Suggest the user try a more specific query using exact function or class names."
    ),
    "none": (
        "\n\nCONTEXT COVERAGE: NONE — no relevant code was found for this query. "
        "You MUST tell the user directly that no relevant code was retrieved. "
        "Do not attempt to answer the question. Suggest re-phrasing with specific identifiers."
    ),
}


def parse_citations(answer: str, chunks: list[dict]) -> list[dict]:
    """
    Extract all [file/path.py:N] or [file/path.py:N-M] patterns from answer text.
    Match each to a chunk_id where possible.
    Returns list of {file, line, chunk_id}. Never raises.
    """
    citations = []
    pattern = r"\[(.*?(?:\.\w+)?):(\\d+)(?:-\d+)?\]"
    # Robust pattern that handles both [file.py:42] and range fallback [file.py:20-50]
    pattern = r"\[([^\[\]]+?):(\d+)(?:-\d+)?\]"

    matches = re.findall(pattern, answer)
    seen: set = set()
    for file_path, line_str in matches:
        try:
            line_num = int(line_str)
        except (ValueError, TypeError):
            continue

        if not file_path:
            continue
        key = (file_path, line_num)
        if key in seen:
            continue
        seen.add(key)

        matched_chunk_id = None
        matched_chunk_file = file_path.lstrip("/")

        for chunk in chunks:
            try:
                chunk_file = chunk.get("file_path") or ""
                chunk_start = chunk.get("start_line")
                chunk_end = chunk.get("end_line")

                if chunk_start is None or chunk_end is None:
                    continue

                chunk_start = int(chunk_start)
                chunk_end = int(chunk_end)

                path_match = (
                    file_path == chunk_file
                    or (chunk_file and chunk_file.endswith("/" + file_path))
                    or (chunk_file and file_path.endswith(chunk_file))
                    or (chunk_file and file_path.endswith(chunk_file.lstrip("/")))
                )
                line_match = chunk_start <= line_num <= chunk_end

                if path_match and line_match:
                    matched_chunk_id = chunk.get("chunk_id")
                    matched_chunk_file = chunk_file or matched_chunk_file
                    if not matched_chunk_id and "_id" in chunk:
                        matched_chunk_id = str(chunk["_id"])
                    elif not matched_chunk_id and "chroma_id" in chunk:
                        matched_chunk_id = chunk["chroma_id"]
                    break
            except Exception:
                continue

        citations.append({
            "file": matched_chunk_file,
            "line": line_num,
            "chunk_id": matched_chunk_id
        })

    return citations


async def generate_answer(
    question: str,
    context: str,
    query_type: str,
    chunks: list[dict],
    confidence_level: str = "high"
) -> dict:
    """
    Async LLM call via AsyncGroq. Never blocks the event loop.
    Has a hard wall-clock timeout of ANSWER_TIMEOUT_SECONDS.
    Returns a fallback dict on any error — never raises.
    """
    fallback = {
        "answer": "I wasn't able to generate an answer for this query. Please try rephrasing or use a more specific function or file name.",
        "citations": [],
        "chunks_used": 0
    }

    if not groq_client:
        fallback["answer"] = "The AI service is temporarily unavailable. Please try again in a moment."
        return fallback

    # Compose system prompt: base + query-type hint + confidence awareness
    addendum = QUERY_TYPE_ADDENDUM.get(query_type, "")
    confidence_note = CONFIDENCE_ADDENDUM.get(confidence_level, "")
    system_with_hint = SYSTEM_PROMPT + addendum + confidence_note

    # Cap context at ~12k chars to avoid hitting token limits on large repos
    if len(context) > 12000:
        context = context[:12000] + "\n\n[...context truncated for length...]"

    user_message = f"Context:\n{context}\n\nQuestion: {question}"

    try:
        response = await asyncio.wait_for(
            groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_with_hint},
                    {"role": "user", "content": user_message}
                ],
                model=settings.groq_model_generation or MODEL_NAME,
                temperature=0.1,
            ),
            timeout=ANSWER_TIMEOUT_SECONDS
        )

        answer_text = response.choices[0].message.content
        if not answer_text:
            return fallback

        citations = parse_citations(answer_text, chunks)

        return {
            "answer": answer_text,
            "citations": citations,
            "chunks_used": len(chunks)
        }

    except asyncio.TimeoutError:
        logger.error(f"Groq answer generation timed out after {ANSWER_TIMEOUT_SECONDS}s")
        fallback["answer"] = (
            "The answer generation timed out. The context may be too large — "
            "try a more specific query."
        )
        return fallback
    except Exception as e:
        logger.error(f"Groq API error in generate_answer: {e}", exc_info=True)
        fallback["answer"] = (
            "Something went wrong while generating the answer. "
            "Please try again or rephrase your question."
        )
        return fallback


async def generate_repo_summary(repo_name: str, description: str, languages: dict) -> str:
    if not groq_client:
        return "Summary not yet generated."

    prompt = f"Write a concise, 2-3 sentence technical and functional summary of the repository '{repo_name}'.\n"
    if description:
        prompt += f"Description: {description}\n"
    if languages:
        prompt += f"Languages: {', '.join(languages.keys())}\n"

    try:
        response = await asyncio.wait_for(
            groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a concise technical writer. Summarize the codebase objectively."},
                    {"role": "user", "content": prompt}
                ],
                model=settings.groq_model_fast or "openai/gpt-oss-20b",
                temperature=0.3,
                max_tokens=150
            ),
            timeout=20
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generating repo summary: {e}")
        return "Summary not yet generated."
