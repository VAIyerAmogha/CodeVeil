import re
from typing import List, Dict, Any, Tuple, Set
from app.db.mongodb import get_database


async def find_callees_for_chunks(
    chunks: List[Dict[str, Any]], 
    repo_id: str
) -> List[Dict[str, Any]]:
    """
    Find callee function chunks by extracting word tokens from the source_code
    of the input chunks and looking them up in MongoDB.
    """
    words: Set[str] = set()
    for chunk in chunks:
        code = chunk.get("source_code", "")
        # Extract word-like identifiers to catch function calls
        found = re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b", code)
        words.update(found)

    if not words:
        return []

    db = get_database()
    if db is None:
        return []

    # Query MongoDB for chunks with matching function names in this repo
    # Only pull function chunks
    callees_cursor = db["chunks"].find({
        "repo_id": repo_id,
        "function_name": {"$in": list(words)},
        "chunk_type": "function"
    })

    callee_chunks = []
    async for doc in callees_cursor:
        callee_chunks.append(doc)

    return callee_chunks


async def build_context(
    chunks: List[Dict[str, Any]], 
    query_type: str, 
    repo_id: str
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Builds the context string for the LLM.
    For architectural queries, performs depth-2 callee expansion.
    Returns the final context string and the list of chunks included (for citations).
    """
    final_chunks = list(chunks)
    seen_chroma_ids = {c.get("chunk_id") for c in final_chunks if c.get("chunk_id")}
    # Also support documents loaded from mongo where key is 'chroma_id' or '_id'
    for c in final_chunks:
        if "chroma_id" in c and c["chroma_id"]:
            seen_chroma_ids.add(c["chroma_id"])

    # Architectural queries expand to callee functions up to depth 2
    if query_type.strip().lower() == "architectural":
        current_level_chunks = list(chunks)
        for depth in range(2):
            callee_docs = await find_callees_for_chunks(current_level_chunks, repo_id)
            new_callees = []
            for callee in callee_docs:
                cid = callee.get("chroma_id")
                # Deduplicate
                if cid and cid not in seen_chroma_ids:
                    seen_chroma_ids.add(cid)
                    callee_dict = {
                        "chunk_id": cid,
                        "source_code": callee.get("source_code", ""),
                        "file_path": callee.get("file_path"),
                        "start_line": callee.get("start_line"),
                        "end_line": callee.get("end_line"),
                        "function_name": callee.get("function_name"),
                        "parent_class": callee.get("parent_class"),
                        "language": callee.get("language"),
                        "chunk_type": callee.get("chunk_type"),
                        "summary": callee.get("summary"),
                    }
                    new_callees.append(callee_dict)

            if not new_callees:
                break

            # Limit total chunks to prevent hitting LLM context/rate limits
            available_slots = 25 - len(final_chunks)
            if available_slots <= 0:
                break
                
            new_callees = new_callees[:available_slots]
            final_chunks.extend(new_callees)
            current_level_chunks = new_callees

    # Format chunks with headers
    context_parts = []
    for chunk in final_chunks:
        file_path = chunk.get("file_path", "unknown")
        start_line = chunk.get("start_line", 0)
        end_line = chunk.get("end_line", 0)
        source_code = chunk.get("source_code", "")

        header = f"# {file_path}:{start_line}-{end_line}"
        context_parts.append(f"{header}\n{source_code}")

    context_string = "\n\n".join(context_parts)
    return context_string, final_chunks
