"""Test end-to-end ingestion pipeline."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


@pytest.fixture
def pipeline():
    """Create pipeline instance for testing."""
    from ingestion.pipeline import IngestionPipeline

    return IngestionPipeline()


def test_ingest_file_end_to_end(pipeline, tmp_path):
    """Test complete file ingestion pipeline."""
    # Create test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Sample text content for testing ingestion pipeline.")

    result = pipeline.ingest_file(
        file_path=str(test_file),
        filename="test.txt"
    )

    # Verify result structure
    assert "doc_id" in result
    assert "artifact_id" in result
    assert "chunks_created" in result
    assert result["chunks_created"] > 0
    assert result["status"] == "success"


def test_ingest_file_with_pdf(pipeline):
    """Test ingestion with real PDF fixture."""
    pdf_path = Path(__file__).parent / "fixtures" / "sample.pdf"

    result = pipeline.ingest_file(
        file_path=str(pdf_path),
        filename="sample.pdf"
    )

    assert result["status"] == "success"
    assert result["chunks_created"] > 0


def test_ingest_file_returns_artifact_id(pipeline, tmp_path):
    """Test that artifact_id can be used to retrieve artifact."""
    test_file = tmp_path / "retrieve_test.txt"
    test_file.write_text("Content for retrieval testing")

    result = pipeline.ingest_file(str(test_file), "retrieve_test.txt")

    # Verify artifact can be retrieved
    from ingestion.artifacts import get_artifact_store

    store = get_artifact_store()
    artifact_path = store.get_artifact(result["artifact_id"])
    assert artifact_path is not None

    # Verify metadata
    metadata = store.get_metadata(result["artifact_id"])
    assert metadata["doc_id"] == result["doc_id"]
    assert len(metadata["vector_ids"]) > 0


def test_ingest_file_with_insufficient_content_fails(pipeline, tmp_path):
    """Test that files with insufficient content raise error."""
    test_file = tmp_path / "tiny.txt"
    test_file.write_text("x")  # Only 1 character

    with pytest.raises(ValueError, match="Insufficient content"):
        pipeline.ingest_file(str(test_file), "tiny.txt")


def test_ingest_file_with_invalid_path_fails(pipeline):
    """Test that non-existent file raises error."""
    with pytest.raises(FileNotFoundError):
        pipeline.ingest_file("/nonexistent/file.pdf", "fake.pdf")


def test_pipeline_creates_chunks(pipeline, tmp_path):
    """Test that pipeline creates multiple chunks for longer content."""
    test_file = tmp_path / "long.txt"
    # Create content longer than chunk size (1000 chars)
    test_file.write_text("This is test content. " * 100)  # ~2200 chars

    result = pipeline.ingest_file(str(test_file), "long.txt")

    # Should create multiple chunks
    assert result["chunks_created"] >= 2


def test_pipeline_stores_vectors(pipeline, tmp_path):
    """Test that vectors are stored in Qdrant."""
    test_file = tmp_path / "vector_test.txt"
    test_file.write_text("Content for vector storage testing.")

    result = pipeline.ingest_file(str(test_file), "vector_test.txt")

    # Verify vectors can be searched
    from ingestion.vector_store import get_vector_store

    store = get_vector_store()
    search_results = store.search("vector storage", limit=5)

    # Should find at least one result
    assert len(search_results) > 0


def test_pipeline_links_vectors_to_artifact(pipeline, tmp_path):
    """Test that vector IDs are saved in artifact metadata."""
    test_file = tmp_path / "link_test.txt"
    test_file.write_text("Test content for linking vectors to artifacts.")

    result = pipeline.ingest_file(str(test_file), "link_test.txt")

    # Verify artifact has vector_ids in metadata
    from ingestion.artifacts import get_artifact_store

    store = get_artifact_store()
    metadata = store.get_metadata(result["artifact_id"])

    assert "vector_ids" in metadata
    assert len(metadata["vector_ids"]) > 0
    assert len(metadata["vector_ids"]) == result["chunks_created"]


def test_pipeline_handles_docx(pipeline):
    """Test pipeline with DOCX file."""
    docx_path = Path(__file__).parent / "fixtures" / "sample.docx"

    result = pipeline.ingest_file(str(docx_path), "sample.docx")

    assert result["status"] == "success"
    assert result["chunks_created"] > 0


def test_pipeline_handles_markdown(pipeline):
    """Test pipeline with Markdown file."""
    md_path = Path(__file__).parent / "fixtures" / "sample.md"

    result = pipeline.ingest_file(str(md_path), "sample.md")

    assert result["status"] == "success"
    assert result["chunks_created"] > 0


def test_pipeline_result_structure(pipeline, tmp_path):
    """Test that pipeline result has all expected fields."""
    test_file = tmp_path / "structure_test.txt"
    test_file.write_text("Content for structure validation.")

    result = pipeline.ingest_file(str(test_file), "structure_test.txt")

    # Verify all required fields present
    assert "doc_id" in result
    assert "artifact_id" in result
    assert "chunks_created" in result
    assert "status" in result

    # Verify types
    assert isinstance(result["doc_id"], str)
    assert isinstance(result["artifact_id"], str)
    assert isinstance(result["chunks_created"], int)
    assert result["status"] == "success"
