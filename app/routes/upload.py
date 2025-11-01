"""File upload endpoints for document ingestion."""

import logging
import os
import re
import shutil
import uuid
from pathlib import Path
from typing import Set

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks

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
