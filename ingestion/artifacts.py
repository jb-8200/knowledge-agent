"""Artifact storage for uploaded files and web content."""

import json
import logging
import mimetypes
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ArtifactStore:
    """Manages storage of original documents and web pages."""

    def __init__(self, base_dir: str = "artifacts"):
        """Initialize artifact store.

        Args:
            base_dir: Base directory for artifact storage
        """
        self.base_dir = Path(base_dir)
        self.upload_dir = self.base_dir / "uploads"
        self.web_dir = self.base_dir / "web"

        # Create directories
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.web_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Artifact store initialized at {self.base_dir}")

    def save_upload(
        self,
        file_path: str,
        original_name: str,
        doc_id: str,
        vector_ids: List[str]
    ) -> str:
        """Save an uploaded file with metadata.

        Args:
            file_path: Path to the temporary uploaded file
            original_name: Original filename from upload
            doc_id: Document identifier
            vector_ids: List of Qdrant point IDs

        Returns:
            Artifact ID (UUID)
        """
        artifact_id = str(uuid.uuid4())

        # Determine file extension
        ext = Path(original_name).suffix
        artifact_file = self.upload_dir / f"{artifact_id}{ext}"

        # Copy file to artifact storage
        shutil.copy2(file_path, artifact_file)

        # Create metadata
        metadata = {
            "artifact_id": artifact_id,
            "doc_id": doc_id,
            "filename": original_name,
            "upload_time": datetime.now(timezone.utc).isoformat(),
            "mime_type": mimetypes.guess_type(original_name)[0],
            "source": "upload",
            "file_size": artifact_file.stat().st_size,
            "vector_ids": vector_ids,
        }

        # Save metadata
        meta_file = self.upload_dir / f"{artifact_id}.meta.json"
        with meta_file.open("w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(
            f"Saved upload artifact {artifact_id}: {original_name} "
            f"({len(vector_ids)} vectors)"
        )
        return artifact_id

    def save_web_page(
        self,
        url: str,
        html_content: str,
        text_content: str,
        doc_id: str,
        vector_ids: List[str]
    ) -> str:
        """Save web page content with metadata.

        Args:
            url: Source URL
            html_content: Raw HTML
            text_content: Extracted text
            doc_id: Document identifier
            vector_ids: List of Qdrant point IDs

        Returns:
            Artifact ID (UUID)
        """
        artifact_id = str(uuid.uuid4())

        # Save HTML
        html_file = self.web_dir / f"{artifact_id}.html"
        html_file.write_text(html_content, encoding="utf-8")

        # Save extracted text
        text_file = self.web_dir / f"{artifact_id}.txt"
        text_file.write_text(text_content, encoding="utf-8")

        # Create metadata
        metadata = {
            "artifact_id": artifact_id,
            "doc_id": doc_id,
            "url": url,
            "upload_time": datetime.now(timezone.utc).isoformat(),
            "source": "web",
            "html_size": len(html_content),
            "text_size": len(text_content),
            "vector_ids": vector_ids,
        }

        # Save metadata
        meta_file = self.web_dir / f"{artifact_id}.meta.json"
        with meta_file.open("w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(
            f"Saved web artifact {artifact_id}: {url} "
            f"({len(vector_ids)} vectors)"
        )
        return artifact_id

    def get_artifact(self, artifact_id: str) -> Optional[str]:
        """Retrieve artifact file path.

        Args:
            artifact_id: Artifact identifier

        Returns:
            Path to artifact file, or None if not found
        """
        # Check uploads
        for ext in [".pdf", ".docx", ".md", ".txt"]:
            artifact_path = self.upload_dir / f"{artifact_id}{ext}"
            if artifact_path.exists():
                return str(artifact_path)

        # Check web artifacts
        for ext in [".html", ".txt"]:
            artifact_path = self.web_dir / f"{artifact_id}{ext}"
            if artifact_path.exists():
                return str(artifact_path)

        logger.warning(f"Artifact not found: {artifact_id}")
        return None

    def get_metadata(self, artifact_id: str) -> Optional[Dict]:
        """Retrieve artifact metadata.

        Args:
            artifact_id: Artifact identifier

        Returns:
            Metadata dict, or None if not found
        """
        # Check both directories
        for directory in [self.upload_dir, self.web_dir]:
            meta_file = directory / f"{artifact_id}.meta.json"
            if meta_file.exists():
                with meta_file.open("r") as f:
                    return json.load(f)

        return None

    def delete_artifact(self, artifact_id: str):
        """Delete artifact and metadata.

        Args:
            artifact_id: Artifact identifier
        """
        deleted = False

        # Delete from uploads
        for ext in [".pdf", ".docx", ".md", ".txt", ".meta.json"]:
            file_path = self.upload_dir / f"{artifact_id}{ext}"
            if file_path.exists():
                file_path.unlink()
                deleted = True

        # Delete from web
        for ext in [".html", ".txt", ".meta.json"]:
            file_path = self.web_dir / f"{artifact_id}{ext}"
            if file_path.exists():
                file_path.unlink()
                deleted = True

        if deleted:
            logger.info(f"Deleted artifact: {artifact_id}")
        else:
            logger.warning(f"No files found to delete for: {artifact_id}")


# Singleton instance
_artifact_store: Optional[ArtifactStore] = None


def get_artifact_store() -> ArtifactStore:
    """Get or create the artifact store singleton."""
    global _artifact_store
    if _artifact_store is None:
        _artifact_store = ArtifactStore()
    return _artifact_store


def reset_artifact_store() -> None:
    """Reset the artifact store singleton (for testing)."""
    global _artifact_store
    _artifact_store = None
