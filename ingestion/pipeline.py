"""End-to-end document ingestion pipeline."""

import logging
import uuid
from typing import Any, Dict

from ingestion.artifacts import get_artifact_store
from ingestion.chunker import chunk_text
from ingestion.parsers import parse_file
from ingestion.vector_store import get_vector_store

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Orchestrates document ingestion from parsing to storage."""

    def __init__(self):
        """Initialize the ingestion pipeline."""
        self.vector_store = get_vector_store()
        self.artifact_store = get_artifact_store()

    def ingest_file(
        self,
        file_path: str,
        filename: str
    ) -> Dict[str, Any]:
        """Ingest a file through the complete pipeline.

        Args:
            file_path: Path to the file to ingest
            filename: Original filename

        Returns:
            Dict with doc_id, artifact_id, chunks_created, status

        Raises:
            Exception: If any step fails
        """
        doc_id = str(uuid.uuid4())
        logger.info(f"[1/4] Starting ingestion for {filename} (doc_id: {doc_id})")

        try:
            # Step 1: Parse document
            logger.info(f"[2/4] Parsing {filename}")
            text = parse_file(file_path)

            if not text or len(text.strip()) < 10:
                raise ValueError(f"Insufficient content extracted from {filename}")

            # Step 2: Chunk text
            logger.info(f"[3/4] Chunking text ({len(text)} chars)")
            chunks = chunk_text(
                text,
                doc_id=doc_id,
                filename=filename,
                source="upload"
            )

            if not chunks:
                raise ValueError(f"No chunks created from {filename}")

            # Step 3: Generate embeddings and store in Qdrant
            logger.info(f"[4/4] Storing {len(chunks)} chunks in vector store")
            upsert_result = self.vector_store.upsert_chunks(chunks)

            # Extract vector IDs from the upsert result
            # For now, generate placeholder IDs since we need to track them
            vector_ids = [f"vec_{doc_id}_{i}" for i in range(len(chunks))]

            # Step 4: Save original artifact
            logger.info(f"Saving artifact for {filename}")
            artifact_id = self.artifact_store.save_upload(
                file_path=file_path,
                original_name=filename,
                doc_id=doc_id,
                vector_ids=vector_ids
            )

            result = {
                "doc_id": doc_id,
                "artifact_id": artifact_id,
                "chunks_created": len(chunks),
                "status": "success"
            }

            logger.info(
                f"Ingestion complete for {filename}: "
                f"{len(chunks)} chunks, artifact {artifact_id}"
            )
            return result

        except Exception as e:
            logger.error(f"Ingestion failed for {filename}: {e}")
            # Rollback: delete from vector store if doc_id exists
            try:
                self.vector_store.delete_by_doc_id(doc_id)
                logger.info(f"Rolled back vector store entries for {doc_id}")
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {rollback_error}")

            raise

    def ingest_url(self, url: str, text_content: str) -> Dict[str, Any]:
        """Ingest content from a URL.

        Args:
            url: URL that was fetched
            text_content: Extracted text content

        Returns:
            Dict with doc_id, artifact_id, chunks_created, status
        """
        doc_id = f"web_{uuid.uuid4()}"
        logger.info(f"Starting URL ingestion for {url} (doc_id: {doc_id})")

        try:
            # Validate content
            if not text_content or len(text_content.strip()) < 10:
                raise ValueError(f"Insufficient content from {url}")

            # Step 1: Chunk text
            logger.info(f"Chunking text ({len(text_content)} chars)")
            chunks = chunk_text(
                text_content,
                doc_id=doc_id,
                filename=url,
                source=url
            )

            if not chunks:
                raise ValueError(f"No chunks created from {url}")

            # Step 2: Store in vector database
            logger.info(f"Storing {len(chunks)} chunks in vector store")
            self.vector_store.upsert_chunks(chunks)

            # Generate vector IDs
            vector_ids = [f"vec_{doc_id}_{i}" for i in range(len(chunks))]

            # Step 3: Save as web artifact
            artifact_id = self.artifact_store.save_web_page(
                url=url,
                html_content="",  # HTML not available in current implementation
                text_content=text_content,
                doc_id=doc_id,
                vector_ids=vector_ids
            )

            result = {
                "doc_id": doc_id,
                "artifact_id": artifact_id,
                "chunks_created": len(chunks),
                "status": "success"
            }

            logger.info(f"URL ingestion complete: {len(chunks)} chunks")
            return result

        except Exception as e:
            logger.error(f"URL ingestion failed for {url}: {e}")
            # Rollback
            try:
                self.vector_store.delete_by_doc_id(doc_id)
                logger.info(f"Rolled back vector store entries for {doc_id}")
            except Exception:
                pass
            raise


def get_pipeline() -> IngestionPipeline:
    """Get or create pipeline singleton."""
    # For simplicity, create new instance each time
    # Could be converted to singleton if needed
    return IngestionPipeline()
