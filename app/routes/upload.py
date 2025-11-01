"""File upload endpoints for document ingestion."""

import ipaddress
import logging
import os
import re
import shutil
import uuid
from pathlib import Path
from typing import Set
from urllib.parse import urlparse

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl, field_validator
from ingestion.firecrawl_client import get_firecrawl_client

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Supported MIME types for upload
SUPPORTED_TYPES: Set[str] = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/markdown",
}

# Upload directory for temporary storage
UPLOAD_DIR = Path("/tmp/kb_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class LinkUploadRequest(BaseModel):
    """Request model for link upload."""

    url: str

    @field_validator("url")
    @classmethod
    def validate_url_safety(cls, v: str) -> str:
        """Validate URL is safe and not an SSRF target."""
        if not v or not v.strip():
            raise ValueError("URL cannot be empty")

        # Parse URL
        try:
            parsed = urlparse(v)
        except Exception:
            raise ValueError("Invalid URL format")

        # Check protocol
        if parsed.scheme not in ("http", "https"):
            raise ValueError("Only HTTP and HTTPS protocols are supported")

        # Extract hostname
        hostname = parsed.hostname
        if not hostname:
            raise ValueError("Invalid URL: missing hostname")

        # Check for localhost variants
        localhost_names = {"localhost", "0.0.0.0"}
        if hostname.lower() in localhost_names:
            raise ValueError("URLs pointing to localhost are not allowed")

        # Check if it's an IP address
        try:
            ip = ipaddress.ip_address(hostname)

            # Block loopback addresses
            if ip.is_loopback:
                raise ValueError("URLs pointing to local addresses are not allowed")

            # Block private IP ranges
            if ip.is_private:
                raise ValueError("URLs pointing to private IP addresses are not allowed")

            # Block link-local addresses
            if ip.is_link_local:
                raise ValueError("URLs pointing to link-local addresses are not allowed")

        except ValueError as e:
            # If it's not an IP, check for known SSRF targets
            if "not allowed" in str(e):
                raise
            # Not an IP address, it's a hostname - continue validation
            pass

        # Block AWS metadata endpoint
        if "169.254.169.254" in hostname:
            raise ValueError("Access to cloud metadata endpoints is not allowed")

        return v


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
            detail=f"Unsupported file type: {content_type}. Supported: {supported_list}",
        )


def sanitize_filename(filename: str) -> str:
    """Remove potentially dangerous characters from filename.

    Prevents directory traversal attacks and ensures filesystem compatibility.

    Args:
        filename: Original filename from upload

    Returns:
        Sanitized filename safe for filesystem storage
    """
    # Remove path traversal attempts
    filename = os.path.basename(filename)
    # Remove non-alphanumeric except dots, dashes, underscores
    filename = re.sub(r"[^\w\-.]", "_", filename)
    # Limit length to prevent filesystem issues
    return filename[:255]


@router.post("/file")
async def upload_file(
    file: UploadFile = File(...), background_tasks: BackgroundTasks = None
):
    """Upload a document for ingestion.

    Accepts PDF, DOCX, and Markdown files. Returns an ingestion ID for tracking.

    Args:
        file: The uploaded file (multipart/form-data)
        background_tasks: FastAPI background tasks for async processing

    Returns:
        dict: Status and ingestion_id

    Raises:
        HTTPException: If file type is unsupported or save fails
    """
    logger.info(f"Received upload: {file.filename} ({file.content_type})")

    # Validate file type
    validate_file_type(file.content_type, SUPPORTED_TYPES)

    # Generate unique ID and save to temp location
    ingestion_id = str(uuid.uuid4())
    safe_filename = sanitize_filename(file.filename)
    temp_filename = f"{ingestion_id}_{safe_filename}"
    temp_path = UPLOAD_DIR / temp_filename

    try:
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to save uploaded file: {str(e)}"
        )
    finally:
        file.file.close()

    # Queue ingestion in background
    if background_tasks:
        background_tasks.add_task(
            start_ingestion, str(temp_path), file.filename, ingestion_id
        )
    else:
        # For testing without background tasks
        start_ingestion(str(temp_path), file.filename, ingestion_id)

    logger.info(f"Queued ingestion: {ingestion_id} for {file.filename}")

    return {
        "status": "accepted",
        "ingestion_id": ingestion_id,
        "filename": file.filename,
    }


def start_ingestion(file_path: str, filename: str, ingestion_id: str):
    """Start the ingestion pipeline for an uploaded file.

    This is a placeholder that will be implemented in later steps.

    Args:
        file_path: Path to the uploaded file
        filename: Original filename
        ingestion_id: Unique ingestion identifier
    """
    # TODO: Implement in step 03-05
    # 1. Parse document to extract text
    # 2. Chunk text into passages
    # 3. Generate embeddings
    # 4. Store in Qdrant
    # 5. Save artifact
    print(f"[INGESTION] Processing {filename} (ID: {ingestion_id}) from {file_path}")


@router.post("/link")
async def upload_link(request: LinkUploadRequest, background_tasks: BackgroundTasks = None):
    """Ingest content from a web URL using Firecrawl.

    Accepts HTTP/HTTPS URLs and extracts content using Firecrawl API.
    Validates URLs to prevent SSRF attacks.

    Args:
        request: Link upload request containing the URL
        background_tasks: FastAPI background tasks for async processing

    Returns:
        dict: Status and ingestion_id

    Raises:
        HTTPException: If URL is invalid, unsafe, or Firecrawl fails
    """
    url = request.url
    logger.info(f"Received link upload: {url}")

    # Generate unique ID with "link_" prefix
    ingestion_id = f"link_{uuid.uuid4()}"

    try:
        # Get Firecrawl client and scrape content
        firecrawl = get_firecrawl_client()
        result = firecrawl.scrape(url)

        if not result.get("success"):
            logger.error(f"Firecrawl returned unsuccessful response for {url}")
            raise HTTPException(
                status_code=500,
                detail="Failed to extract content from URL"
            )

        # Extract content (prefer markdown over plain text)
        data = result.get("data", {})
        content = data.get("markdown") or data.get("content", "")

        if not content:
            logger.error(f"No content extracted from {url}")
            raise HTTPException(
                status_code=422,
                detail="No content could be extracted from the provided URL"
            )

        # Save scraped content to temp file
        temp_filename = f"{ingestion_id}.md"
        temp_path = UPLOAD_DIR / temp_filename

        try:
            with temp_path.open("w", encoding="utf-8") as f:
                f.write(content)
        except IOError as e:
            logger.error(f"Failed to save content for {url}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to save extracted content"
            )

        # Queue ingestion in background
        if background_tasks:
            background_tasks.add_task(
                start_ingestion, str(temp_path), url, ingestion_id
            )
        else:
            # For testing without background tasks
            start_ingestion(str(temp_path), url, ingestion_id)

        logger.info(f"Queued link ingestion: {ingestion_id} for {url}")

        return {
            "status": "accepted",
            "ingestion_id": ingestion_id,
            "url": url,
        }

    except HTTPException:
        raise
    except ConnectionError as e:
        logger.error(f"Network error accessing {url}: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Unable to connect to URL: {str(e)}"
        )
    except TimeoutError as e:
        logger.error(f"Timeout accessing {url}: {e}")
        raise HTTPException(
            status_code=504,
            detail=f"Request timed out accessing URL: {str(e)}"
        )
    except ValueError as e:
        logger.error(f"Invalid response from {url}: {e}")
        raise HTTPException(
            status_code=422,
            detail=f"Invalid content from URL: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during link ingestion for {url}: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Service temporarily unavailable: {str(e)}"
        )
