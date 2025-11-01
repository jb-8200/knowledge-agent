# Step 01: Implement Vector Search Logic

## Objective

Create a vector search service that embeds user queries using the same model as document embeddings and retrieves the top-K most similar passages from Qdrant with metadata and similarity scores.

## Atomic Implementation

This step is atomic: it either creates a complete vector search service with query embedding, Qdrant search, and result formatting, or fails with clear error messages. No partial state.

## TDD Cycle

### Red Phase

Write failing tests that define expected search behavior:

```python
# tests/test_vector_search.py
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
```

**Expected Result**: All tests fail because VectorSearchService doesn't exist yet.

### Green Phase

1. **Create VectorSearchService implementation**:

```python
# app/services/vector_search.py
from typing import List, Optional
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter
import logging
import os

logger = logging.getLogger(__name__)

class SearchResult(BaseModel):
    """Represents a single search result from vector search."""
    text: str
    metadata: dict
    score: float

class VectorSearchService:
    """Service for vector similarity search over Qdrant collection."""

    def __init__(
        self,
        qdrant_client: Optional[QdrantClient] = None,
        collection_name: str = "kb_passages",
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """Initialize vector search service.

        Args:
            qdrant_client: Optional Qdrant client instance (for testing)
            collection_name: Name of Qdrant collection to search
            embedding_model_name: Sentence transformer model name
        """
        self.collection_name = collection_name

        # Initialize Qdrant client
        if qdrant_client is not None:
            self.qdrant_client = qdrant_client
        else:
            qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
            self.qdrant_client = QdrantClient(url=qdrant_url)

        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model_name}")
        self.embedding_model = SentenceTransformer(embedding_model_name)
        logger.info("Embedding model loaded successfully")

    def embed_query(self, query: str) -> List[float]:
        """Embed query text to vector using same model as documents.

        Args:
            query: Query text to embed

        Returns:
            384-dimensional embedding vector
        """
        # Encode query (returns numpy array)
        embedding = self.embedding_model.encode(query, show_progress_bar=False)

        # Convert to list of floats
        return embedding.tolist()

    def validate_query(self, query: str) -> None:
        """Validate query string.

        Args:
            query: Query string to validate

        Raises:
            ValueError: If query is empty or whitespace-only
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty or whitespace-only")

    def search_vectors(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Filter] = None,
        score_threshold: Optional[float] = None
    ) -> List[SearchResult]:
        """Search for similar passages in Qdrant.

        Args:
            query: Query text to search for
            top_k: Number of results to return (default: 5)
            filters: Optional Qdrant filters for metadata
            score_threshold: Minimum similarity score (default: no threshold)

        Returns:
            List of SearchResult objects ranked by similarity

        Raises:
            ValueError: If query is empty
        """
        # Validate query
        self.validate_query(query)

        # Embed query
        logger.info(f"Searching for: {query[:100]}...")
        query_vector = self.embed_query(query)

        try:
            # Search Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                query_filter=filters,
                with_payload=True,
                score_threshold=score_threshold
            )

            logger.info(f"Found {len(search_results)} results")

            # Convert to SearchResult objects
            results = []
            for hit in search_results:
                result = SearchResult(
                    text=hit.payload.get("text", ""),
                    metadata={
                        "doc_id": hit.payload.get("doc_id"),
                        "filename": hit.payload.get("filename"),
                        "chunk_index": hit.payload.get("chunk_index"),
                        "page_number": hit.payload.get("page_number"),
                        "source": hit.payload.get("source"),
                        "timestamp": hit.payload.get("timestamp")
                    },
                    score=hit.score
                )
                results.append(result)

            return results

        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            raise
```

2. **Create services package init**:

```python
# app/services/__init__.py
from .vector_search import VectorSearchService, SearchResult

__all__ = ["VectorSearchService", "SearchResult"]
```

3. **Run tests**:
```bash
pytest tests/test_vector_search.py -v
```

**Expected Result**: All tests pass.

### Refactor Phase

1. **Add configuration management** for search parameters:

```python
# app/config.py (add to existing Config class)
class Config(BaseSettings):
    # ... existing fields ...

    # Vector Search Configuration
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    qdrant_collection_name: str = "kb_passages"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    default_top_k: int = 5
    max_top_k: int = 20
    min_relevance_score: Optional[float] = None
```

2. **Add error handling** for Qdrant connection issues:

