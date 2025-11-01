# Task 05 – Parse and chunk uploaded documents

**Phase:** Document Ingestion & Indexing

**Description:**

Implement parsing logic for PDF, Word (DOCX) and Markdown files to extract raw text.  Use libraries such as `pdfplumber` for PDFs, `python-docx` for DOCX files and Python’s `markdown` or `markdown2` package for Markdown.  Normalize whitespace and encoding, then split the text into passages (e.g., using a recursive character splitter or token‑based chunker) suitable for embedding.  Ensure that each chunk carries metadata linking it back to its source file, position and paragraph index.

**Acceptance Criteria:**

* For each supported file type, the parser extracts text without crashing on typical documents.
* The chunking logic produces passages of an appropriate size (e.g., 500–1 500 tokens) with overlap to preserve context.
* Each chunk includes metadata: document identifier, original filename, page number (for PDFs) or section indicator.
* Unit tests cover parsing and chunking across file types and edge cases (empty documents, non‑standard encodings).
