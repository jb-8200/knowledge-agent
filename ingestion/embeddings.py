"""Embedding generation service using sentence transformers."""

import logging
from typing import List, Optional

from sentence_transformers import SentenceTransformer
from app.config import get_config

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings."""

    def __init__(self, model_name: Optional[str] = None):
        """Initialize the embedding service.

        Args:
            model_name: HuggingFace model identifier (defaults to config value)
        """
        if model_name is None:
            config = get_config()
            model_name = config.embedding_model

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


def reset_embedding_service() -> None:
    """Reset the embedding service singleton (for testing)."""
    global _embedding_service
    _embedding_service = None
