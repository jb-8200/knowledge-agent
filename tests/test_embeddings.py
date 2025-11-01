"""Test embedding generation service."""

import pytest
import numpy as np


def test_embedding_service_singleton():
    """Test that embedding service uses singleton pattern."""
    from ingestion.embeddings import get_embedding_service

    service1 = get_embedding_service()
    service2 = get_embedding_service()
    assert service1 is service2


def test_embed_single_text():
    """Test embedding a single text string."""
    from ingestion.embeddings import get_embedding_service

    service = get_embedding_service()
    text = "This is a test sentence for embedding."

    embedding = service.embed_text(text)

    assert isinstance(embedding, list)
    assert len(embedding) == 384  # MiniLM dimension
    assert all(isinstance(x, float) for x in embedding)
    assert not any(np.isnan(embedding))  # No NaN values


def test_embed_multiple_texts():
    """Test batch embedding of multiple texts."""
    from ingestion.embeddings import get_embedding_service

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
    from ingestion.embeddings import get_embedding_service

    service = get_embedding_service()

    with pytest.raises(ValueError, match="empty"):
        service.embed_text("")


def test_embed_whitespace_only_raises_error():
    """Test that whitespace-only text raises error."""
    from ingestion.embeddings import get_embedding_service

    service = get_embedding_service()

    with pytest.raises(ValueError, match="empty"):
        service.embed_text("   \n\t  ")


def test_similar_texts_have_similar_embeddings():
    """Test that semantically similar texts have high cosine similarity."""
    from ingestion.embeddings import get_embedding_service

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


def test_embed_texts_filters_empty_strings():
    """Test that batch embedding handles empty strings gracefully."""
    from ingestion.embeddings import get_embedding_service

    service = get_embedding_service()
    texts = ["Valid text", "", "Another valid text", "  "]

    # Should process only valid texts (2 out of 4)
    embeddings = service.embed_texts(texts)

    # Only non-empty texts should be embedded
    assert len(embeddings) == 2
    assert all(len(emb) == 384 for emb in embeddings)


def test_embedding_dimension_property():
    """Test that service exposes embedding dimension."""
    from ingestion.embeddings import get_embedding_service

    service = get_embedding_service()

    assert hasattr(service, 'dimension')
    assert service.dimension == 384


def test_embed_texts_empty_list_returns_empty():
    """Test that empty list returns empty embeddings."""
    from ingestion.embeddings import get_embedding_service

    service = get_embedding_service()

    embeddings = service.embed_texts([])
    assert embeddings == []
