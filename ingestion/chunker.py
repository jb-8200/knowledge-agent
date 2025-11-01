"""Text chunking service for splitting documents into searchable passages."""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """Represents a text chunk with metadata."""
    text: str
    metadata: dict = field(default_factory=dict)


# Chunker configuration
CHUNK_SIZE = 1000  # characters
CHUNK_OVERLAP = 200  # characters for context preservation
SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=SEPARATORS,
    length_function=len,
)


def chunk_text(
    text: str,
    doc_id: str = "unknown",
    filename: str = "unknown",
    source: str = "unknown",
    page_number: Optional[int] = None
) -> List[Chunk]:
    """Split text into chunks with metadata.

    Args:
        text: The text to chunk
        doc_id: Document identifier
        filename: Original filename or URL
        source: Source type ("upload" or URL)
        page_number: Optional page number for PDFs

    Returns:
        List of Chunk objects with text and metadata
    """
    if not text or not text.strip():
        logger.warning(f"Empty text provided for chunking: {filename}")
        return []

    try:
        # Split text into chunks
        text_chunks = _splitter.split_text(text)

        # Create Chunk objects with metadata
        chunks = []
        for idx, chunk_text in enumerate(text_chunks):
            metadata = {
                "doc_id": doc_id,
                "filename": filename,
                "chunk_index": idx,
                "source": source,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            if page_number is not None:
                metadata["page_number"] = page_number

            chunks.append(Chunk(text=chunk_text, metadata=metadata))

        logger.info(
            f"Chunked {len(text)} chars from {filename} into {len(chunks)} passages"
        )
        return chunks

    except Exception as e:
        logger.error(f"Error chunking text from {filename}: {e}")
        raise


def chunk_pdf_by_page(
    file_path: str,
    doc_id: str,
    filename: str
) -> List[Chunk]:
    """Chunk a PDF file page by page for better metadata.

    Args:
        file_path: Path to PDF file
        doc_id: Document identifier
        filename: Original filename

    Returns:
        List of chunks with page numbers in metadata
    """
    all_chunks = []

    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    chunks = chunk_text(
                        page_text,
                        doc_id=doc_id,
                        filename=filename,
                        source="upload",
                        page_number=page_num
                    )
                    all_chunks.extend(chunks)

        return all_chunks

    except Exception as e:
        logger.error(f"Error chunking PDF {file_path}: {e}")
        raise


def chunk_text_streaming(
    text: str,
    doc_id: str = "unknown",
    filename: str = "unknown",
    source: str = "unknown"
) -> List[Chunk]:
    """Chunk text with memory-efficient streaming for large docs.

    Args:
        text: The text to chunk
        doc_id: Document identifier
        filename: Original filename or URL
        source: Source type

    Returns:
        List of Chunk objects
    """
    # For very large documents, process in batches
    MAX_TEXT_SIZE = 1_000_000  # 1MB

    if len(text) > MAX_TEXT_SIZE:
        logger.info(f"Large document ({len(text)} chars), using batch processing")
        # Split into manageable sections first
        sections = [text[i:i+MAX_TEXT_SIZE] for i in range(0, len(text), MAX_TEXT_SIZE)]
        all_chunks = []
        for section_idx, section in enumerate(sections):
            section_chunks = chunk_text(
                section,
                doc_id=f"{doc_id}_section_{section_idx}",
                filename=filename,
                source=source
            )
            all_chunks.extend(section_chunks)
        return all_chunks
    else:
        return chunk_text(text, doc_id=doc_id, filename=filename, source=source)
