import os
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from rank_bm25 import BM25Okapi
from app.retrieval import bm25_retriever, dense_retriever


@pytest.mark.asyncio
async def test_load_bm25_not_found():
    with patch("os.path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            await bm25_retriever.load_bm25("nonexistent_repo")


@pytest.mark.asyncio
async def test_load_bm25_success():
    mock_bm25 = MagicMock(spec=BM25Okapi)
    mock_bm25.corpus_size = 2

    mock_db = MagicMock()
    mock_cursor = MagicMock()
    # Mocking async for doc in chunks_cursor
    mock_cursor.__aiter__.return_value = [{"chroma_id": "id1"}, {"chroma_id": "id2"}]
    mock_db["chunks"].find.return_value.sort.return_value = mock_cursor

    # Clear cache before test
    bm25_retriever._bm25_cache.clear()

    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", MagicMock()), \
         patch("pickle.load", return_value=mock_bm25), \
         patch("app.retrieval.bm25_retriever.get_database", return_value=mock_db):
        
        result = await bm25_retriever.load_bm25("repo123")
        assert result == mock_bm25
        assert "repo123" in bm25_retriever._bm25_cache
        assert bm25_retriever._bm25_cache["repo123"] == (mock_bm25, ["id1", "id2"])


@pytest.mark.asyncio
async def test_retrieve_bm25():
    mock_bm25 = MagicMock(spec=BM25Okapi)
    mock_bm25.corpus_size = 2
    mock_bm25.get_scores.return_value = [1.5, 3.2]

    # Pre-populate cache
    bm25_retriever._bm25_cache["repo123"] = (mock_bm25, ["id1", "id2"])

    # We patch load_bm25 to just return the cached bm25
    with patch("app.retrieval.bm25_retriever.load_bm25", return_value=mock_bm25):
        results = await bm25_retriever.retrieve_bm25("repo123", "hello world", top_k=2)
        
        assert len(results) == 2
        # Check sorting by score: "id2" has 3.2, "id1" has 1.5
        assert results[0]["chunk_id"] == "id2"
        assert results[0]["score"] == 3.2
        assert results[0]["rank"] == 1
        assert results[1]["chunk_id"] == "id1"
        assert results[1]["score"] == 1.5
        assert results[1]["rank"] == 2


@pytest.mark.asyncio
async def test_retrieve_dense():
    # Mock ChromaDB Collection
    mock_collection = MagicMock()
    mock_collection.query.return_value = {
        "ids": [["id1", "id2"]],
        "distances": [[0.2, 0.5]]
    }
    
    mock_chroma_client = MagicMock()
    mock_chroma_client.get_collection.return_value = mock_collection

    # Mock MongoDB
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.__aiter__.return_value = [
        {"chroma_id": "id1", "file_path": "a.py", "summary": "sum1"},
        {"chroma_id": "id2", "file_path": "b.py", "summary": "sum2"},
    ]
    mock_db["chunks"].find.return_value = mock_cursor

    # Mock SentenceTransformer encode
    with patch("app.retrieval.dense_retriever.get_chroma_client", return_value=mock_chroma_client), \
         patch("app.retrieval.dense_retriever.get_database", return_value=mock_db), \
         patch("app.retrieval.dense_retriever.embedding_model.encode") as mock_encode:
        
        mock_encode.return_value.tolist.return_value = [0.1, 0.2]

        results = await dense_retriever.retrieve_dense("repo123", "some query", top_k=2)

        assert len(results) == 2
        
        # Verify call to chroma collection
        mock_collection.query.assert_called_once()
        
        # id1 cosine similarity = 1.0 - 0.2 = 0.8
        assert results[0]["chunk_id"] == "id1"
        assert results[0]["score"] == pytest.approx(0.8)
        assert results[0]["metadata"]["file_path"] == "a.py"
        
        # id2 cosine similarity = 1.0 - 0.5 = 0.5
        assert results[1]["chunk_id"] == "id2"
        assert results[1]["score"] == pytest.approx(0.5)
        assert results[1]["metadata"]["file_path"] == "b.py"
