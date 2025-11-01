"""Test artifact storage system."""

import pytest
from pathlib import Path
import json


@pytest.fixture
def artifact_store(tmp_path):
    """Create artifact store with temporary directory."""
    from ingestion.artifacts import ArtifactStore

    store = ArtifactStore(base_dir=str(tmp_path))
    yield store
    # Cleanup handled by tmp_path fixture


def test_save_upload_creates_artifact(artifact_store, tmp_path):
    """Test that saving an upload creates artifact and metadata files."""
    # Create a temporary file to upload
    test_file = tmp_path / "test_upload.pdf"
    test_file.write_bytes(b"%PDF-1.4 test content")

    artifact_id = artifact_store.save_upload(
        file_path=str(test_file),
        original_name="document.pdf",
        doc_id="doc-123",
        vector_ids=["vec-1", "vec-2", "vec-3"]
    )

    # Verify artifact exists
    assert artifact_id is not None
    assert len(artifact_id) > 0

    # Verify metadata file exists
    metadata = artifact_store.get_metadata(artifact_id)
    assert metadata["filename"] == "document.pdf"
    assert metadata["doc_id"] == "doc-123"
    assert metadata["vector_ids"] == ["vec-1", "vec-2", "vec-3"]
    assert metadata["source"] == "upload"
    assert "upload_time" in metadata


def test_save_web_page_creates_artifact(artifact_store):
    """Test that saving web content creates HTML and text artifacts."""
    url = "https://example.com/article"
    html_content = "<html><body><h1>Test</h1><p>Content</p></body></html>"
    text_content = "Test\nContent"

    artifact_id = artifact_store.save_web_page(
        url=url,
        html_content=html_content,
        text_content=text_content,
        doc_id="web-123",
        vector_ids=["vec-10", "vec-11"]
    )

    # Verify artifact exists
    assert artifact_id is not None

    # Verify metadata
    metadata = artifact_store.get_metadata(artifact_id)
    assert metadata["source"] == "web"
    assert metadata["url"] == url
    assert metadata["doc_id"] == "web-123"


def test_get_artifact_returns_file_content(artifact_store, tmp_path):
    """Test that get_artifact retrieves the original file."""
    test_file = tmp_path / "original.txt"
    test_file.write_text("Original content")

    artifact_id = artifact_store.save_upload(
        file_path=str(test_file),
        original_name="test.txt",
        doc_id="doc-1",
        vector_ids=[]
    )

    # Retrieve artifact
    artifact_path = artifact_store.get_artifact(artifact_id)
    assert artifact_path is not None
    assert Path(artifact_path).exists()

    # Verify content
    content = Path(artifact_path).read_text()
    assert "Original content" in content


def test_delete_artifact_removes_files(artifact_store, tmp_path):
    """Test that deleting artifact removes all associated files."""
    test_file = tmp_path / "delete_me.pdf"
    test_file.write_bytes(b"test")

    artifact_id = artifact_store.save_upload(
        file_path=str(test_file),
        original_name="temp.pdf",
        doc_id="doc-del",
        vector_ids=[]
    )

    # Delete artifact
    artifact_store.delete_artifact(artifact_id)

    # Verify files are gone
    assert artifact_store.get_artifact(artifact_id) is None
    assert artifact_store.get_metadata(artifact_id) is None


def test_save_upload_preserves_extension(artifact_store, tmp_path):
    """Test that file extension is preserved."""
    test_file = tmp_path / "test.docx"
    test_file.write_bytes(b"docx content")

    artifact_id = artifact_store.save_upload(
        file_path=str(test_file),
        original_name="document.docx",
        doc_id="doc-ext",
        vector_ids=[]
    )

    artifact_path = artifact_store.get_artifact(artifact_id)
    assert artifact_path is not None
    assert artifact_path.endswith(".docx")


def test_artifact_store_creates_directories(tmp_path):
    """Test that artifact store creates required directories."""
    from ingestion.artifacts import ArtifactStore

    base_dir = tmp_path / "artifacts"
    store = ArtifactStore(base_dir=str(base_dir))

    # Verify directories exist
    assert (base_dir / "uploads").exists()
    assert (base_dir / "web").exists()


def test_get_artifact_returns_none_for_nonexistent(artifact_store):
    """Test that get_artifact returns None for non-existent ID."""
    result = artifact_store.get_artifact("nonexistent-id")
    assert result is None


def test_get_metadata_returns_none_for_nonexistent(artifact_store):
    """Test that get_metadata returns None for non-existent ID."""
    result = artifact_store.get_metadata("nonexistent-id")
    assert result is None


def test_metadata_includes_file_size(artifact_store, tmp_path):
    """Test that metadata includes file size."""
    test_file = tmp_path / "sized.txt"
    test_content = "A" * 1000  # 1000 bytes
    test_file.write_text(test_content)

    artifact_id = artifact_store.save_upload(
        file_path=str(test_file),
        original_name="sized.txt",
        doc_id="doc-size",
        vector_ids=[]
    )

    metadata = artifact_store.get_metadata(artifact_id)
    assert "file_size" in metadata
    assert metadata["file_size"] == 1000
