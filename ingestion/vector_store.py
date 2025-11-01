"""Qdrant vector store integration for document chunks."""

import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

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

        start_time = time.time()

        # Extract texts for embedding
        texts = [chunk.text for chunk in chunks]

        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} chunks")
        embed_start = time.time()
        embeddings = self.embedding_service.embed_texts(texts)
        embed_time = time.time() - embed_start

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

        # Upsert to Qdrant with batching for large sets
        logger.info(f"Upserting {len(points)} points to {self.collection_name}")
        upsert_start = time.time()

        # Batch upload for large datasets
        BATCH_SIZE = 100
        results = []
        for i in range(0, len(points), BATCH_SIZE):
            batch = points[i:i+BATCH_SIZE]
            try:
                result = self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Error upserting batch {i//BATCH_SIZE + 1}: {e}")
                # Continue with next batch
                continue

        upsert_time = time.time() - upsert_start
        total_time = time.time() - start_time

        logger.info(
            f"Upserted {len(points)} vectors in {total_time:.2f}s "
            f"(embed: {embed_time:.2f}s, upsert: {upsert_time:.2f}s, "
            f"{len(points)/total_time:.1f} vectors/sec)"
        )

        return results if len(results) > 1 else (results[0] if results else None)

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
        try:
            self.client.delete_collection(self.collection_name)
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")


# Singleton instance
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get or create the vector store singleton."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store


def reset_vector_store() -> None:
    """Reset the vector store singleton (for testing)."""
    global _vector_store
    _vector_store = None
