"""Test link ingestion endpoint."""

import pytest
from fastapi.testclient import TestClient


def test_upload_link_with_valid_url(monkeypatch):
    """Test that uploading a valid URL returns an ingestion ID."""
    from app.main import app

    class MockFirecrawlClient:
        def scrape(self, url: str):
            return {
                "success": True,
                "data": {
                    "content": "Test content",
                    "markdown": "# Test Article",
                }
            }

    # Mock the Firecrawl client
    monkeypatch.setattr(
        "app.routes.upload.get_firecrawl_client",
        lambda: MockFirecrawlClient()
    )

    client = TestClient(app)
    response = client.post(
        "/upload/link",
        json={"url": "https://example.com/article"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert "ingestion_id" in data
    assert data["ingestion_id"].startswith("link_")


def test_upload_link_with_invalid_url_returns_422():
    """Test that malformed URLs are rejected."""
    from app.main import app

    client = TestClient(app)

    # Test various invalid URLs
    invalid_urls = [
        "not-a-url",
        "ftp://example.com",  # Unsupported protocol
        "javascript:alert(1)",  # XSS attempt
        "file:///etc/passwd",  # Local file
        "http://",  # Incomplete
        "",  # Empty string
    ]

    for invalid_url in invalid_urls:
        response = client.post(
            "/upload/link",
            json={"url": invalid_url}
        )
        assert response.status_code == 422, f"Should reject: {invalid_url}"


def test_upload_link_without_url_returns_422():
    """Test that missing URL field returns validation error."""
    from app.main import app

    client = TestClient(app)

    # Empty request body
    response = client.post("/upload/link", json={})
    assert response.status_code == 422

    # No request body at all
    response = client.post("/upload/link")
    assert response.status_code == 422


def test_firecrawl_is_called_with_url(monkeypatch):
    """Test that Firecrawl client is invoked with the provided URL."""
    from app.main import app

    client = TestClient(app)
    firecrawl_calls = []

    class MockFirecrawlClient:
        def scrape(self, url: str):
            firecrawl_calls.append(url)
            return {
                "success": True,
                "data": {
                    "content": "Test content from example.com",
                    "markdown": "# Test Article\n\nContent here",
                }
            }

    # Mock the Firecrawl client
    monkeypatch.setattr(
        "app.routes.upload.get_firecrawl_client",
        lambda: MockFirecrawlClient()
    )

    response = client.post(
        "/upload/link",
        json={"url": "https://example.com/test-article"}
    )

    assert response.status_code == 200
    assert len(firecrawl_calls) == 1
    assert firecrawl_calls[0] == "https://example.com/test-article"


def test_firecrawl_error_does_not_crash_endpoint(monkeypatch):
    """Test that Firecrawl failures are handled gracefully."""
    from app.main import app

    client = TestClient(app)

    class MockFirecrawlClient:
        def scrape(self, url: str):
            raise Exception("Firecrawl API timeout")

    # Mock the Firecrawl client to raise error
    monkeypatch.setattr(
        "app.routes.upload.get_firecrawl_client",
        lambda: MockFirecrawlClient()
    )

    response = client.post(
        "/upload/link",
        json={"url": "https://example.com/article"}
    )

    # Should return error response, not crash
    assert response.status_code in [500, 503]  # Internal error or service unavailable
    data = response.json()
    assert "detail" in data or "error" in data


def test_url_safety_checks_reject_ssrf():
    """Test that SSRF attempts are blocked."""
    from app.main import app

    client = TestClient(app)

    # Common SSRF payloads
    ssrf_urls = [
        "http://localhost/admin",
        "http://127.0.0.1/secret",
        "http://0.0.0.0/internal",
        "http://169.254.169.254/latest/meta-data/",  # AWS metadata
        "http://[::1]/private",  # IPv6 localhost
        "http://10.0.0.1/internal",  # Private IP
        "http://192.168.1.1/router",  # Private IP
        "http://172.16.0.1/admin",  # Private IP
    ]

    for ssrf_url in ssrf_urls:
        response = client.post(
            "/upload/link",
            json={"url": ssrf_url}
        )
        assert response.status_code == 422, f"Should reject SSRF: {ssrf_url}"

        # Handle Pydantic validation error format (detail is a list)
        detail = response.json()["detail"]
        if isinstance(detail, list):
            # Pydantic validation error format
            error_msg = str(detail).lower()
        else:
            error_msg = detail.lower()

        assert "private" in error_msg or \
               "local" in error_msg or \
               "not allowed" in error_msg, \
               f"Error message should mention security issue for {ssrf_url}: {error_msg}"
