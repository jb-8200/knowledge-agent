# Task Breakdown: Document Ingestion

## Overview

Implement a complete document ingestion pipeline that accepts files and URLs, extracts and chunks text, generates vector embeddings, and persists both vectors and original artifacts for future retrieval.

## Requirements Traceability

- Links to: `user-story.md` - Research Analyst needs searchable knowledge base
- Links to: `design.md` - Technical architecture and component design
- Original tasks: Task 03 (file upload), Task 04 (URL ingestion), Task 05 (parsing/chunking), Task 06 (embeddings), Task 07 (artifacts)

## Test Strategy

- **Unit Tests**:
  - Parser functions for each file type (PDF, DOCX, Markdown)
  - Chunking logic with various text lengths
  - Embedding generation and dimension validation
  - Artifact storage and retrieval

- **Integration Tests**:
  - End-to-end file upload to vector storage
  - URL ingestion with mocked Firecrawl
  - Pipeline error handling and rollback

- **Acceptance Tests**:
  - Upload real documents and verify searchability
  - Test vector similarity search returns relevant chunks
  - Validate artifact metadata completeness

## Sequential Steps (TDD Approach)

Each step follows Red → Green → Refactor cycle:

### 01 - Implement File Upload Endpoint

**Objective**: Create POST /upload/file endpoint that validates and accepts document uploads

**Acceptance Criteria**:
- Endpoint accepts PDF, DOCX, and Markdown files
- Invalid file types return 400 error with clear message
- Valid uploads return ingestion_id
- Background task queues file for processing
- Test: Mock upload verifies ingestion pipeline invocation

**TDD Cycle**:
1. **Red**: Write test expecting /upload/file to exist and validate file types
2. **Green**: Implement endpoint with validation, temp storage, background tasks
3. **Refactor**: Extract validation logic, add proper error handling

**Files Modified**:
- Create: `app/routes/upload.py`
- Create: `tests/test_upload_endpoint.py`
- Modify: `app/__init__.py` or `app/main.py` (FastAPI app)

**Estimated Time**: 2-3 hours

---

### 02 - Implement Link Ingestion Endpoint

**Objective**: Create POST /upload/link endpoint that fetches and processes web content

**Acceptance Criteria**:
- Endpoint validates URL format using Pydantic
- Valid URLs trigger Firecrawl fetch in background
- Invalid URLs return 422 validation error
- Fetch errors are logged without crashing service
- Test: Mock Firecrawl and verify pipeline invocation

**TDD Cycle**:
1. **Red**: Write test expecting /upload/link with URL validation
2. **Green**: Implement endpoint with Firecrawl integration
3. **Refactor**: Extract Firecrawl client, add retry logic, improve error messages

**Files Modified**:
- Create: `ingestion/firecrawl_client.py`
- Modify: `app/routes/upload.py`
- Create: `tests/test_link_ingestion.py`

**Estimated Time**: 2-3 hours

---

### 03 - Parse and Chunk Documents

**Objective**: Extract text from supported formats and split into searchable passages

**Acceptance Criteria**:
- Parsers extract text from PDF, DOCX, Markdown without errors
- Chunker produces passages of ~1000 chars with 200 char overlap
- Each chunk includes metadata (doc_id, filename, chunk_index, page)
- Empty documents handled gracefully
- Test: Verify chunk count, size, and metadata completeness

**TDD Cycle**:
1. **Red**: Write tests expecting parsers and chunker to produce correct output
2. **Green**: Implement parsers using pdfplumber, python-docx, markdown/BeautifulSoup
3. **Refactor**: Normalize whitespace, handle encoding errors, optimize chunk boundaries

**Files Modified**:
- Create: `ingestion/parsers.py`
- Create: `ingestion/chunker.py`
- Create: `tests/test_parsers.py`
- Create: `tests/test_chunker.py`
- Create: `tests/fixtures/` (sample PDF, DOCX, MD files)

**Estimated Time**: 3-4 hours

---

### 04 - Generate Vector Embeddings

**Objective**: Convert text chunks to 384-dimensional vectors and store in Qdrant

**Acceptance Criteria**:
- Embeddings generated using all-MiniLM-L6-v2 model
- Each vector has dimension 384 with no NaNs
- Qdrant collection created with cosine distance metric
- Vectors and metadata upserted to Qdrant successfully
- Test: Similarity search retrieves correct chunk as top result

**TDD Cycle**:
1. **Red**: Write test expecting embedding function to return correct dimensions
2. **Green**: Implement embedding service and Qdrant integration
3. **Refactor**: Add batching for large document sets, connection pooling

**Files Modified**:
- Create: `ingestion/embeddings.py`
- Create: `ingestion/vector_store.py`
- Create: `tests/test_embeddings.py`
- Create: `tests/test_vector_store.py`

**Estimated Time**: 3-4 hours

---

### 05 - Persist Original Artifacts

**Objective**: Save uploaded files and web pages with metadata for future retrieval

**Acceptance Criteria**:
- Artifacts saved to `artifacts/uploads/` and `artifacts/web/` directories
- Each artifact has unique ID and associated metadata JSON
- Metadata includes filename, timestamp, MIME type, vector_ids
- Mapping exists between Qdrant points and artifact IDs
- Test: Save and retrieve artifact by ID

**TDD Cycle**:
1. **Red**: Write test expecting artifact save/retrieve to work
2. **Green**: Implement artifact storage with filesystem operations
3. **Refactor**: Add UUID generation, metadata validation, error handling

**Files Modified**:
- Create: `ingestion/artifacts.py`
- Create: `ingestion/pipeline.py` (orchestrate all steps)
- Create: `tests/test_artifacts.py`
- Create: `tests/test_pipeline.py`

**Estimated Time**: 2-3 hours

---

## Commit Strategy

Following "Tidy First" methodology:

**Commit 1** (Step 01):
- Add file upload endpoint with validation
- Implement background task queueing
- Tests for endpoint behavior

**Commit 2** (Step 02):
- Add URL ingestion endpoint
- Integrate Firecrawl client
- Tests with mocked external service

**Commit 3** (Step 03):
- Implement parsers for PDF, DOCX, Markdown
- Add chunking service with overlap
- Tests for all file types and edge cases

**Commit 4** (Step 04):
- Add embedding generation service
- Implement Qdrant vector store integration
- Tests for embedding quality and search

**Commit 5** (Step 05):
- Add artifact storage system
- Create end-to-end ingestion pipeline
- Integration tests for complete flow

## Dependencies

- Feature F01: Project Setup must be complete
- Qdrant must be running (docker run -p 6333:6333 qdrant/qdrant)
- Firecrawl API key configured in .env

## Blocks

- F03: Vector Search depends on this feature completing
- F04: RAG Q&A depends on searchable vector store

## Testing Prerequisites

Before starting, ensure:
1. Virtual environment is activated
2. All dependencies installed (pdfplumber, python-docx, markdown, sentence-transformers, qdrant-client)
3. Qdrant is running and accessible
4. Sample test files created (fixtures/sample.pdf, sample.docx, sample.md)
