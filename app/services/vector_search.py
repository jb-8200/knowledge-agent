"""Vector search service for RAG retrieval."""

from typing import List, Optional
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter
from qdrant_client.http.exceptions import UnexpectedResponse
import logging
import os
import time

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
        start_time = time.time()

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

        # Log search
        logger.info(
            f"Vector search: query_len={len(query)}, top_k={top_k}, "
            f"filters={filters is not None}, threshold={score_threshold}"
        )

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

            # Log results
            elapsed = (time.time() - start_time) * 1000  # ms
            logger.info(
                f"Search completed: {len(results)} results in {elapsed:.1f}ms, "
                f"top_score={results[0].score if results else 'N/A'}"
            )

            return results

        except UnexpectedResponse as e:
            logger.error(f"Qdrant search failed: {str(e)}")
            if "not found" in str(e).lower():
                raise ValueError(f"Collection '{self.collection_name}' does not exist")
            raise
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            raise RuntimeError(f"Search failed: {str(e)}")