```python
# app/services/vector_search.py
from qdrant_client.http.exceptions import UnexpectedResponse

def search_vectors(self, query: str, top_k: int = 5, ...) -> List[SearchResult]:
    """..."""
    # Validate query
    self.validate_query(query)

    # Validate top_k
    if top_k < 1:
        raise ValueError("top_k must be at least 1")
    if top_k > 20:
        logger.warning(f"top_k={top_k} exceeds maximum of 20, capping to 20")
        top_k = 20

    # Embed query
    logger.info(f"Searching for: {query[:100]}...")
    try:
        query_vector = self.embed_query(query)
    except Exception as e:
        logger.error(f"Query embedding failed: {str(e)}")
        raise ValueError(f"Failed to embed query: {str(e)}")

    # Search Qdrant
    try:
        search_results = self.qdrant_client.search(...)
        # ... rest of implementation
    except UnexpectedResponse as e:
        logger.error(f"Qdrant search failed: {str(e)}")
        if "not found" in str(e).lower():
            raise ValueError(f"Collection '{self.collection_name}' does not exist")
        raise
    except Exception as e:
        logger.error(f"Vector search failed: {str(e)}")
        raise RuntimeError(f"Search failed: {str(e)}")
```

3. **Add optional metadata filtering**:

```python
# app/services/vector_search.py
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

def build_filters(
    doc_ids: Optional[List[str]] = None,
    sources: Optional[List[str]] = None
) -> Optional[Filter]:
    """Build Qdrant filter from metadata criteria.

    Args:
        doc_ids: List of document IDs to filter by
        sources: List of sources to filter by ("upload", "web")

    Returns:
        Qdrant Filter object or None if no filters
    """
    conditions = []

    if doc_ids:
        conditions.append(
            FieldCondition(
                key="doc_id",
                match=MatchValue(any=doc_ids)
            )
        )

    if sources:
        conditions.append(
            FieldCondition(
                key="source",
                match=MatchValue(any=sources)
            )
        )

    if conditions:
        return Filter(must=conditions)

    return None
```

4. **Add comprehensive logging**:

```python
# app/services/vector_search.py
import time

def search_vectors(self, query: str, top_k: int = 5, ...) -> List[SearchResult]:
    """..."""
    start_time = time.time()

    # ... validation and embedding ...

    # Log search
    logger.info(
        f"Vector search: query_len={len(query)}, top_k={top_k}, "
        f"filters={filters is not None}, threshold={score_threshold}"
    )

    # ... search Qdrant ...

    # Log results
    elapsed = (time.time() - start_time) * 1000  # ms
    logger.info(
        f"Search completed: {len(results)} results in {elapsed:.1f}ms, "
        f"top_score={results[0].score if results else 'N/A'}"
    )

    return results
```

5. **Commit changes**:

```bash
git add .
git commit -m "feat: implement vector search service

- Add VectorSearchService with query embedding
- Integrate with Qdrant for similarity search
- Return ranked passages with text, metadata, scores
- Validate queries (reject empty/whitespace)
- Handle edge cases: empty database, connection errors
- Add metadata filtering by doc_id and source
- Add comprehensive logging with timing metrics
- Tests verify search accuracy, ranking, and edge cases

Covers Task 08 from original requirements.
All tests passing.
"
```

## Acceptance Criteria Verification

- [x] VectorSearchService initializes with embedding model
- [x] Query embedding produces 384-dimensional vectors
- [x] Same query produces consistent embeddings
- [x] Search returns top-K results ranked by similarity score
- [x] Results include text, metadata, and score fields
- [x] Metadata includes doc_id, filename, chunk_index, page_number, source
- [x] Empty queries raise ValueError with clear message
- [x] Whitespace-only queries handled same as empty
- [x] Searching empty collection returns empty list (no crash)
- [x] top_k parameter correctly limits results
- [x] Qdrant connection errors handled gracefully
- [x] All tests pass

## Files Created/Modified

- Created: `app/services/vector_search.py`
- Created: `app/services/__init__.py`
- Created: `tests/test_vector_search.py`
- Modified: `app/config.py` (add vector search settings)

## Rollback Strategy

If this step fails:
1. Remove `app/services/vector_search.py`
2. Remove `tests/test_vector_search.py`
3. Run `git reset --hard HEAD~1`
4. Investigate errors (check Qdrant connection, model download)
5. Retry step from Red phase

## Dependencies

Requires:
- Qdrant running on localhost:6333 (or configured URL)
- sentence-transformers installed: `pip install sentence-transformers`
- At least one document ingested (from F02) for realistic testing
- Qdrant collection `kb_passages` exists with embeddings

## Testing the Service Manually

Test in Python REPL:

```python
from app.services.vector_search import VectorSearchService

# Initialize service
service = VectorSearchService()

# Test embedding
vector = service.embed_query("What is machine learning?")
print(f"Vector dimension: {len(vector)}")

# Test search (requires Qdrant with data)
results = service.search_vectors("artificial intelligence", top_k=3)
for i, result in enumerate(results, 1):
    print(f"\nResult {i}:")
    print(f"  Score: {result.score:.3f}")
    print(f"  Text: {result.text[:100]}...")
    print(f"  Source: {result.metadata['filename']}")
```

## Next Step

Proceed to `02_retriever_tool.md` - Wrap vector search as LangChain Tool
