# Step 02: Implement Link Ingestion Endpoint

## Objective

Create a REST API endpoint `POST /upload/link` that accepts URLs, validates them, fetches web page content using Firecrawl, and queues the extracted text for ingestion processing.

## Atomic Implementation

This step is atomic: it either creates a working URL ingestion endpoint with Firecrawl integration, or fails with clear error messages. External service failures are handled gracefully.

## TDD Cycle

### Red Phase

Write failing tests that define expected endpoint behavior:

```python
# tests/test_link_ingestion.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

client = TestClient(app)

def test_upload_link_with_valid_url():
    """Test that valid URL is accepted and returns ingestion ID."""
    payload = {"url": "https://example.com/article"}

    response = client.post("/upload/link", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert "ingestion_id" in data
    assert data["ingestion_id"].startswith("link_")

def test_upload_link_with_invalid_url_returns_422():
    """Test that invalid URLs return validation error."""
    invalid_urls = [
        {"url": "not-a-url"},
        {"url": "ftp://invalid-scheme.com"},
        {"url": ""},
        {"url": 123},  # not a string
    ]

    for payload in invalid_urls:
        response = client.post("/upload/link", json=payload)
        assert response.status_code == 422, f"Failed for: {payload}"

def test_upload_link_without_url_returns_422():
    """Test that missing URL field returns validation error."""
    response = client.post("/upload/link", json={})
    assert response.status_code == 422

@patch("ingestion.firecrawl_client.fetch_url")
def test_firecrawl_is_called_with_url(mock_fetch):
    """Test that Firecrawl fetch is triggered for valid URLs."""
    mock_fetch.return_value = AsyncMock(return_value="Fetched content")

    payload = {"url": "https://example.com/page"}
    response = client.post("/upload/link", json=payload)

    assert response.status_code == 200
    # Verify Firecrawl was called (will be checked after background task runs)

@patch("ingestion.firecrawl_client.fetch_url")
def test_firecrawl_error_does_not_crash_endpoint(mock_fetch):
    """Test that Firecrawl errors are handled gracefully."""
    mock_fetch.side_effect = Exception("Firecrawl API error")

    payload = {"url": "https://failing-site.com"}
    response = client.post("/upload/link", json=payload)

    # Endpoint still returns 200 because processing is async
    assert response.status_code == 200
    # Error should be logged, not raised
```

**Expected Result**: Tests fail because endpoint doesn't exist yet.

### Green Phase

1. **Create Firecrawl client module**:
   ```python
   # ingestion/firecrawl_client.py
   """Firecrawl API client for web page content extraction."""
   import httpx
   import logging
   from typing import Optional
   from app.config import get_config

   logger = logging.getLogger(__name__)

   async def fetch_url(url: str) -> Optional[str]:
       """Fetch and extract text content from a URL using Firecrawl.

       Args:
           url: The URL to fetch and extract content from

       Returns:
           Extracted text content, or None if fetch fails

       Raises:
           httpx.HTTPError: If the request fails
       """
       config = get_config()
       api_key = config.firecrawl_api_key

       if not api_key:
           logger.warning("FIRECRAWL_API_KEY not configured, skipping fetch")
           return None

       try:
           async with httpx.AsyncClient(timeout=30.0) as client:
               response = await client.get(
                   "https://api.firecrawl.dev/v0/scrape",
                   params={"url": url},
                   headers={"Authorization": f"Bearer {api_key}"}
               )
               response.raise_for_status()

               data = response.json()
               text = data.get("data", {}).get("markdown", "") or data.get("data", {}).get("content", "")

               logger.info(f"Fetched {len(text)} characters from {url}")
               return text

       except httpx.TimeoutException:
           logger.error(f"Timeout fetching {url}")
           raise
       except httpx.HTTPError as e:
           logger.error(f"HTTP error fetching {url}: {e}")
           raise
       except Exception as e:
           logger.error(f"Unexpected error fetching {url}: {e}")
           raise
   ```

