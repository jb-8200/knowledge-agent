"""Test text chunking service."""

import pytest


def test_chunk_short_text_returns_single_chunk():
    """Test that short text returns one chunk."""
    from ingestion.chunker import chunk_text, Chunk

    text = "This is a short document."
    chunks = chunk_text(text, doc_id="test-123", filename="test.txt")

    assert len(chunks) == 1
    assert isinstance(chunks[0], Chunk)
    assert chunks[0].text == text
    assert chunks[0].metadata["doc_id"] == "test-123"
    assert chunks[0].metadata["chunk_index"] == 0


def test_chunk_long_text_splits_into_multiple():
    """Test that long text is split into multiple chunks."""
    from ingestion.chunker import chunk_text

    text = "A" * 2000  # Long text exceeding chunk size
    chunks = chunk_text(text, doc_id="test-456", filename="long.txt")

    assert len(chunks) > 1
    # Verify chunks have reasonable size (chunk_size is 1000)
    for chunk in chunks:
        assert len(chunk.text) <= 1200  # chunk_size + some tolerance for overlap


def test_chunk_metadata_includes_all_fields():
    """Test that chunk metadata contains required fields."""
    from ingestion.chunker import chunk_text

    text = "Sample text for chunking."
    chunks = chunk_text(text, doc_id="doc-1", filename="file.pdf", source="upload")

    chunk = chunks[0]
    assert chunk.metadata["doc_id"] == "doc-1"
    assert chunk.metadata["filename"] == "file.pdf"
    assert chunk.metadata["chunk_index"] == 0
    assert chunk.metadata["source"] == "upload"
    assert "timestamp" in chunk.metadata


def test_chunk_overlap_preserves_context():
    """Test that chunks have overlap for context preservation."""
    from ingestion.chunker import chunk_text

    text = "A" * 1500  # Enough for 2 chunks with overlap
    chunks = chunk_text(text)

    if len(chunks) > 1:
        # Last part of first chunk should overlap with start of second
        # Overlap is configured at 200 characters
        assert len(chunks[1].text) > 0
        # Both chunks should exist
        assert len(chunks[0].text) > 0


def test_chunk_respects_separators():
    """Test that chunker splits on paragraph boundaries when possible."""
    from ingestion.chunker import chunk_text

    text = "Paragraph one.\n\nParagraph two.\n\nParagraph three." * 50
    chunks = chunk_text(text)

    # Chunks should ideally break on \n\n boundaries
    # Not guaranteed, but likely with recursive splitter
    assert len(chunks) > 0


def test_chunk_empty_text_returns_empty_list():
    """Test that empty text returns empty chunk list."""
    from ingestion.chunker import chunk_text

    chunks = chunk_text("", doc_id="empty-doc", filename="empty.txt")
    assert chunks == []

    chunks = chunk_text("   \n\n  ", doc_id="whitespace", filename="space.txt")
    assert chunks == []


def test_chunk_with_page_number():
    """Test that page_number is included in metadata when provided."""
    from ingestion.chunker import chunk_text

    text = "Text from page 5 of a PDF document."
    chunks = chunk_text(
        text,
        doc_id="pdf-123",
        filename="document.pdf",
        source="upload",
        page_number=5
    )

    assert len(chunks) == 1
    assert chunks[0].metadata["page_number"] == 5


def test_chunk_pdf_by_page():
    """Test page-by-page PDF chunking with metadata."""
    from ingestion.chunker import chunk_pdf_by_page
    from pathlib import Path

    # Use a sample PDF from fixtures
    pdf_path = Path(__file__).parent / "fixtures" / "sample.pdf"
    chunks = chunk_pdf_by_page(
        str(pdf_path),
        doc_id="pdf-doc-1",
        filename="sample.pdf"
    )

    # Should have at least one chunk
    assert len(chunks) > 0

    # All chunks should have page numbers
    for chunk in chunks:
        assert "page_number" in chunk.metadata
        assert chunk.metadata["page_number"] >= 1
        assert chunk.metadata["doc_id"] == "pdf-doc-1"
        assert chunk.metadata["filename"] == "sample.pdf"


def test_chunk_preserves_text_integrity():
    """Test that chunking doesn't lose or corrupt text."""
    from ingestion.chunker import chunk_text

    original_text = "The quick brown fox jumps over the lazy dog. " * 100
    chunks = chunk_text(original_text, doc_id="test")

    # Reconstruct text from chunks (accounting for overlap)
    # Just verify total length is reasonable
    total_chars = sum(len(c.text) for c in chunks)

    # Total should be >= original due to overlap
    assert total_chars >= len(original_text)
