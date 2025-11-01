# Step 04: Generate Vector Embeddings

## Objective

Convert text chunks into 384-dimensional vector embeddings using the sentence-transformers model, create a Qdrant collection, and persist vectors with metadata for similarity search.

## Atomic Implementation

This step is atomic: it either creates a working embedding service and Qdrant integration with successful vector storage, or fails with clear error messages.

## TDD Cycle

### Red Phase

Write failing tests that define expected embedding and vector store behavior:

```python
# tests/test_embeddings.py
import pytest
import numpy as np
from ingestion.embeddings import EmbeddingService, get_embedding_service

def test_embedding_service_singleton():
    """Test that embedding service uses singleton pattern."""
    service1 = get_embedding_service()
    service2 = get_embedding_service()
    assert service1 is service2

def test_embed_single_text():
    """Test embedding a single text string."""
    service = get_embedding_service()
    text = "This is a test sentence for embedding."

    embedding = service.embed_text(text)

    assert isinstance(embedding, list)
    assert len(embedding) == 384  # MiniLM dimension
    assert all(isinstance(x, float) for x in embedding)
    assert not any(np.isnan(embedding))  # No NaN values

def test_embed_multiple_texts():
    """Test batch embedding of multiple texts."""
    service = get_embedding_service()
    texts = [
        "First document about machine learning.",
        "Second document about natural language processing.",
        "Third document about vector databases."
    ]

    embeddings = service.embed_texts(texts)

    assert len(embeddings) == 3
    assert all(len(emb) == 384 for emb in embeddings)
    assert all(isinstance(emb, list) for emb in embeddings)

def test_embed_empty_text_raises_error():
    """Test that empty text raises appropriate error."""
    service = get_embedding_service()

    with pytest.raises(ValueError, match="empty"):
        service.embed_text("")

def test_similar_texts_have_similar_embeddings():
    """Test that semantically similar texts have high cosine similarity."""
    service = get_embedding_service()

    text1 = "The cat sat on the mat."
    text2 = "A cat was sitting on a mat."
    text3 = "Quantum physics is complex."

    emb1 = service.embed_text(text1)
    emb2 = service.embed_text(text2)
    emb3 = service.embed_text(text3)

    # Cosine similarity helper
    def cosine_sim(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    sim_1_2 = cosine_sim(emb1, emb2)
    sim_1_3 = cosine_sim(emb1, emb3)

    # Similar sentences should be more similar than different ones
    assert sim_1_2 > sim_1_3
    assert sim_1_2 > 0.7  # High similarity threshold
```

```python
# tests/test_vector_store.py
import pytest
from qdrant_client import QdrantClient
from ingestion.vector_store import VectorStore, get_vector_store
from ingestion.chunker import Chunk

@pytest.fixture
def test_collection_name():
    """Use a test collection to avoid polluting production data."""
    return "test_kb_passages"

@pytest.fixture
def vector_store(test_collection_name):
    """Create a vector store instance for testing."""
    store = VectorStore(collection_name=test_collection_name)
    yield store
    # Cleanup: delete test collection
    store.delete_collection()

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

    assert result is True or "operation_id" in result  # Success indicator

def test_upsert_multiple_vectors(vector_store):
    """Test batch upserting multiple vectors."""
    chunks = [
        Chunk(
            text=f"Document {i} content",
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

def test_delete_by_doc_id(vector_store):
    """Test deleting vectors by document ID."""
    chunks = [
        Chunk(text="Doc 1 content", metadata={"doc_id": "delete-me"}),
        Chunk(text="Doc 2 content", metadata={"doc_id": "keep-me"}),
    ]
    vector_store.upsert_chunks(chunks)

    # Delete by doc_id
    vector_store.delete_by_doc_id("delete-me")

    # Search should not return deleted doc
    results = vector_store.search("Doc 1", limit=5)
    doc_ids = [r["metadata"]["doc_id"] for r in results]
    assert "delete-me" not in doc_ids
```

**Expected Result**: Tests fail because modules don't exist yet.

