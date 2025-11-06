"""Tests for vector search service."""

import pytest
from app.services.vector_search import VectorSearchService, SearchResult
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import uuid


@pytest.fixture
def qdrant_client():
    """Create test Qdrant client with in-memory storage."""
    client = QdrantClient(location=":memory:")
    collection_name = "test_kb_passages"

    # Create collection with same config as production
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )

    # Insert test data
    test_points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=[0.1] * 384,  # Placeholder vector
            payload={
                "text": "Machine learning is a subset of artificial intelligence.",
                "doc_id": "doc1",
                "filename": "ml_basics.pdf",
                "chunk_index": 0,
                "page_number": 1,
                "source": "upload",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        ),
        PointStruct(
            id=str(uuid.uuid4()),
            vector=[0.9] * 384,  # Different vector
            payload={
                "text": "Deep learning uses neural networks with multiple layers.",
                "doc_id": "doc1",
                "filename": "ml_basics.pdf",
                "chunk_index": 1,
                "page_number": 2,
                "source": "upload",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        )
    ]
    client.upsert(collection_name=collection_name, points=test_points)

    return client, collection_name


def test_vector_search_service_initialization():
    """Test that VectorSearchService initializes with embedding model."""
    service = VectorSearchService()
    assert service.embedding_model is not None
    assert service.collection_name == "kb_passages"


def test_embed_query_returns_correct_dimensions():
    """Test query embedding produces 384-dimensional vectors."""
    service = VectorSearchService()
    query = "What is machine learning?"

    vector = service.embed_query(query)

    assert isinstance(vector, list)
    assert len(vector) == 384
    assert all(isinstance(x, float) for x in vector)


def test_embed_query_consistency():
    """Test that same query produces same embedding."""
    service = VectorSearchService()
    query = "artificial intelligence"

    vector1 = service.embed_query(query)
    vector2 = service.embed_query(query)

    assert vector1 == vector2


def test_search_vectors_returns_top_k_results(qdrant_client):
    """Test that search returns correct number of results."""
    client, collection_name = qdrant_client
    service = VectorSearchService(qdrant_client=client, collection_name=collection_name)

    results = service.search_vectors("machine learning", top_k=2)

    assert len(results) <= 2
    assert all(isinstance(r, SearchResult) for r in results)


def test_search_result_contains_required_fields(qdrant_client):
    """Test that search results include text, metadata, and score."""
    client, collection_name = qdrant_client
    service = VectorSearchService(qdrant_client=client, collection_name=collection_name)

    results = service.search_vectors("neural networks", top_k=1)

    assert len(results) > 0
    result = results[0]
    assert hasattr(result, 'text')
    assert hasattr(result, 'metadata')
    assert hasattr(result, 'score')
    assert isinstance(result.text, str)
    assert isinstance(result.metadata, dict)
    assert isinstance(result.score, float)


def test_search_metadata_completeness(qdrant_client):
    """Test that metadata includes all required fields."""
    client, collection_name = qdrant_client
    service = VectorSearchService(qdrant_client=client, collection_name=collection_name)

    results = service.search_vectors("deep learning", top_k=1)

    assert len(results) > 0
    metadata = results[0].metadata
    required_fields = ['doc_id', 'filename', 'chunk_index', 'source']
    for field in required_fields:
        assert field in metadata


def test_search_results_ranked_by_score(qdrant_client):
    """Test that results are sorted by similarity score (descending)."""
    client, collection_name = qdrant_client
    service = VectorSearchService(qdrant_client=client, collection_name=collection_name)

    results = service.search_vectors("AI and ML", top_k=5)

    if len(results) > 1:
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)


def test_empty_query_raises_validation_error():
    """Test that empty queries are rejected."""
    service = VectorSearchService()

    with pytest.raises(ValueError, match="Query cannot be empty"):
        service.search_vectors("", top_k=5)


def test_whitespace_only_query_raises_validation_error():
    """Test that whitespace-only queries are rejected."""
    service = VectorSearchService()

    with pytest.raises(ValueError, match="Query cannot be empty"):
        service.search_vectors("   \n\t  ", top_k=5)


def test_search_with_empty_database_returns_empty_list():
    """Test that searching empty collection returns no results."""
    client = QdrantClient(location=":memory:")
    collection_name = "empty_collection"
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )

    service = VectorSearchService(qdrant_client=client, collection_name=collection_name)
    results = service.search_vectors("test query", top_k=5)

    assert len(results) == 0


def test_top_k_parameter_respected(qdrant_client):
    """Test that top_k limits number of results."""
    client, collection_name = qdrant_client
    service = VectorSearchService(qdrant_client=client, collection_name=collection_name)

    results_3 = service.search_vectors("learning", top_k=3)
    results_1 = service.search_vectors("learning", top_k=1)

    assert len(results_3) <= 3
    assert len(results_1) <= 1
