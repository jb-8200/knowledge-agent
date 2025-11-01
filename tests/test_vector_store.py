"""Test Qdrant vector store integration."""

import pytest
from ingestion.chunker import Chunk


@pytest.fixture
def test_collection_name():
    """Use a test collection to avoid polluting production data."""
    return "test_kb_passages"


@pytest.fixture
def vector_store(test_collection_name):
    """Create a vector store instance for testing."""
    from ingestion.vector_store import VectorStore

    store = VectorStore(collection_name=test_collection_name)
    yield store
    # Cleanup: delete test collection
    try:
        store.delete_collection()
    except Exception:
        pass  # Collection may not exist if test failed early


def test_vector_store_creates_collection(vector_store):
    """Test that vector store creates collection on initialization."""
    collections = vector_store.client.get_collections().collections
    collection_names = [c.name for c in collections]

    assert vector_store.collection_name in collection_names


def test_upsert_single_vector(vector_store):
    """Test upserting a single vector with metadata."""
    chunks = [
        Chunk(
            text="Test document content",
            metadata={"doc_id": "test-1", "chunk_index": 0, "filename": "test.txt"}
        )
    ]

    result = vector_store.upsert_chunks(chunks)

    # Check result is successful
    assert result is not None


def test_upsert_multiple_vectors(vector_store):
    """Test batch upserting multiple vectors."""
    chunks = [
        Chunk(
            text=f"Document {i} content about topic {i}",
            metadata={"doc_id": f"doc-{i}", "chunk_index": 0}
        )
        for i in range(5)
    ]

    result = vector_store.upsert_chunks(chunks)
    assert result is not None


def test_search_returns_relevant_chunks(vector_store):
    """Test that similarity search returns relevant results."""
    # Insert test data
    chunks = [
        Chunk(text="Python programming language", metadata={"doc_id": "1"}),
        Chunk(text="JavaScript web development", metadata={"doc_id": "2"}),
        Chunk(text="Machine learning with Python", metadata={"doc_id": "3"}),
    ]
    vector_store.upsert_chunks(chunks)

    # Search for Python-related content
    results = vector_store.search("Python coding", limit=2)

    assert len(results) <= 2
    assert len(results) > 0
    # Top result should be Python-related
    assert "Python" in results[0]["text"]


def test_search_returns_scores(vector_store):
    """Test that search results include similarity scores."""
    chunks = [
        Chunk(text="Sample text for search", metadata={"doc_id": "test"})
    ]
    vector_store.upsert_chunks(chunks)

    results = vector_store.search("sample text", limit=1)

    assert len(results) > 0
    assert "score" in results[0]
    assert 0.0 <= results[0]["score"] <= 1.0


def test_search_respects_limit(vector_store):
    """Test that search respects the limit parameter."""
    chunks = [
        Chunk(text=f"Document number {i}", metadata={"doc_id": f"doc-{i}"})
        for i in range(10)
    ]
    vector_store.upsert_chunks(chunks)

    results = vector_store.search("document", limit=3)

    assert len(results) <= 3


def test_delete_by_doc_id(vector_store):
    """Test deleting vectors by document ID."""
    chunks = [
        Chunk(text="Doc 1 content to delete", metadata={"doc_id": "delete-me"}),
        Chunk(text="Doc 2 content to keep", metadata={"doc_id": "keep-me"}),
    ]
    vector_store.upsert_chunks(chunks)

    # Delete by doc_id
    vector_store.delete_by_doc_id("delete-me")

    # Search should not return deleted doc
    results = vector_store.search("delete", limit=5)
    doc_ids = [r["metadata"]["doc_id"] for r in results]
    assert "delete-me" not in doc_ids


def test_search_with_score_threshold(vector_store):
    """Test that score threshold filters low-quality results."""
    chunks = [
        Chunk(text="Highly relevant document", metadata={"doc_id": "1"}),
        Chunk(text="Somewhat related content", metadata={"doc_id": "2"}),
    ]
    vector_store.upsert_chunks(chunks)

    # Search with high threshold - should get fewer results
    high_threshold_results = vector_store.search(
        "Highly relevant document",
        limit=10,
        score_threshold=0.9
    )

    # At least the exact match should be above 0.9
    assert len(high_threshold_results) > 0
    assert all(r["score"] >= 0.9 for r in high_threshold_results)


def test_upsert_empty_list_returns_none(vector_store):
    """Test that upserting empty list handles gracefully."""
    result = vector_store.upsert_chunks([])
    assert result is None


def test_search_formats_results_correctly(vector_store):
    """Test that search results have expected structure."""
    chunks = [
        Chunk(
            text="Test content",
            metadata={
                "doc_id": "test-123",
                "filename": "test.txt",
                "chunk_index": 0
            }
        )
    ]
    vector_store.upsert_chunks(chunks)

    results = vector_store.search("test", limit=1)

    assert len(results) > 0
    result = results[0]

    # Check structure
    assert "id" in result
    assert "score" in result
    assert "text" in result
    assert "metadata" in result

    # Check metadata
    assert result["metadata"]["doc_id"] == "test-123"
    assert result["metadata"]["filename"] == "test.txt"
    assert result["metadata"]["chunk_index"] == 0


def test_vector_store_singleton():
    """Test that get_vector_store returns singleton."""
    from ingestion.vector_store import get_vector_store

    store1 = get_vector_store()
    store2 = get_vector_store()

    # Should be same instance
    assert store1 is store2
