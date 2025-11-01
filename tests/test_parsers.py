"""Test document parsers for PDF, DOCX, and Markdown."""

import pytest
from pathlib import Path

# Test fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_parse_pdf_extracts_text():
    """Test that PDF parser extracts text from all pages."""
    from ingestion.parsers import parse_pdf

    pdf_path = FIXTURES_DIR / "sample.pdf"
    text = parse_pdf(str(pdf_path))

    assert isinstance(text, str)
    assert len(text) > 0
    assert "sample" in text.lower() or "test" in text.lower()


def test_parse_pdf_handles_empty_pages():
    """Test that PDF parser handles documents with empty pages."""
    from ingestion.parsers import parse_pdf

    pdf_path = FIXTURES_DIR / "empty.pdf"
    text = parse_pdf(str(pdf_path))

    # Should return empty string, not crash
    assert isinstance(text, str)


def test_parse_docx_extracts_paragraphs():
    """Test that DOCX parser extracts paragraph text."""
    from ingestion.parsers import parse_docx

    docx_path = FIXTURES_DIR / "sample.docx"
    text = parse_docx(str(docx_path))

    assert isinstance(text, str)
    assert len(text) > 0
    assert "sample" in text.lower() or "test" in text.lower()


def test_parse_markdown_strips_formatting():
    """Test that Markdown parser converts to plain text."""
    from ingestion.parsers import parse_markdown

    md_path = FIXTURES_DIR / "sample.md"
    text = parse_markdown(str(md_path))

    assert isinstance(text, str)
    assert len(text) > 0
    # Content should be present
    assert "sample" in text.lower() or "markdown" in text.lower()


def test_parse_markdown_preserves_content():
    """Test that Markdown parser preserves actual content."""
    from ingestion.parsers import parse_markdown

    md_content = "# Title\n\nThis is **bold** and *italic* text."
    md_path = FIXTURES_DIR / "test_preserve.md"

    # Create temp file
    md_path.parent.mkdir(exist_ok=True)
    md_path.write_text(md_content)

    text = parse_markdown(str(md_path))
    assert "Title" in text
    assert "bold" in text
    assert "italic" in text

    # Cleanup
    md_path.unlink()


def test_parse_file_dispatches_by_extension():
    """Test that parse_file uses correct parser based on extension."""
    from ingestion.parsers import parse_file

    # Test PDF
    pdf_path = FIXTURES_DIR / "sample.pdf"
    pdf_text = parse_file(str(pdf_path))
    assert isinstance(pdf_text, str)
    assert len(pdf_text) > 0

    # Test DOCX
    docx_path = FIXTURES_DIR / "sample.docx"
    docx_text = parse_file(str(docx_path))
    assert isinstance(docx_text, str)
    assert len(docx_text) > 0

    # Test Markdown
    md_path = FIXTURES_DIR / "sample.md"
    md_text = parse_file(str(md_path))
    assert isinstance(md_text, str)
    assert len(md_text) > 0


def test_parse_file_rejects_unsupported_type():
    """Test that parse_file raises error for unsupported file types."""
    from ingestion.parsers import parse_file

    with pytest.raises(ValueError, match="Unsupported file type"):
        parse_file("/fake/file.exe")


def test_parse_nonexistent_file_raises_error():
    """Test that missing file raises FileNotFoundError."""
    from ingestion.parsers import parse_pdf

    with pytest.raises(FileNotFoundError):
        parse_pdf("/nonexistent/file.pdf")


def test_parsers_normalize_whitespace():
    """Test that parsers normalize excessive whitespace."""
    from ingestion.parsers import normalize_whitespace

    text_with_spaces = "Hello    world  \n\n\n\n  Multiple   spaces"
    normalized = normalize_whitespace(text_with_spaces)

    # Multiple spaces reduced to single
    assert "    " not in normalized
    # Excessive newlines reduced
    assert "\n\n\n" not in normalized
    # Content preserved
    assert "Hello" in normalized
    assert "world" in normalized
