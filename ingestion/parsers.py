"""Document parsers for extracting text from various file formats."""

import logging
import re
from pathlib import Path
from typing import Dict

import pdfplumber
from docx import Document
import markdown
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def parse_pdf(file_path: str) -> str:
    """Extract text from a PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        Extracted text with normalized whitespace

    Raises:
        FileNotFoundError: If file doesn't exist
        Exception: If PDF parsing fails
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    text_chunks = []

    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_chunks.append(page_text)
                else:
                    logger.warning(f"No text on page {page_num} of {file_path}")

    except Exception as e:
        logger.error(f"Error parsing PDF {file_path}: {e}")
        raise

    text = "\n".join(text_chunks)
    return normalize_whitespace(text)


def parse_docx(file_path: str) -> str:
    """Extract text from a DOCX file.

    Args:
        file_path: Path to the DOCX file

    Returns:
        Extracted text from all paragraphs

    Raises:
        FileNotFoundError: If file doesn't exist
        Exception: If DOCX parsing fails
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"DOCX file not found: {file_path}")

    try:
        doc = Document(file_path)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        text = "\n\n".join(paragraphs)
        return normalize_whitespace(text)

    except Exception as e:
        logger.error(f"Error parsing DOCX {file_path}: {e}")
        raise


def parse_markdown(file_path: str) -> str:
    """Extract plain text from a Markdown file.

    Args:
        file_path: Path to the Markdown file

    Returns:
        Plain text with markdown formatting removed

    Raises:
        FileNotFoundError: If file doesn't exist
        Exception: If Markdown parsing fails
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    try:
        # Try UTF-8 first
        with open(file_path, 'r', encoding='utf-8') as f:
            md_text = f.read()
    except UnicodeDecodeError:
        # Fallback to latin-1
        logger.warning(f"UTF-8 decode failed for {file_path}, trying latin-1")
        with open(file_path, 'r', encoding='latin-1') as f:
            md_text = f.read()

    try:
        # Convert markdown to HTML
        html = markdown.markdown(md_text)

        # Strip HTML tags to get plain text
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n")

        return normalize_whitespace(text)

    except Exception as e:
        logger.error(f"Error parsing Markdown {file_path}: {e}")
        raise


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text.

    Args:
        text: Input text with potentially irregular whitespace

    Returns:
        Text with normalized spaces and newlines
    """
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)

    # Replace more than 2 newlines with 2 newlines
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def parse_file(file_path: str) -> str:
    """Parse a file based on its extension.

    Args:
        file_path: Path to the file to parse

    Returns:
        Extracted text content

    Raises:
        ValueError: If file type is not supported
        FileNotFoundError: If file doesn't exist
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    parsers = {
        '.pdf': parse_pdf,
        '.docx': parse_docx,
        '.md': parse_markdown,
        '.markdown': parse_markdown,
    }

    if suffix not in parsers:
        raise ValueError(f"Unsupported file type: {suffix}")

    return parsers[suffix](file_path)


def extract_pdf_metadata(file_path: str) -> Dict[str, str]:
    """Extract metadata from PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        Dict with title, author, creation date if available
    """
    try:
        with pdfplumber.open(file_path) as pdf:
            metadata = pdf.metadata or {}
            return {
                "title": metadata.get("Title", ""),
                "author": metadata.get("Author", ""),
                "created": metadata.get("CreationDate", ""),
                "pages": len(pdf.pages),
            }
    except Exception as e:
        logger.warning(f"Could not extract PDF metadata: {e}")
        return {}