### Green Phase

1. **Implement embedding service**:
   ```python
   # ingestion/embeddings.py
   """Embedding generation service using sentence transformers."""
   from typing import List, Optional
   from sentence_transformers import SentenceTransformer
   import logging

   logger = logging.getLogger(__name__)

   class EmbeddingService:
       """Service for generating text embeddings."""

       def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
           """Initialize the embedding service.

           Args:
               model_name: HuggingFace model identifier
           """
           logger.info(f"Loading embedding model: {model_name}")
           self.model = SentenceTransformer(model_name)
           self.dimension = self.model.get_sentence_embedding_dimension()
           logger.info(f"Model loaded, embedding dimension: {self.dimension}")

       def embed_text(self, text: str) -> List[float]:
           """Generate embedding for a single text.

           Args:
               text: The text to embed

           Returns:
               List of floats representing the embedding vector

           Raises:
               ValueError: If text is empty
           """
           if not text or not text.strip():
               raise ValueError("Cannot embed empty text")

           try:
               embedding = self.model.encode(text, show_progress_bar=False)
               return embedding.tolist()

           except Exception as e:
               logger.error(f"Error generating embedding: {e}")
               raise

       def embed_texts(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
           """Generate embeddings for multiple texts.

           Args:
               texts: List of texts to embed
               batch_size: Number of texts to process at once

           Returns:
               List of embedding vectors
           """
           if not texts:
               return []

           # Filter out empty texts
           valid_texts = [t for t in texts if t and t.strip()]
           if len(valid_texts) != len(texts):
               logger.warning(f"Filtered out {len(texts) - len(valid_texts)} empty texts")

           if not valid_texts:
               return []

           try:
               embeddings = self.model.encode(
                   valid_texts,
                   batch_size=batch_size,
                   show_progress_bar=len(valid_texts) > 100
               )
               return embeddings.tolist()

           except Exception as e:
               logger.error(f"Error batch embedding {len(texts)} texts: {e}")
               raise

   # Singleton instance
   _embedding_service: Optional[EmbeddingService] = None

   def get_embedding_service() -> EmbeddingService:
       """Get or create the embedding service singleton."""
       global _embedding_service
       if _embedding_service is None:
           _embedding_service = EmbeddingService()
       return _embedding_service
   ```

