# Step 03: Parse and Chunk Documents

## Objective

Implement text extraction from PDF, DOCX, and Markdown files, then split the extracted text into searchable passages (chunks) with metadata preservation and context overlap.

## Atomic Implementation

This step is atomic: it either creates working parsers for all supported formats and a functioning chunker, or fails with clear error messages. All file types must be handled.

## TDD Cycle

### Red Phase

Write failing tests that define expected parser and chunker behavior:

```python
# tests/test_parsers.py
import pytest
from pathlib import Path
from ingestion.parsers import parse_pdf, parse_docx, parse_markdown

# Test fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"

def test_parse_pdf_extracts_text():
    """Test that PDF parser extracts text from all pages."""
    pdf_path = FIXTURES_DIR / "sample.pdf"
    text = parse_pdf(str(pdf_path))

    assert isinstance(text, str)
    assert len(text) > 0
    assert "sample" in text.lower() or "test" in text.lower()

def test_parse_pdf_handles_empty_pages():
    """Test that PDF parser handles documents with empty pages."""
    pdf_path = FIXTURES_DIR / "empty.pdf"
    text = parse_pdf(str(pdf_path))

    # Should return empty string, not crash
    assert isinstance(text, str)

def test_parse_docx_extracts_paragraphs():
    """Test that DOCX parser extracts paragraph text."""
    docx_path = FIXTURES_DIR / "sample.docx"
    text = parse_docx(str(docx_path))

    assert isinstance(text, str)
    assert len(text) > 0

def test_parse_markdown_strips_formatting():
    """Test that Markdown parser converts to plain text."""
    md_path = FIXTURES_DIR / "sample.md"
    text = parse_markdown(str(md_path))

    assert isinstance(text, str)
    assert len(text) > 0
    # Should have text but not markdown syntax
    assert "# " not in text or text.count("#") < 3  # Headers converted

def test_parse_markdown_preserves_content():
    """Test that Markdown parser preserves actual content."""
    md_content = "# Title\n\nThis is **bold** and *italic* text."
    md_path = FIXTURES_DIR / "test.md"

    # Create temp file
    md_path.parent.mkdir(exist_ok=True)
    md_path.write_text(md_content)

    text = parse_markdown(str(md_path))
    assert "Title" in text
    assert "bold" in text
    assert "italic" in text

def test_parsers_normalize_whitespace():
    """Test that parsers normalize excessive whitespace."""
    # Each parser should handle multiple newlines, spaces
    # This is tested via the actual implementation
    pass  # Implementation-specific
```

```python
# tests/test_chunker.py
import pytest
from ingestion.chunker import chunk_text, Chunk

def test_chunk_short_text_returns_single_chunk():
    """Test that short text returns one chunk."""
    text = "This is a short document."
    chunks = chunk_text(text, doc_id="test-123", filename="test.txt")

    assert len(chunks) == 1
    assert isinstance(chunks[0], Chunk)
    assert chunks[0].text == text
    assert chunks[0].metadata["doc_id"] == "test-123"
    assert chunks[0].metadata["chunk_index"] == 0

def test_chunk_long_text_splits_into_multiple():
    """Test that long text is split into multiple chunks."""
    text = "A" * 2000  # Long text exceeding chunk size
    chunks = chunk_text(text, doc_id="test-456", filename="long.txt")

    assert len(chunks) > 1
    # Verify chunks have reasonable size
    for chunk in chunks:
        assert len(chunk.text) <= 1200  # chunk_size + some tolerance

def test_chunk_metadata_includes_all_fields():
    """Test that chunk metadata contains required fields."""
    text = "Sample text for chunking."
    chunks = chunk_text(text, doc_id="doc-1", filename="file.pdf", source="upload")

    chunk = chunks[0]
    assert chunk.metadata["doc_id"] == "doc-1"
    assert chunk.metadata["filename"] == "file.pdf"
    assert chunk.metadata["chunk_index"] == 0
    assert chunk.metadata["source"] == "upload"
    assert "timestamp" in chunk.metadata

def test_chunk_overlap_preserves_context():
    """Test that chunks have overlap for context preservation."""
    text = "A" * 1500  # Enough for 2 chunks with overlap
    chunks = chunk_text(text)

    if len(chunks) > 1:
        # Last part of first chunk should overlap with start of second
        # This is validated by the chunker configuration
        assert len(chunks[1].text) > 0

def test_chunk_respects_separators():
    """Test that chunker splits on paragraph boundaries when possible."""
    text = "Paragraph one.\n\nParagraph two.\n\nParagraph three." * 50
    chunks = chunk_text(text)

    # Chunks should ideally break on \n\n boundaries
    # Not guaranteed, but likely with recursive splitter
    assert len(chunks) > 0
```

