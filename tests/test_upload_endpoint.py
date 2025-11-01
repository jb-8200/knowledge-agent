"""Test file upload endpoint."""

import pytest
from fastapi.testclient import TestClient
from io import BytesIO


def test_upload_pdf_returns_ingestion_id():
    """Test that uploading a valid PDF returns an ingestion ID.

    Red Phase: This test will fail because endpoint doesn't exist yet.
    """
    from app.main import app

    client = TestClient(app)

    file_content = b"%PDF-1.4 fake pdf content"
    files = {"file": ("test.pdf", BytesIO(file_content), "application/pdf")}

    response = client.post("/upload/file", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert "ingestion_id" in data
    assert len(data["ingestion_id"]) > 0


def test_upload_docx_succeeds():
    """Test that uploading a DOCX file is accepted.

    Red Phase: This test will fail because endpoint doesn't exist yet.
    """
    from app.main import app

    client = TestClient(app)

    file_content = b"PK\x03\x04 fake docx"  # DOCX files start with ZIP header
    files = {
        "file": (
            "test.docx",
            BytesIO(file_content),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    }

    response = client.post("/upload/file", files=files)
    assert response.status_code == 200


def test_upload_markdown_succeeds():
    """Test that uploading a Markdown file is accepted.

    Red Phase: This test will fail because endpoint doesn't exist yet.
    """
    from app.main import app

    client = TestClient(app)

    file_content = b"# Test Markdown\n\nThis is a test."
    files = {"file": ("test.md", BytesIO(file_content), "text/markdown")}

    response = client.post("/upload/file", files=files)
    assert response.status_code == 200


def test_upload_unsupported_type_returns_400():
    """Test that unsupported file types return 400 error.

    Red Phase: This test will fail because endpoint doesn't exist yet.
    """
    from app.main import app

    client = TestClient(app)

    file_content = b"MZ\x90\x00 fake exe"
    files = {
        "file": ("malware.exe", BytesIO(file_content), "application/x-msdownload")
    }

    response = client.post("/upload/file", files=files)

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_no_file_returns_422():
    """Test that missing file parameter returns validation error.

    Red Phase: This test will fail because endpoint doesn't exist yet.
    """
    from app.main import app

    client = TestClient(app)

    response = client.post("/upload/file")
    assert response.status_code == 422


def test_ingestion_pipeline_is_called(monkeypatch):
    """Test that the ingestion pipeline is triggered for valid uploads.

    Red Phase: This test will fail because endpoint doesn't exist yet.
    """
    from app.main import app

    client = TestClient(app)

    ingestion_called = []

    def mock_start_ingestion(file_path: str, filename: str, ingestion_id: str):
        ingestion_called.append((file_path, filename, ingestion_id))

    monkeypatch.setattr(
        "app.routes.upload.start_ingestion", mock_start_ingestion
    )

    file_content = b"%PDF-1.4 test"
    files = {"file": ("doc.pdf", BytesIO(file_content), "application/pdf")}

    response = client.post("/upload/file", files=files)

    assert response.status_code == 200
    assert len(ingestion_called) == 1
    assert ingestion_called[0][1] == "doc.pdf"
