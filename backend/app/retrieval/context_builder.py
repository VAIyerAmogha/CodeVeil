import re
from typing import List, Dict, Any, Tuple, Set
from app.db.mongodb import get_database


# Maximum total chunks fed to the LLM (keeps token budget bounded)
MAX_CONTEXT_CHUNKS = 20

# Identifiers shorter than this are too generic to be meaningful callee names
MIN_IDENTIFIER_LEN = 4

# Common Python/JS/TS keywords and builtins to exclude from callee lookups
_STOP_WORDS = frozenset({
    "self", "cls", "None", "True", "False", "return", "import", "from",
    "class", "def", "async", "await", "yield", "raise", "pass", "break",
    "continue", "with", "as", "try", "except", "finally", "for", "while",
    "if", "elif", "else", "and", "or", "not", "in", "is", "lambda",
    "print", "len", "str", "int", "float", "bool", "list", "dict", "set",
    "tuple", "type", "super", "object", "property", "staticmethod",
    "classmethod", "isinstance", "hasattr", "getattr", "setattr",
    "const", "let", "var", "function", "arrow", "null", "undefined",
    "true", "false", "this", "new", "delete", "typeof", "void", "throw",
    "catch", "finally", "export", "default", "module", "require",
    "append", "extend", "items", "keys", "values", "update", "get",
})


def _extract_callee_names(source_code: str) -> Set[str]:
    """
    Extract only likely function-call identifiers from source code.
    Filters out short tokens, stop words, and ALL_CAPS constants.
    This keeps the MongoDB $in list focused and fast.
    """
    # Match word-like identifiers followed by '(' — these are calls
    call_pattern = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]{3,})\s*\(', source_code)
    names: Set[str] = set()
    for name in call_pattern:
        if name in _STOP_WORDS:
            continue
        if name.upper() == name:  # Skip ALL_CAPS constants like MAX_SIZE
            continue
        names.add(name)
    return names


async def find_callees_for_chunks(
    chunks: List[Dict[str, Any]],
    repo_id: str
) -> List[Dict[str, Any]]:
    """
    Find callee function chunks by extracting likely function call identifiers
    from the source code of input chunks and looking them up in MongoDB.
    Only considers identifiers that appear as actual call sites (followed by '(').
    """
    callee_names: Set[str] = set()
    for chunk in chunks:
        code = chunk.get("source_code", "")
        callee_names.update(_extract_callee_names(code))

    if not callee_names:
        return []

    db = get_database()
    if db is None:
        return []

    callees_cursor = db["chunks"].find({
        "repo_id": repo_id,
        "function_name": {"$in": list(callee_names)},
        "chunk_type": "function"
    }, {
        "chroma_id": 1,
        "source_code": 1,
        "file_path": 1,
        "start_line": 1,
        "end_line": 1,
        "function_name": 1,
        "parent_class": 1,
        "language": 1,
        "chunk_type": 1,
        "summary": 1,
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
    For architectural queries, performs depth-2 callee expansion (capped at MAX_CONTEXT_CHUNKS).
    Returns the final context string and the list of chunks included (for citations).
    """
    final_chunks = list(chunks)

    # Track seen IDs to avoid duplicates (support both chunk_id and chroma_id keys)
    seen_ids: Set[str] = set()
    for c in final_chunks:
        for key in ("chunk_id", "chroma_id"):
            val = c.get(key)
            if val:
                seen_ids.add(val)

    # Architectural queries expand to callee functions up to depth 2
    if query_type.strip().lower() == "architectural":
        current_level_chunks = list(chunks)
        for _depth in range(2):
            if len(final_chunks) >= MAX_CONTEXT_CHUNKS:
                break

            callee_docs = await find_callees_for_chunks(current_level_chunks, repo_id)
            new_callees = []
            for callee in callee_docs:
                cid = callee.get("chroma_id")
                if not cid or cid in seen_ids:
                    continue
                seen_ids.add(cid)

                callee_dict = {
                    "chunk_id": cid,
                    "source_code": callee.get("source_code") or "",
                    "file_path": callee.get("file_path") or "",
                    "start_line": callee.get("start_line") if callee.get("start_line") is not None else -1,
                    "end_line": callee.get("end_line") if callee.get("end_line") is not None else -1,
                    "function_name": callee.get("function_name"),
                    "parent_class": callee.get("parent_class"),
                    "language": callee.get("language"),
                    "chunk_type": callee.get("chunk_type"),
                    "summary": callee.get("summary"),
                }
                new_callees.append(callee_dict)

            if not new_callees:
                break

            slots = MAX_CONTEXT_CHUNKS - len(final_chunks)
            new_callees = new_callees[:slots]
            final_chunks.extend(new_callees)
            current_level_chunks = new_callees

    # Format chunks with enriched headers
    context_parts = []
    for chunk in final_chunks:
        file_path = chunk.get("file_path", "unknown")
        start_line = chunk.get("start_line", 0)
        end_line = chunk.get("end_line", 0)
        source_code = chunk.get("source_code", "")

        if not source_code:
            continue  # Skip empty chunks — they waste token budget

        header_parts = [f"FILE: {file_path} | LINES {start_line}-{end_line}"]
        if chunk.get("chunk_type"):
            header_parts.append(f"type={chunk['chunk_type']}")
        if chunk.get("function_name"):
            header_parts.append(f"function={chunk['function_name']}")
        if chunk.get("parent_class"):
            header_parts.append(f"class={chunk['parent_class']}")
        if chunk.get("language"):
            header_parts.append(f"lang={chunk['language']}")

        header = " | ".join(header_parts)
        context_parts.append(f"{header}\n```\n{source_code}\n```")

    context_string = "\n\n---\n\n".join(context_parts)
    return context_string, final_chunks
