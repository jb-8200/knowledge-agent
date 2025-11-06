"""Tests for LangChain retriever tool."""

import pytest
import json
from app.tools.retriever import retrieval_tool, retrieve_passages, RetrievalInput
from langchain.tools import BaseTool
from pydantic import ValidationError


def test_retrieval_tool_is_structured_tool():
    """Test that retrieval_tool is a LangChain tool."""
    assert isinstance(retrieval_tool, BaseTool)
    assert retrieval_tool.name == "search_knowledge_base"
    assert len(retrieval_tool.description) > 0


def test_retrieval_tool_has_input_schema():
    """Test that tool has Pydantic input schema."""
    assert retrieval_tool.args_schema is not None
    assert retrieval_tool.args_schema == RetrievalInput


def test_retrieval_input_schema_validation():
    """Test that RetrievalInput validates input correctly."""
    # Valid input
    valid_input = RetrievalInput(query="test query", top_k=5)
    assert valid_input.query == "test query"
    assert valid_input.top_k == 5

    # Default top_k
    default_input = RetrievalInput(query="another query")
    assert default_input.top_k == 5

    # Invalid: empty query
    with pytest.raises(ValidationError):
        RetrievalInput(query="", top_k=5)

    # Invalid: top_k out of range
    with pytest.raises(ValidationError):
        RetrievalInput(query="test", top_k=0)


def test_retrieve_passages_function_signature():
    """Test that retrieve_passages has correct signature."""
    import inspect
    sig = inspect.signature(retrieve_passages)

    assert 'query' in sig.parameters
    assert 'top_k' in sig.parameters
    assert sig.parameters['top_k'].default == 5


def test_retrieve_passages_returns_dict(monkeypatch):
    """Test that retrieve_passages returns JSON-serializable dict."""
    # Mock VectorSearchService
    from app.services.vector_search import SearchResult

    mock_results = [
        SearchResult(
            text="Machine learning is a field of AI.",
            metadata={
                "doc_id": "doc1",
                "filename": "test.pdf",
                "chunk_index": 0,
                "page_number": 1,
                "source": "upload",
                "timestamp": "2024-01-01T00:00:00Z"
            },
            score=0.95
        )
    ]

    def mock_search(self, query, top_k):
        return mock_results

    monkeypatch.setattr(
        "app.services.vector_search.VectorSearchService.search_vectors",
        mock_search
    )

    result = retrieve_passages(query="AI", top_k=3)

    assert isinstance(result, dict)
    assert "passages" in result
    assert "query" in result
    assert "count" in result
    assert result["query"] == "AI"
    assert result["count"] == 1
    assert len(result["passages"]) == 1


def test_retrieve_passages_output_format(monkeypatch):
    """Test that passages have correct structure."""
    from app.services.vector_search import SearchResult

    mock_results = [
        SearchResult(
            text="Test passage",
            metadata={
                "doc_id": "doc1",
                "filename": "test.pdf",
                "chunk_index": 0,
                "source": "upload"
            },
            score=0.85
        )
    ]

    def mock_search(self, query, top_k):
        return mock_results

    monkeypatch.setattr(
        "app.services.vector_search.VectorSearchService.search_vectors",
        mock_search
    )

    result = retrieve_passages("test", top_k=1)
    passage = result["passages"][0]

    assert "text" in passage
    assert "metadata" in passage
    assert "score" in passage
    assert passage["text"] == "Test passage"
    assert passage["score"] == 0.85


def test_retrieval_tool_direct_invocation(monkeypatch):
    """Test invoking tool directly with tool.func()."""
    from app.services.vector_search import SearchResult

    mock_results = [
        SearchResult(
            text="LangChain is a framework.",
            metadata={"doc_id": "doc2", "filename": "docs.pdf", "chunk_index": 5, "source": "web"},
            score=0.92
        )
    ]

    def mock_search(self, query, top_k):
        return mock_results

    monkeypatch.setattr(
        "app.services.vector_search.VectorSearchService.search_vectors",
        mock_search
    )

    # Invoke tool
    result = retrieval_tool.func(query="LangChain", top_k=1)

    assert result["count"] == 1
    assert result["passages"][0]["text"] == "LangChain is a framework."


def test_retrieval_tool_invoke_method(monkeypatch):
    """Test invoking tool with .invoke() method."""
    from app.services.vector_search import SearchResult

    mock_results = [
        SearchResult(
            text="Testing invoke method.",
            metadata={"doc_id": "doc3", "filename": "test.md", "chunk_index": 0, "source": "upload"},
            score=0.88
        )
    ]

    def mock_search(self, query, top_k):
        return mock_results

    monkeypatch.setattr(
        "app.services.vector_search.VectorSearchService.search_vectors",
        mock_search
    )

    # Use invoke method
    result = retrieval_tool.invoke({"query": "test invoke", "top_k": 1})

    assert isinstance(result, dict)
    assert result["count"] == 1


def test_retrieval_tool_with_langchain_chain(monkeypatch):
    """Test that tool works in a simple LangChain chain."""
    from app.services.vector_search import SearchResult

    mock_results = [
        SearchResult(
            text="Chain integration test.",
            metadata={"doc_id": "doc4", "filename": "chain.pdf", "chunk_index": 2, "source": "upload"},
            score=0.90
        )
    ]

    def mock_search(self, query, top_k):
        return mock_results

    monkeypatch.setattr(
        "app.services.vector_search.VectorSearchService.search_vectors",
        mock_search
    )

    # Test tool in chain-like context
    tool_input = {"query": "chain test", "top_k": 1}
    result = retrieval_tool.invoke(tool_input)

    assert result is not None
    assert "passages" in result


def test_empty_query_error_handling():
    """Test that empty queries are handled gracefully."""
    with pytest.raises(ValidationError, match="query"):
        RetrievalInput(query="", top_k=5)


def test_retrieve_passages_handles_no_results(monkeypatch):
    """Test that function handles empty search results."""
    def mock_search(self, query, top_k):
        return []

    monkeypatch.setattr(
        "app.services.vector_search.VectorSearchService.search_vectors",
        mock_search
    )

    result = retrieve_passages("nonexistent query", top_k=5)

    assert result["count"] == 0
    assert result["passages"] == []
    assert result["query"] == "nonexistent query"


def test_tool_output_is_json_serializable(monkeypatch):
    """Test that tool output can be serialized to JSON."""
    from app.services.vector_search import SearchResult

    mock_results = [
        SearchResult(
            text="JSON serialization test.",
            metadata={"doc_id": "doc5", "filename": "test.pdf", "chunk_index": 1, "source": "upload"},
            score=0.87
        )
    ]

    def mock_search(self, query, top_k):
        return mock_results

    monkeypatch.setattr(
        "app.services.vector_search.VectorSearchService.search_vectors",
        mock_search
    )

    result = retrieval_tool.invoke({"query": "JSON test", "top_k": 1})

    # Should not raise exception
    json_str = json.dumps(result)
    assert isinstance(json_str, str)

    # Parse back
    parsed = json.loads(json_str)
    assert parsed["count"] == 1