2. **Implement vector store**:
   ```python
   # ingestion/vector_store.py
   """Qdrant vector store integration for document chunks."""
   from typing import List, Dict, Any, Optional
   from qdrant_client import QdrantClient
   from qdrant_client.models import (
       Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
   )
   import uuid
   import logging
   from app.config import get_config
   from ingestion.chunker import Chunk
   from ingestion.embeddings import get_embedding_service

   logger = logging.getLogger(__name__)

   class VectorStore:
       """Qdrant vector store for semantic search."""

       def __init__(self, collection_name: str = "kb_passages"):
           """Initialize the vector store.

           Args:
               collection_name: Name of the Qdrant collection
           """
           config = get_config()
           self.collection_name = collection_name

           # Initialize Qdrant client
           self.client = QdrantClient(
               url=config.qdrant_url,
               api_key=config.qdrant_api_key
           )

           # Initialize embedding service
           self.embedding_service = get_embedding_service()

           # Create collection if it doesn't exist
           self._ensure_collection_exists()

       def _ensure_collection_exists(self):
           """Create collection if it doesn't exist."""
           collections = self.client.get_collections().collections
           collection_names = [c.name for c in collections]

           if self.collection_name not in collection_names:
               logger.info(f"Creating collection: {self.collection_name}")
               self.client.create_collection(
                   collection_name=self.collection_name,
                   vectors_config=VectorParams(
                       size=self.embedding_service.dimension,
                       distance=Distance.COSINE
                   )
               )
               logger.info(f"Collection created: {self.collection_name}")
           else:
               logger.info(f"Collection already exists: {self.collection_name}")

       def upsert_chunks(self, chunks: List[Chunk]) -> Any:
           """Upload chunks with embeddings to Qdrant.

           Args:
               chunks: List of Chunk objects to store

           Returns:
               Qdrant operation result
           """
           if not chunks:
               logger.warning("No chunks to upsert")
               return None

           # Extract texts for embedding
           texts = [chunk.text for chunk in chunks]

           # Generate embeddings
           logger.info(f"Generating embeddings for {len(texts)} chunks")
           embeddings = self.embedding_service.embed_texts(texts)

           # Create Qdrant points
           points = []
           for chunk, embedding in zip(chunks, embeddings):
               point_id = str(uuid.uuid4())
               point = PointStruct(
                   id=point_id,
                   vector=embedding,
                   payload={
                       "text": chunk.text,
                       **chunk.metadata
                   }
               )
               points.append(point)

           # Upsert to Qdrant
           logger.info(f"Upserting {len(points)} points to {self.collection_name}")
           result = self.client.upsert(
               collection_name=self.collection_name,
               points=points
           )

           logger.info(f"Upserted {len(points)} vectors successfully")
           return result

       def search(
           self,
           query: str,
           limit: int = 5,
           score_threshold: float = 0.0
       ) -> List[Dict[str, Any]]:
           """Search for similar chunks.

           Args:
               query: Search query text
               limit: Maximum number of results
               score_threshold: Minimum similarity score (0-1)

           Returns:
               List of dicts with text, metadata, and score
           """
           # Generate query embedding
           query_embedding = self.embedding_service.embed_text(query)

           # Search Qdrant
           results = self.client.search(
               collection_name=self.collection_name,
               query_vector=query_embedding,
               limit=limit,
               score_threshold=score_threshold
           )

           # Format results
           formatted_results = []
           for result in results:
               formatted_results.append({
                   "id": result.id,
                   "score": result.score,
                   "text": result.payload.get("text", ""),
                   "metadata": {
                       k: v for k, v in result.payload.items()
                       if k != "text"
                   }
               })

           return formatted_results

       def delete_by_doc_id(self, doc_id: str):
           """Delete all chunks for a document.

           Args:
               doc_id: Document identifier
           """
           logger.info(f"Deleting chunks for doc_id: {doc_id}")

           self.client.delete(
               collection_name=self.collection_name,
               points_selector=Filter(
                   must=[
                       FieldCondition(
                           key="doc_id",
                           match=MatchValue(value=doc_id)
                       )
                   ]
               )
           )

       def delete_collection(self):
           """Delete the entire collection (for testing/cleanup)."""
           logger.warning(f"Deleting collection: {self.collection_name}")
           self.client.delete_collection(self.collection_name)

   # Singleton instance
   _vector_store: Optional[VectorStore] = None

   def get_vector_store() -> VectorStore:
       """Get or create the vector store singleton."""
       global _vector_store
       if _vector_store is None:
           _vector_store = VectorStore()
       return _vector_store
   ```

3. **Update ingestion/__init__.py**:
   ```python
   # ingestion/__init__.py
   from . import parsers, chunker, firecrawl_client, embeddings, vector_store

   __all__ = ["parsers", "chunker", "firecrawl_client", "embeddings", "vector_store"]
   ```

4. **Run tests**:
   ```bash
   # Make sure Qdrant is running first
   docker run -p 6333:6333 qdrant/qdrant

   # Run tests
   pytest tests/test_embeddings.py tests/test_vector_store.py -v
   ```

**Expected Result**: All tests pass.

### Refactor Phase

1. **Add batch size configuration**:
   ```python
   # app/config.py
   class Config(BaseSettings):
       # ... existing fields
       embedding_batch_size: int = 100
       embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
   ```

2. **Add caching for frequently accessed embeddings**:
   ```python
   # ingestion/embeddings.py
   from functools import lru_cache

   class EmbeddingService:
       @lru_cache(maxsize=1000)
       def embed_text_cached(self, text: str) -> tuple:
           """Cached version for repeated queries."""
           embedding = self.embed_text(text)
           return tuple(embedding)  # Lists aren't hashable
   ```