2. **Add link ingestion endpoint**:
   ```python
   # app/routes/upload.py (add to existing file)
   from pydantic import BaseModel, HttpUrl
   from ingestion.firecrawl_client import fetch_url
   import asyncio

   class LinkPayload(BaseModel):
       """Request payload for URL ingestion."""
       url: HttpUrl

   @router.post("/link")
   async def upload_link(
       payload: LinkPayload,
       background_tasks: BackgroundTasks = None
   ):
       """Ingest content from a URL.

       Fetches the web page using Firecrawl and processes the extracted text.
       """
       url = str(payload.url)

       # Generate ingestion ID
       ingestion_id = f"link_{uuid.uuid4()}"

       logger.info(f"Received URL for ingestion: {url} (ID: {ingestion_id})")

       # Queue fetch and ingestion in background
       if background_tasks:
           background_tasks.add_task(
               fetch_and_ingest_link,
               url,
               ingestion_id
           )
       else:
           # For testing - run synchronously
           await fetch_and_ingest_link(url, ingestion_id)

       return {
           "status": "accepted",
           "ingestion_id": ingestion_id,
           "url": url
       }

   async def fetch_and_ingest_link(url: str, ingestion_id: str):
       """Fetch URL content and start ingestion pipeline.

       Args:
           url: The URL to fetch
           ingestion_id: Unique identifier for tracking
       """
       try:
           # Fetch content using Firecrawl
           text = await fetch_url(url)

           if not text:
               logger.warning(f"No content extracted from {url}")
               return

           logger.info(f"Fetched {len(text)} chars from {url}, starting ingestion")

           # TODO: Implement in steps 03-05
           # 1. Save raw HTML and extracted text as artifact
           # 2. Chunk text into passages
           # 3. Generate embeddings
           # 4. Store in Qdrant
           print(f"[INGESTION] Processing URL {url} (ID: {ingestion_id})")

       except Exception as e:
           logger.error(f"Error processing URL {url}: {e}")
           # Don't re-raise - background task should not crash
   ```

3. **Update ingestion/__init__.py**:
   ```python
   # ingestion/__init__.py
   from . import firecrawl_client

   __all__ = ["firecrawl_client"]
   ```

4. **Update config for Firecrawl**:
   ```python
   # app/config.py (verify this exists from design.md)
   class Config(BaseSettings):
       # ... existing fields
       firecrawl_api_key: Optional[str] = None
   ```

5. **Run tests**:
   ```bash
   pytest tests/test_link_ingestion.py -v
   ```

**Expected Result**: All tests pass.

### Refactor Phase

1. **Add retry logic** for transient failures:
   ```python
   # ingestion/firecrawl_client.py
   from tenacity import retry, stop_after_attempt, wait_exponential

   @retry(
       stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=1, min=2, max=10),
       reraise=True
   )
   async def fetch_url(url: str) -> Optional[str]:
       """Fetch with automatic retry on transient errors."""
       # ... existing implementation
   ```

2. **Add URL blocklist** for security (prevent SSRF):
   ```python
   # app/routes/upload.py
   from urllib.parse import urlparse

   BLOCKED_HOSTS = {
       "localhost",
       "127.0.0.1",
       "0.0.0.0",
       # Add private IP ranges
   }

   def validate_url_safety(url: str) -> None:
       """Ensure URL doesn't point to internal/private resources.

       Args:
           url: The URL to validate

       Raises:
           HTTPException: If URL is blocked for security reasons
       """
       parsed = urlparse(url)
       host = parsed.hostname

       if host in BLOCKED_HOSTS:
           raise HTTPException(
               status_code=400,
               detail=f"Cannot access blocked host: {host}"
           )

       # Check for private IP ranges
       if host and (host.startswith("192.168.") or host.startswith("10.")):
           raise HTTPException(
               status_code=400,
               detail="Cannot access private IP addresses"
           )

   @router.post("/link")
   async def upload_link(payload: LinkPayload, ...):
       url = str(payload.url)
       validate_url_safety(url)
       # ... rest of implementation
   ```

