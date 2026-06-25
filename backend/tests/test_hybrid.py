import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.retrieval import hybrid


def test_merge_results():
    bm25_res = [
        {"chunk_id": "id1", "score": 2.5, "rank": 1},
        {"chunk_id": "id2", "score": 1.2, "rank": 2},
    ]
    dense_res = [
        {"chunk_id": "id2", "score": 0.8, "metadata": {}},
        {"chunk_id": "id3", "score": 0.6, "metadata": {}},
    ]

    merged = hybrid.merge_results(bm25_res, dense_res)
    # Check deduplication and merging
    assert len(merged) == 3
    
    # Map by chunk_id for assertions
    merged_map = {m["chunk_id"]: m for m in merged}
    
    assert merged_map["id1"]["bm25_score"] == 2.5
    assert merged_map["id1"]["dense_score"] == 0.0
    
    assert merged_map["id2"]["bm25_score"] == 1.2
    assert merged_map["id2"]["dense_score"] == 0.8
    
    assert merged_map["id3"]["bm25_score"] == 0.0
    assert merged_map["id3"]["dense_score"] == 0.6


def test_rerank():
    chunks = [
        {"chunk_id": "id1", "source_code": "def func1(): pass"},
        {"chunk_id": "id2", "source_code": "def func2(): pass"},
    ]
    
    with patch("app.retrieval.hybrid.cross_encoder.predict", return_value=[0.1, 0.95]):
        reranked = hybrid.rerank("query text", chunks, top_k=2)
        assert len(reranked) == 2
        # Should be sorted descending by rerank score: id2 (0.95) first, then id1 (0.1)
        assert reranked[0]["chunk_id"] == "id2"
        assert reranked[0]["rerank_score"] == 0.95
        assert reranked[1]["chunk_id"] == "id1"
        assert reranked[1]["rerank_score"] == 0.1


@pytest.mark.asyncio
async def test_hybrid_retrieve():
    mock_bm25 = [
        {"chunk_id": "id1", "score": 2.5, "rank": 1},
        {"chunk_id": "id2", "score": 1.2, "rank": 2},
    ]
    mock_dense = [
        {"chunk_id": "id2", "score": 0.8, "metadata": {}},
        {"chunk_id": "id3", "score": 0.6, "metadata": {}},
    ]

    # Mock retrievers
    async def mock_ret_bm25(*args, **kwargs):
        return mock_bm25
    async def mock_ret_dense(*args, **kwargs):
        return mock_dense

    # Mock ChromaDB
    mock_collection = MagicMock()
    mock_collection.get.return_value = {
        "ids": ["id1", "id2", "id3"],
        "documents": ["code1", "code2", "code3"]
    }
    mock_chroma_client = MagicMock()
    mock_chroma_client.get_collection.return_value = mock_collection

    # Mock MongoDB
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.__aiter__.return_value = [
        {"chroma_id": "id1", "source_code": "code1", "file_path": "a.py", "start_line": 1, "end_line": 10},
        {"chroma_id": "id2", "source_code": "code2", "file_path": "b.py", "start_line": 5, "end_line": 15},
        {"chroma_id": "id3", "source_code": "code3", "file_path": "c.py", "start_line": 8, "end_line": 20},
    ]
    mock_db["chunks"].find.return_value = mock_cursor

    with patch("app.retrieval.hybrid.retrieve_bm25", side_effect=mock_ret_bm25), \
         patch("app.retrieval.hybrid.retrieve_dense", side_effect=mock_ret_dense), \
         patch("app.retrieval.hybrid.get_chroma_client", return_value=mock_chroma_client), \
         patch("app.retrieval.hybrid.get_database", return_value=mock_db), \
         patch("app.retrieval.hybrid.cross_encoder.predict", return_value=[0.9, 0.4, 0.7]):
        
        results = await hybrid.hybrid_retrieve("repo123", "some query", top_k=2)

        # Should return top 2
        assert len(results) == 2
        
        # Checked ordered descending by rerank score:
        # id1 had 0.9, id3 had 0.7, id2 had 0.4.
        # Top 2 should be id1 and id3.
        assert results[0]["chunk_id"] == "id1"
        assert results[0]["rerank_score"] == 0.9
        assert results[0]["file_path"] == "a.py"

        assert results[1]["chunk_id"] == "id3"
        assert results[1]["rerank_score"] == 0.7
        assert results[1]["file_path"] == "c.py"