3. **Add performance monitoring**:
   ```python
   # ingestion/vector_store.py
   import time

   def upsert_chunks(self, chunks: List[Chunk]) -> Any:
       start_time = time.time()

       # ... existing implementation

       elapsed = time.time() - start_time
       logger.info(
           f"Upserted {len(points)} vectors in {elapsed:.2f}s "
           f"({len(points)/elapsed:.1f} vectors/sec)"
       )
       return result
   ```

4. **Add error recovery** for partial failures:
   ```python
   def upsert_chunks(self, chunks: List[Chunk]) -> Any:
       # Batch upload to handle large document sets
       BATCH_SIZE = 100
       all_results = []

       for i in range(0, len(chunks), BATCH_SIZE):
           batch = chunks[i:i+BATCH_SIZE]
           try:
               result = self._upsert_batch(batch)
               all_results.append(result)
           except Exception as e:
               logger.error(f"Error upserting batch {i//BATCH_SIZE}: {e}")
               # Continue with other batches
               continue

       return all_results
   ```

5. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: implement embedding generation and vector storage

   - Add EmbeddingService using sentence-transformers/all-MiniLM-L6-v2
   - Generate 384-dimensional embeddings with batch support
   - Implement VectorStore for Qdrant integration
   - Create collection with cosine distance metric
   - Support upsert, search, and delete operations
   - Add singleton pattern for service instances
   - Add performance monitoring and error handling
   - Tests verify embedding quality and search accuracy

   Covers Task 06 from original requirements.
   All tests passing.
   "
   ```

## Acceptance Criteria Verification

- [x] Embeddings generated using all-MiniLM-L6-v2 model
- [x] Each embedding has dimension 384 with no NaN values
- [x] Batch embedding supports processing 100+ chunks efficiently
- [x] Qdrant collection created with cosine distance metric
- [x] Vectors and metadata upserted successfully
- [x] Search returns relevant chunks with similarity scores
- [x] Delete by doc_id removes all associated chunks
- [x] Tests verify embedding quality and search relevance

## Files Created/Modified

- Created: `ingestion/embeddings.py` (embedding service)
- Created: `ingestion/vector_store.py` (Qdrant integration)
- Created: `tests/test_embeddings.py`
- Created: `tests/test_vector_store.py`
- Modified: `ingestion/__init__.py`
- Modified: `app/config.py` (add embedding settings)

## Rollback Strategy

If this step fails:
1. Remove `ingestion/embeddings.py` and `ingestion/vector_store.py`
2. Remove test files
3. Delete test Qdrant collection if created
4. Run `git reset --hard HEAD~1`
5. Review error logs and fix issues
6. Retry step from Red phase

## Dependencies

Requires:
- sentence-transformers: already in requirements.txt
- qdrant-client: already in requirements.txt
- numpy: installed with sentence-transformers
- Qdrant running on localhost:6333 or cloud instance

## Starting Qdrant for Development

Using Docker:
```bash
docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant
```

Or use Qdrant Cloud and update `.env`:
```bash
QDRANT_URL=https://your-instance.qdrant.io
QDRANT_API_KEY=your_api_key_here
```

## Testing Embeddings and Search Manually

```python
# Test in Python REPL
from ingestion.embeddings import get_embedding_service
from ingestion.vector_store import get_vector_store
from ingestion.chunker import Chunk

# Generate embedding
service = get_embedding_service()
emb = service.embed_text("Machine learning is fascinating")
print(f"Embedding dimension: {len(emb)}")

# Store and search
store = get_vector_store()
chunks = [
    Chunk("Python is a programming language", {"doc_id": "1"}),
    Chunk("Machine learning uses algorithms", {"doc_id": "2"}),
]
store.upsert_chunks(chunks)

results = store.search("programming", limit=2)
for r in results:
    print(f"Score: {r['score']:.3f} - {r['text']}")
```

## Next Step

Proceed to `05_persist_artifacts.md` - Implement artifact storage and complete ingestion pipeline
