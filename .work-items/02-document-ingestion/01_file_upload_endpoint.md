# Step 01: Implement File Upload Endpoint

## Objective

Create a REST API endpoint `POST /upload/file` that accepts multipart file uploads for PDF, DOCX, and Markdown documents, validates file types, and queues them for asynchronous ingestion processing.

## Atomic Implementation

This step is atomic: it either creates a working upload endpoint with validation and background processing, or fails with clear error messages. No partial state.

## TDD Cycle

### Red Phase

Write failing tests that define expected endpoint behavior:

```python
# tests/test_upload_endpoint.py
import pytest
from fastapi.testclient import TestClient
from io import BytesIO
from app.main import app

client = TestClient(app)

def test_upload_pdf_returns_ingestion_id():
    """Test that uploading a valid PDF returns an ingestion ID."""
    file_content = b"%PDF-1.4 fake pdf content"
    files = {"file": ("test.pdf", BytesIO(file_content), "application/pdf")}

    response = client.post("/upload/file", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert "ingestion_id" in data
    assert len(data["ingestion_id"]) > 0

def test_upload_docx_succeeds():
    """Test that uploading a DOCX file is accepted."""
    file_content = b"PK\x03\x04 fake docx"  # DOCX files start with ZIP header
    files = {
        "file": (
            "test.docx",
            BytesIO(file_content),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    }

    response = client.post("/upload/file", files=files)
    assert response.status_code == 200

def test_upload_markdown_succeeds():
    """Test that uploading a Markdown file is accepted."""
    file_content = b"# Test Markdown\n\nThis is a test."
    files = {"file": ("test.md", BytesIO(file_content), "text/markdown")}

    response = client.post("/upload/file", files=files)
    assert response.status_code == 200

def test_upload_unsupported_type_returns_400():
    """Test that unsupported file types return 400 error."""
    file_content = b"MZ\x90\x00 fake exe"
    files = {"file": ("malware.exe", BytesIO(file_content), "application/x-msdownload")}

    response = client.post("/upload/file", files=files)

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]

def test_upload_no_file_returns_422():
    """Test that missing file parameter returns validation error."""
    response = client.post("/upload/file")
    assert response.status_code == 422

def test_ingestion_pipeline_is_called(monkeypatch):
    """Test that the ingestion pipeline is triggered for valid uploads."""
    ingestion_called = []

    def mock_start_ingestion(file_path: str, filename: str):
        ingestion_called.append((file_path, filename))

    monkeypatch.setattr("app.routes.upload.start_ingestion", mock_start_ingestion)

    file_content = b"%PDF-1.4 test"
    files = {"file": ("doc.pdf", BytesIO(file_content), "application/pdf")}

    response = client.post("/upload/file", files=files)

    assert response.status_code == 200
    assert len(ingestion_called) == 1
    assert ingestion_called[0][1] == "doc.pdf"
```

**Expected Result**: All tests fail because endpoint doesn't exist yet.

### Green Phase

1. **Create FastAPI application structure** (if not exists):
   ```python
   # app/main.py
   from fastapi import FastAPI
   from app.routes import upload

   app = FastAPI(
       title="Knowledge Base Agent",
       description="Document ingestion and Q&A system",
       version="0.1.0"
   )

   # Include routers
   app.include_router(upload.router, prefix="/upload", tags=["ingestion"])

   @app.get("/")
   async def root():
       return {"message": "Knowledge Base Agent API", "version": "0.1.0"}
   ```

2. **Create upload route with validation**:
   ```python
   # app/routes/upload.py
   from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
   import shutil
   import uuid
   import os
   from pathlib import Path

   router = APIRouter()

   SUPPORTED_TYPES = {
       "application/pdf",
       "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
       "text/markdown",
   }

   UPLOAD_DIR = Path("/tmp/kb_uploads")
   UPLOAD_DIR.mkdir(exist_ok=True)

   @router.post("/file")
   async def upload_file(
       file: UploadFile = File(...),
       background_tasks: BackgroundTasks = None
   ):
       """Upload a document for ingestion.

       Accepts PDF, DOCX, and Markdown files. Returns an ingestion ID for tracking.
       """
       # Validate file type
       if file.content_type not in SUPPORTED_TYPES:
           raise HTTPException(
               status_code=400,
               detail=f"Unsupported file type: {file.content_type}. "
                      f"Supported types: PDF, DOCX, Markdown"
           )

       # Generate unique ID and save to temp location
       ingestion_id = str(uuid.uuid4())
       temp_filename = f"{ingestion_id}_{file.filename}"
       temp_path = UPLOAD_DIR / temp_filename

       try:
           with temp_path.open("wb") as buffer:
               shutil.copyfileobj(file.file, buffer)
       except Exception as e:
           raise HTTPException(
               status_code=500,
               detail=f"Failed to save uploaded file: {str(e)}"
           )
       finally:
           file.file.close()

       # Queue ingestion in background
       if background_tasks:
           background_tasks.add_task(
               start_ingestion,
               str(temp_path),
               file.filename,
               ingestion_id
           )
       else:
           # For testing without background tasks
           start_ingestion(str(temp_path), file.filename, ingestion_id)

       return {
           "status": "accepted",
           "ingestion_id": ingestion_id,
           "filename": file.filename
       }

   def start_ingestion(file_path: str, filename: str, ingestion_id: str):
       """Start the ingestion pipeline for an uploaded file.

       This is a placeholder that will be implemented in later steps.
       """
       # TODO: Implement in step 03-05
       # 1. Parse document to extract text
       # 2. Chunk text into passages
       # 3. Generate embeddings
       # 4. Store in Qdrant
       # 5. Save artifact
       print(f"[INGESTION] Processing {filename} (ID: {ingestion_id}) from {file_path}")
   ```