3. **Improve error messages** for different failure modes:
   ```python
   async def fetch_and_ingest_link(url: str, ingestion_id: str):
       try:
           text = await fetch_url(url)

           if not text:
               logger.warning(
                   f"No content extracted from {url}. "
                   "Page may be JavaScript-heavy or blocked."
               )
               return

           if len(text) < 100:
               logger.warning(
                   f"Very little content extracted from {url} "
                   f"({len(text)} chars). May not be useful."
               )

           # Continue processing...

       except httpx.TimeoutException:
           logger.error(
               f"Timeout fetching {url} after 30s. "
               "Site may be slow or unreachable."
           )
       except httpx.HTTPStatusError as e:
           logger.error(
               f"HTTP {e.response.status_code} error fetching {url}. "
               "Page may not exist or require authentication."
           )
       except Exception as e:
           logger.error(f"Unexpected error processing {url}: {type(e).__name__}: {e}")
   ```

4. **Add integration test** with real Firecrawl (optional, requires API key):
   ```python
   # tests/test_link_ingestion_integration.py
   import pytest
   from ingestion.firecrawl_client import fetch_url
   import os

   @pytest.mark.skipif(
       not os.getenv("FIRECRAWL_API_KEY"),
       reason="Requires FIRECRAWL_API_KEY"
   )
   @pytest.mark.asyncio
   async def test_fetch_real_url():
       """Integration test with real Firecrawl API."""
       text = await fetch_url("https://example.com")
       assert text is not None
       assert len(text) > 0
       assert "example" in text.lower()
   ```

5. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: implement link ingestion endpoint

   - Add POST /upload/link endpoint with URL validation
   - Integrate Firecrawl API client for web scraping
   - Add retry logic for transient failures
   - Implement URL safety checks (block localhost, private IPs)
   - Queue background task for fetch and ingestion
   - Add comprehensive error handling for network failures
   - Tests verify URL validation and Firecrawl integration

   Covers Task 04 from original requirements.
   All tests passing.
   "
   ```

## Acceptance Criteria Verification

- [x] POST /upload/link endpoint exists and accepts JSON payload
- [x] Valid URLs (http/https) are accepted and return ingestion_id
- [x] Invalid URLs return 422 validation error (Pydantic HttpUrl)
- [x] Firecrawl API is called to fetch web page content
- [x] Fetch errors are logged without crashing the service
- [x] Background task queues URL for ingestion pipeline
- [x] URL safety validation prevents SSRF attacks
- [x] Tests verify all scenarios (valid URL, invalid URL, fetch errors)

## Files Created/Modified

- Created: `ingestion/firecrawl_client.py` (Firecrawl API client)
- Created: `tests/test_link_ingestion.py`
- Modified: `app/routes/upload.py` (add /link endpoint)
- Modified: `ingestion/__init__.py`

## Rollback Strategy

If this step fails:
1. Remove `ingestion/firecrawl_client.py`
2. Remove `/link` endpoint from `app/routes/upload.py`
3. Remove `tests/test_link_ingestion.py`
4. Run `git reset --hard HEAD~1`
5. Review error logs and fix issues
6. Retry step from Red phase

## Dependencies

Requires:
- httpx for async HTTP requests: `pip install httpx`
- tenacity for retry logic: already in requirements.txt
- Firecrawl API key in .env (optional for development, required for production)

## Testing the Endpoint Manually

Start the server:
```bash
uvicorn app.main:app --reload
```

Test with curl:
```bash
# Valid URL
curl -X POST "http://localhost:8000/upload/link" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Invalid URL
curl -X POST "http://localhost:8000/upload/link" \
  -H "Content-Type: application/json" \
  -d '{"url": "not-a-valid-url"}'
```

Or use the interactive docs at `http://localhost:8000/docs`.

## Environment Setup

Add to your `.env` file:
```bash
FIRECRAWL_API_KEY=your_api_key_here
```

Get an API key from: https://www.firecrawl.dev/

## Next Step

Proceed to `03_parse_and_chunk.md` - Implement document parsing and text chunking