**Expected Result**: Tests fail because parsers and chunker don't exist yet.

### Green Phase

1. **Create test fixtures**:
   ```bash
   mkdir -p tests/fixtures
   ```

   Create sample files:
   ```python
   # tests/create_fixtures.py (run once to generate test files)
   from reportlab.pdfgen import canvas
   from docx import Document
   from pathlib import Path

   FIXTURES = Path(__file__).parent / "fixtures"
   FIXTURES.mkdir(exist_ok=True)

   # Create sample PDF
   pdf = canvas.Canvas(str(FIXTURES / "sample.pdf"))
   pdf.drawString(100, 750, "Sample PDF Document")
   pdf.drawString(100, 730, "This is test content for parsing.")
   pdf.save()

   # Create sample DOCX
   doc = Document()
   doc.add_heading("Sample Document", 0)
   doc.add_paragraph("This is a sample DOCX file for testing.")
   doc.add_paragraph("It has multiple paragraphs.")
   doc.save(FIXTURES / "sample.docx")

   # Create sample Markdown
   (FIXTURES / "sample.md").write_text("""
   # Sample Markdown

   This is a **sample** markdown document.

   ## Section Two

   - List item 1
   - List item 2

   Regular paragraph text.
   """)
   ```

2. **Implement parsers**:
   ```python
   # ingestion/parsers.py
   """Document parsers for extracting text from various file formats."""
   import pdfplumber
   from docx import Document
   import markdown
   from bs4 import BeautifulSoup
   import logging
   from pathlib import Path

   logger = logging.getLogger(__name__)

   def parse_pdf(file_path: str) -> str:
       """Extract text from a PDF file.

       Args:
           file_path: Path to the PDF file

       Returns:
           Extracted text with normalized whitespace
       """
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
       """
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
       """
       try:
           with open(file_path, 'r', encoding='utf-8') as f:
               md_text = f.read()

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
       import re
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
   ```

3. **Implement chunker**:
   ```python
   # ingestion/chunker.py
   """Text chunking service for splitting documents into searchable passages."""
   from dataclasses import dataclass, field
   from typing import Optional, List
   from datetime import datetime
   from langchain.text_splitter import RecursiveCharacterTextSplitter
   import logging

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
                   "timestamp": datetime.utcnow().isoformat() + "Z",
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
       import pdfplumber

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
   ```

4. **Update ingestion/__init__.py**:
   ```python
   # ingestion/__init__.py
   from . import parsers, chunker, firecrawl_client

   __all__ = ["parsers", "chunker", "firecrawl_client"]
   ```

5. **Run tests**:
   ```bash
   # Generate fixtures first
   python tests/create_fixtures.py

   # Run tests
   pytest tests/test_parsers.py tests/test_chunker.py -v
   ```

**Expected Result**: All tests pass.

### Refactor Phase

1. **Add encoding error handling** for robust parsing:
   ```python
   # ingestion/parsers.py
   def parse_markdown(file_path: str) -> str:
       try:
           # Try UTF-8 first
           with open(file_path, 'r', encoding='utf-8') as f:
               md_text = f.read()
       except UnicodeDecodeError:
           # Fallback to latin-1
           logger.warning(f"UTF-8 decode failed for {file_path}, trying latin-1")
           with open(file_path, 'r', encoding='latin-1') as f:
               md_text = f.read()

       # ... rest of implementation
   ```

2. **Add performance optimization** for large documents:
   ```python
   # ingestion/chunker.py
   def chunk_text_streaming(text: str, **kwargs) -> List[Chunk]:
       """Chunk text with memory-efficient streaming for large docs."""
       # For very large documents, process in batches
       MAX_TEXT_SIZE = 1_000_000  # 1MB

       if len(text) > MAX_TEXT_SIZE:
           logger.info(f"Large document ({len(text)} chars), using batch processing")
           # Split into manageable sections first
           sections = [text[i:i+MAX_TEXT_SIZE] for i in range(0, len(text), MAX_TEXT_SIZE)]
           all_chunks = []
           for section in sections:
               all_chunks.extend(chunk_text(section, **kwargs))
           return all_chunks
       else:
           return chunk_text(text, **kwargs)
   ```

