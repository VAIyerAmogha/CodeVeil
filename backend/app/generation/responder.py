import re
import logging
from typing import List, Dict, Any, Optional

from groq import Groq
from app.config import settings

logger = logging.getLogger(__name__)

def _get_groq_api_key() -> str:
    if settings.groq_api_key:
        return settings.groq_api_key
    if settings.groq_api_keys:
        return settings.groq_api_keys.split(",")[0].strip()
    return ""

# Groq client singleton at module level
try:
    api_key = _get_groq_api_key()
    if not api_key:
        raise ValueError("No Groq API key found in settings.")
    groq_client = Groq(api_key=api_key)
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    groq_client = None

MODEL_NAME = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are CodeVeil, an expert code analysis assistant.
You answer questions about codebases using only the provided code context.

CITATION RULES — non-negotiable:
- Every factual claim must be followed by a citation in this exact format: [file/path.py:42]
- If you cannot cite something from the provided context, do not state it
- Do not make assumptions about code you have not seen

ANSWER FORMAT:
- Be precise and technical
- Reference specific function names, class names, and line numbers
- For architectural queries, describe the flow step by step
- Keep answers focused — do not pad with unnecessary explanation"""


def parse_citations(answer: str, chunks: list[dict]) -> list[dict]:
    """
    Extract all [file/path.py:N] patterns from answer text.
    Match each to a chunk_id where possible.
    Return list of {file, line, chunk_id}
    """
    citations = []
    # Pattern to match [file_path:line_number]
    pattern = r"\[(.*?(?:\.\w+)?):(\d+)\]"
    
    matches = re.findall(pattern, answer)
    for file_path, line_str in matches:
        try:
            line_num = int(line_str)
        except ValueError:
            continue
            
        matched_chunk_id = None
        matched_chunk_file = file_path.lstrip("/")
        
        for chunk in chunks:
            # Check if file path matches and line is within chunk boundaries
            chunk_file = chunk.get("file_path", "")
            chunk_start = chunk.get("start_line", -1)
            chunk_end = chunk.get("end_line", -1)
            
            # Allow exact match, or if the LLM used just the filename or a suffix
            if (file_path == chunk_file or chunk_file.endswith("/" + file_path) or file_path.endswith(chunk_file)) and chunk_start <= line_num <= chunk_end:
                matched_chunk_id = chunk.get("chunk_id")
                matched_chunk_file = chunk_file
                # Fallback to other possible id keys if chunk_id isn't present
                if not matched_chunk_id and "_id" in chunk:
                     matched_chunk_id = str(chunk["_id"])
                elif not matched_chunk_id and "chroma_id" in chunk:
                     matched_chunk_id = chunk["chroma_id"]
                break
                
        citations.append({
            "file": matched_chunk_file,
            "line": line_num,
            "chunk_id": matched_chunk_id
        })
        
    return citations


def generate_answer(
    question: str,
    context: str,
    query_type: str,
    chunks: list[dict]
) -> dict:
    """
    Builds user message, calls Groq, parses response.
    Never raises exceptions - returns fallback dict on error.
    """
    fallback = {
        "answer": "Unable to generate answer.",
        "citations": [],
        "chunks_used": 0
    }
    
    if not groq_client:
        return fallback

    user_message = f"Context:\n{context}\n\nQuestion: {question}\n\nQuery type: {query_type}"
    
    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            model=MODEL_NAME,
            temperature=0.1,
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
    except Exception as e:
        logger.error(f"Groq API error in generate_answer: {e}")
        fallback["answer"] = f"Unable to generate answer. Error: {str(e)}"
        return fallback

def generate_repo_summary(repo_name: str, description: str, languages: dict) -> str:
    if not groq_client:
        return "Summary not yet generated."
        
    prompt = f"Write a concise, 2-3 sentence technical summary of the repository '{repo_name}'.\n"
    if description:
        prompt += f"Description: {description}\n"
    if languages:
        prompt += f"Languages: {', '.join(languages.keys())}\n"
        
    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a concise technical writer. Summarize the codebase objectively."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generating repo summary: {e}")
        return "Summary not yet generated."