3. **Update app/__init__.py** to expose router:
   ```python
   # app/routes/__init__.py
   from . import upload

   __all__ = ["upload"]
   ```

4. **Run tests**:
   ```bash
   pytest tests/test_upload_endpoint.py -v
   ```

**Expected Result**: All tests pass.

### Refactor Phase

1. **Extract validation logic** to reusable function:
   ```python
   # app/routes/upload.py
   from typing import Set

   def validate_file_type(content_type: str, supported_types: Set[str]) -> None:
       """Validate that file type is supported.

       Args:
           content_type: MIME type of the uploaded file
           supported_types: Set of allowed MIME types

       Raises:
           HTTPException: If file type is not supported
       """
       if content_type not in supported_types:
           supported_list = ", ".join(supported_types)
           raise HTTPException(
               status_code=400,
               detail=f"Unsupported file type: {content_type}. Supported: {supported_list}"
           )

   @router.post("/file")
   async def upload_file(...):
       validate_file_type(file.content_type, SUPPORTED_TYPES)
       # ... rest of implementation
   ```

2. **Add filename sanitization** for security:
   ```python
   import re

   def sanitize_filename(filename: str) -> str:
       """Remove potentially dangerous characters from filename.

       Args:
           filename: Original filename from upload

       Returns:
           Sanitized filename safe for filesystem storage
       """
       # Remove path traversal attempts
       filename = os.path.basename(filename)
       # Remove non-alphanumeric except dots, dashes, underscores
       filename = re.sub(r'[^\w\-.]', '_', filename)
       # Limit length
       return filename[:255]

   @router.post("/file")
   async def upload_file(...):
       safe_filename = sanitize_filename(file.filename)
       temp_filename = f"{ingestion_id}_{safe_filename}"
       # ...
   ```

3. **Add logging** for monitoring:
   ```python
   import logging

   logger = logging.getLogger(__name__)

   @router.post("/file")
   async def upload_file(...):
       logger.info(f"Received upload: {file.filename} ({file.content_type})")
       # ...
       logger.info(f"Queued ingestion: {ingestion_id} for {file.filename}")
       return {...}
   ```

4. **Add configuration** for upload limits:
   ```python
   # app/config.py (update existing Config class)
   class Config(BaseSettings):
       # ... existing fields

       # Upload configuration
       max_upload_size: int = 10 * 1024 * 1024  # 10MB
       upload_temp_dir: str = "/tmp/kb_uploads"
   ```

5. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: implement file upload endpoint

   - Add POST /upload/file endpoint with multipart support
   - Validate MIME types (PDF, DOCX, Markdown)
   - Save uploads to temp directory with UUID
   - Queue background ingestion task
   - Add filename sanitization for security
   - Add comprehensive error handling
   - Tests verify file validation and ingestion queueing

   Covers Task 03 from original requirements.
   All tests passing.
   "
   ```

## Acceptance Criteria Verification

- [x] POST /upload/file endpoint exists and accepts multipart/form-data
- [x] PDF, DOCX, and Markdown files are accepted (return 200)
- [x] Unsupported file types return 400 with clear error message
- [x] Response includes `ingestion_id` for tracking
- [x] Uploaded files saved to temporary location
- [x] Background task queues file for ingestion pipeline
- [x] Filename sanitization prevents directory traversal
- [x] Tests verify all scenarios (valid types, invalid types, missing file)

## Files Created/Modified

- Created: `app/main.py` (FastAPI app initialization)
- Created: `app/routes/__init__.py`
- Created: `app/routes/upload.py` (upload endpoint)
- Created: `tests/test_upload_endpoint.py`
- Modified: `app/config.py` (add upload settings)

## Rollback Strategy

If this step fails:
1. Remove `app/routes/upload.py`
2. Remove `tests/test_upload_endpoint.py`
3. Run `git reset --hard HEAD~1`
4. Review error logs and fix issues
5. Retry step from Red phase

## Dependencies

Requires:
- FastAPI and Uvicorn (installed in F01)
- python-multipart for file uploads: `pip install python-multipart`
- Virtual environment activated

## Testing the Endpoint Manually

Start the server:
```bash
uvicorn app.main:app --reload
```

Test with curl:
```bash
# Valid PDF upload
curl -X POST "http://localhost:8000/upload/file" \
  -F "file=@/path/to/document.pdf"

# Invalid file type
curl -X POST "http://localhost:8000/upload/file" \
  -F "file=@/path/to/image.jpg"
```

Or visit `http://localhost:8000/docs` for interactive API documentation.

## Next Step

Proceed to `02_link_ingestion_endpoint.md` - Implement URL ingestion with Firecrawl
