# Acceptance Test for Task 05 – Parse and chunk uploaded documents

**Objective:** Verify that document parsing and chunking works for PDFs, DOCX files and Markdown files.

**Test Steps:**

1. Provide sample documents in PDF, DOCX and Markdown formats.
2. Call the parsing functions for each type and ensure that the returned text is not empty.
3. Pass the extracted text to the chunking function and verify that it returns a list of chunks.
4. Check that each chunk contains text and metadata (including `chunk_index`).
5. For extremely short documents, ensure that the chunker returns a single chunk.

**Expected Result:**

* Parsing functions extract text without raising exceptions.
* Chunking produces a non‑empty list of chunks with correct sizes and metadata.
* Edge cases (empty files) are handled gracefully.