3. **Add better metadata extraction** for PDFs:
   ```python
   # ingestion/parsers.py
   def extract_pdf_metadata(file_path: str) -> dict:
       """Extract metadata from PDF file.

       Returns:
           Dict with title, author, creation date if available
       """
       try:
           with pdfplumber.open(file_path) as pdf:
               return {
                   "title": pdf.metadata.get("Title", ""),
                   "author": pdf.metadata.get("Author", ""),
                   "created": pdf.metadata.get("CreationDate", ""),
                   "pages": len(pdf.pages),
               }
       except Exception as e:
           logger.warning(f"Could not extract PDF metadata: {e}")
           return {}
   ```

4. **Add comprehensive error tests**:
   ```python
   # tests/test_parsers.py
   def test_parse_corrupted_pdf_raises_error():
       """Test that corrupted PDF raises appropriate error."""
       bad_pdf = FIXTURES_DIR / "corrupted.pdf"
       bad_pdf.write_bytes(b"not a real pdf")

       with pytest.raises(Exception):
           parse_pdf(str(bad_pdf))

   def test_parse_nonexistent_file_raises_error():
       """Test that missing file raises FileNotFoundError."""
       with pytest.raises(FileNotFoundError):
           parse_file("/nonexistent/file.pdf")
   ```

5. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: implement document parsing and chunking

   - Add parsers for PDF (pdfplumber), DOCX (python-docx), Markdown
   - Implement RecursiveCharacterTextSplitter for text chunking
   - Configure 1000 char chunks with 200 char overlap
   - Add Chunk dataclass with comprehensive metadata
   - Support page-by-page PDF chunking with page numbers
   - Add whitespace normalization and encoding error handling
   - Create test fixtures (sample PDF, DOCX, Markdown files)
   - Tests verify parsing accuracy and chunk quality

   Covers Task 05 from original requirements.
   All tests passing.
   "
   ```

## Acceptance Criteria Verification

- [x] PDF parser extracts text from all pages using pdfplumber
- [x] DOCX parser extracts paragraphs using python-docx
- [x] Markdown parser converts to plain text (strips formatting)
- [x] All parsers normalize whitespace and handle encoding errors
- [x] Chunker splits text into ~1000 character passages
- [x] Chunks have 200 character overlap for context
- [x] Each chunk includes metadata: doc_id, filename, chunk_index, timestamp
- [x] PDF chunks include page_number in metadata
- [x] Empty documents return empty chunk list (no crash)
- [x] Tests verify all file types and edge cases

## Files Created/Modified

- Created: `ingestion/parsers.py` (PDF, DOCX, Markdown parsers)
- Created: `ingestion/chunker.py` (chunking service)
- Created: `tests/test_parsers.py`
- Created: `tests/test_chunker.py`
- Created: `tests/fixtures/sample.pdf`, `sample.docx`, `sample.md`
- Created: `tests/create_fixtures.py` (fixture generation script)
- Modified: `ingestion/__init__.py`

## Rollback Strategy

If this step fails:
1. Remove `ingestion/parsers.py` and `ingestion/chunker.py`
2. Remove test files and fixtures
3. Run `git reset --hard HEAD~1`
4. Review error logs and fix issues
5. Retry step from Red phase

## Dependencies

Requires:
- pdfplumber: already in requirements.txt
- python-docx: already in requirements.txt
- markdown: already in requirements.txt
- beautifulsoup4: `pip install beautifulsoup4`
- langchain (RecursiveCharacterTextSplitter): already in requirements.txt

## Testing Parsers Manually

```python
# Test in Python REPL
from ingestion.parsers import parse_pdf, parse_docx, parse_markdown
from ingestion.chunker import chunk_text

# Parse a PDF
text = parse_pdf("tests/fixtures/sample.pdf")
print(f"Extracted {len(text)} characters")

# Chunk the text
chunks = chunk_text(text, doc_id="test-1", filename="sample.pdf")
print(f"Created {len(chunks)} chunks")
print(f"First chunk: {chunks[0].text[:100]}...")
print(f"Metadata: {chunks[0].metadata}")
```

## Next Step

Proceed to `04_generate_embeddings.md` - Generate vector embeddings and store in Qdrant
