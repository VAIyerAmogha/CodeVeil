import pytest
from unittest.mock import MagicMock, patch
from app.retrieval import context_builder


@pytest.mark.asyncio
async def test_build_context_explanation():
    chunks = [
        {"chunk_id": "id1", "source_code": "def hello(): print('hello')", "file_path": "hello.py", "start_line": 1, "end_line": 3},
        {"chunk_id": "id2", "source_code": "class World: pass", "file_path": "world.py", "start_line": 5, "end_line": 6},
    ]

    context_str, final_chunks = await context_builder.build_context(chunks, "explanation", "repo123")
    
    assert len(final_chunks) == 2
    assert "hello.py:1-3" in context_str
    assert "world.py:5-6" in context_str
    assert "def hello(): print('hello')" in context_str
    assert "class World: pass" in context_str
    assert context_str.startswith("# hello.py:1-3")


@pytest.mark.asyncio
async def test_build_context_architectural_callee_expansion():
    # Initial chunk refers to 'process_payment'
    chunks = [
        {
            "chunk_id": "id1", 
            "source_code": "def checkout():\n    process_payment()", 
            "file_path": "checkout.py", 
            "start_line": 1, 
            "end_line": 5,
            "function_name": "checkout"
        }
    ]

    # Level 1 callee refers to 'charge_card'
    level_1_callee = {
        "chroma_id": "callee_id_1",
        "source_code": "def process_payment():\n    charge_card()",
        "file_path": "payment.py",
        "start_line": 10,
        "end_line": 15,
        "function_name": "process_payment",
        "chunk_type": "function"
    }

    # Level 2 callee
    level_2_callee = {
        "chroma_id": "callee_id_2",
        "source_code": "def charge_card():\n    print('charged')",
        "file_path": "gateway.py",
        "start_line": 20,
        "end_line": 22,
        "function_name": "charge_card",
        "chunk_type": "function"
    }

    mock_db = MagicMock()
    
    # Simple mock for cursor find
    # First call find_callees_for_chunks extracts 'checkout', 'process_payment' -> mock returns process_payment
    # Second call extracts 'charge_card' -> mock returns charge_card
    # Third call extracts 'charged' -> mock returns empty list
    find_calls = []

    def mock_find(query, *args, **kwargs):
        find_calls.append(query)
        mock_cursor = MagicMock()
        
        # Determine what to return based on $in query
        func_names = query.get("function_name", {}).get("$in", [])
        
        results = []
        if "process_payment" in func_names and "callee_id_1" not in [c.get("chroma_id") for c in results]:
            results.append(level_1_callee)
        if "charge_card" in func_names and "callee_id_2" not in [c.get("chroma_id") for c in results]:
            results.append(level_2_callee)
            
        mock_cursor.__aiter__.return_value = results
        return mock_cursor

    mock_db["chunks"].find.side_effect = mock_find

    with patch("app.retrieval.context_builder.get_database", return_value=mock_db):
        context_str, final_chunks = await context_builder.build_context(chunks, "architectural", "repo123")

        # Initial chunk + level 1 callee + level 2 callee = 3 chunks
        assert len(final_chunks) == 3
        
        # Verify ids
        chunk_ids = [c.get("chunk_id") for c in final_chunks]
        assert "id1" in chunk_ids
        assert "callee_id_1" in chunk_ids
        assert "callee_id_2" in chunk_ids

        # Verify context content and headers
        assert "checkout.py:1-5" in context_str
        assert "payment.py:10-15" in context_str
        assert "gateway.py:20-22" in context_str
        assert "charged" in context_str
