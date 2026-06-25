import pytest
from unittest.mock import MagicMock, patch
from app.retrieval import classifier


def test_classify_query_lookup():
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "   lookup\n"
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("app.retrieval.classifier.client_cycle", iter([mock_client])):
        result = classifier.classify_query("where is X defined?")
        assert result == "lookup"
        mock_client.chat.completions.create.assert_called_once()


def test_classify_query_explanation():
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "Explanation"
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("app.retrieval.classifier.client_cycle", iter([mock_client])):
        result = classifier.classify_query("how does function Y work?")
        assert result == "explanation"
        mock_client.chat.completions.create.assert_called_once()


def test_classify_query_architectural():
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "architectural"
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("app.retrieval.classifier.client_cycle", iter([mock_client])):
        result = classifier.classify_query("how do modules connect?")
        assert result == "architectural"
        mock_client.chat.completions.create.assert_called_once()


def test_classify_query_unexpected_response():
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "something_else"
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("app.retrieval.classifier.client_cycle", iter([mock_client])):
        result = classifier.classify_query("what calls X?")
        assert result == "explanation"  # Default fallback on unexpected response
        mock_client.chat.completions.create.assert_called_once()


def test_classify_query_groq_error():
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("Groq API error")

    with patch("app.retrieval.classifier.client_cycle", iter([mock_client])):
        result = classifier.classify_query("walk me through Y")
        assert result == "explanation"  # Default fallback on Groq error


def test_classify_query_no_clients():
    with patch("app.retrieval.classifier.client_cycle", None):
        result = classifier.classify_query("what does constant Y equal?")
        assert result == "explanation"  # Default fallback when no client is configured
