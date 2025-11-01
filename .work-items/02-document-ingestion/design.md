# Design: Document Ingestion

## Objective

Enable ingestion of documents from multiple sources (file uploads and URLs) with automated parsing, chunking, embedding generation, and persistent storage. This feature transforms raw content into searchable vector representations while preserving original artifacts.

## Technical Design

### System Architecture

The document ingestion pipeline consists of five sequential stages:

1. **Input Reception** - REST API endpoints for file uploads and URL submissions
2. **Parsing** - Format-specific text extraction (PDF, DOCX, Markdown, HTML)
3. **Chunking** - Text segmentation with overlap for context preservation
4. **Embedding** - Vector representation generation using sentence transformers
5. **Storage** - Dual persistence (vectors in Qdrant, artifacts in filesystem)

### Data Flow

```
User Upload → Validation → Parser → Chunker → Embedder → Storage
                ↓                                            ↓
           Error Response                          Qdrant + Artifacts
```

## Key Components

### 2.1 API Endpoints

**POST /upload/file**
- Accepts: multipart/form-data
- Supported MIME types:
  - `application/pdf`
  - `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
  - `text/markdown`
- Returns: `{"status": "accepted", "ingestion_id": "<uuid>"}`
- Error codes: 400 (unsupported type), 413 (file too large), 500 (processing error)

**POST /upload/link**
- Accepts: JSON `{"url": "https://..."}`
- Validation: Pydantic HttpUrl type
- Returns: `{"status": "accepted", "ingestion_id": "<uuid>"}`
- Error codes: 422 (invalid URL), 500 (fetch error)

### 2.2 Data Models

**Document Schema**:
```python
class Document:
    id: str                    # UUID
    filename: str              # Original name or URL
    source: Literal["upload", "web"]
    upload_time: datetime
    mime_type: str
    file_size: int             # bytes
    artifact_path: str         # filesystem location
    vector_ids: list[str]      # Qdrant point IDs
```

**Chunk Schema**:
```python
class Chunk:
    text: str                  # Chunk content
    metadata: dict = {
        "doc_id": str,
        "filename": str,
        "chunk_index": int,
        "page_number": int,    # PDFs only
        "source": str,         # "upload" or URL
        "timestamp": str
    }
```

**Qdrant Point**:
```python
{
    "id": "<uuid>",
    "vector": [float] * 384,   # MiniLM embedding dimension
    "payload": {
        "text": str,
        "doc_id": str,
        "filename": str,
        "chunk_index": int,
        "page_number": int | None,
        "source": str,
        "timestamp": str
    }
}
```

### 2.3 Component Responsibilities

**FileParser** (`ingestion/parsers.py`):
- Methods: `parse_pdf()`, `parse_docx()`, `parse_markdown()`
- Libraries: pdfplumber, python-docx, markdown + BeautifulSoup
- Output: Raw text string with normalized whitespace

**ChunkingService** (`ingestion/chunker.py`):
- Strategy: RecursiveCharacterTextSplitter
- Configuration:
  - `chunk_size=1000` characters
  - `chunk_overlap=200` characters
  - `separators=["\n\n", "\n", " "]`
- Output: List of Chunk objects with metadata

**EmbeddingService** (`ingestion/embeddings.py`):
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Dimension: 384
- Batch size: 100 (for memory efficiency)
- Output: List of 384-dimensional vectors

**VectorStore** (`ingestion/vector_store.py`):
- Backend: Qdrant
- Collection: `kb_passages`
- Distance metric: Cosine similarity
- Operations: `create_collection()`, `upsert_vectors()`, `search()`

**ArtifactStore** (`ingestion/artifacts.py`):
- Directory structure:
  ```
  artifacts/
  ├── uploads/          # User-uploaded files
  │   ├── {id}_{filename}
  │   └── {id}.meta.json
  └── web/              # Fetched web pages
      ├── {id}.html
      ├── {id}.txt      # Extracted text
      └── {id}.meta.json
  ```
- Operations: `save_upload()`, `save_web_page()`, `get_artifact()`

**IngestionPipeline** (`ingestion/pipeline.py`):
- Orchestrates: Parser → Chunker → Embedder → Storage
- Background execution via FastAPI BackgroundTasks
- Error handling with rollback on failure
- Logging for monitoring and debugging

### 2.4 External Services

**Firecrawl Integration**:
- Purpose: Web page content extraction
- API: `https://firecrawl.dev/api/extract?url={url}`
- Authentication: `X-API-Key` header
- Timeout: 30 seconds
- Fallback: Log error, return empty content

**Qdrant Configuration**:
- Local development: `http://localhost:6333`
- Production: Qdrant Cloud with API key
- Collection schema: 384-dimensional vectors, cosine distance
- Persistence: Enabled for durability

## Technical Constraints

### File Size Limits
- Maximum upload: 10MB (configurable via FastAPI)
- Reason: Prevent memory exhaustion during parsing

### Processing Time
- File upload: Asynchronous (non-blocking)
- URL fetch: 30-second timeout
- Embedding batch: 100 chunks (prevent OOM)

### Storage Requirements
- Qdrant: ~4KB per chunk (vector + metadata)
- Artifacts: Original file size + ~1KB metadata
- Estimate: 1000 documents × 50 chunks × 4KB = 200MB Qdrant storage

## Alternatives Considered

1. **Synchronous vs Asynchronous Processing**:
   - Chose: Asynchronous via FastAPI BackgroundTasks
   - Reason: Prevents request timeout for large documents
   - Trade-off: Requires status endpoint (future work)

2. **Chunk Size**:
   - Considered: 256, 512, 1000, 1500 characters
   - Chose: 1000 characters
   - Reason: Balance between context preservation and granularity

3. **Embedding Model**:
   - Considered: OpenAI ada-002, Cohere, local models
   - Chose: sentence-transformers/all-MiniLM-L6-v2
   - Reason: Free, fast, good quality, runs locally

4. **Vector Database**:
   - Considered: Pinecone, Weaviate, Chroma, Qdrant
   - Chose: Qdrant
   - Reason: Open-source, good Python support, local + cloud options

5. **Artifact Storage**:
   - Considered: S3, Firebase Storage, local filesystem
   - Chose: Local filesystem (with cloud migration path)
   - Reason: Simplicity for MVP, easy to migrate later

## Out of Scope

- Batch upload of multiple files
- Progress tracking for ingestion status
- OCR for scanned PDFs
- Image extraction and indexing
- Document deduplication
- Custom chunking strategies (user-configurable)
- Vector index optimization (HNSW parameters)
- Artifact compression or encryption

## Dependencies

- Feature F01: Project Setup (environment, dependencies, config)
- Qdrant instance running on localhost:6333 or cloud
- Firecrawl API key (for URL ingestion)

## Security Considerations

1. **File Upload Validation**:
   - Validate MIME type via content inspection (not just extension)
   - Sanitize filenames to prevent directory traversal
   - Limit file size to prevent DoS

2. **URL Ingestion**:
   - Validate URL format with Pydantic HttpUrl
   - Block private IP ranges (127.0.0.1, 192.168.x.x, etc.)
   - Use Firecrawl API (prevents SSRF attacks)

3. **Artifact Storage**:
   - Store in dedicated directory with restricted permissions
   - Generate UUIDs (prevent filename collisions/overwrites)
   - Log all access for audit trail

## Future Enhancements

- Task 08: Implement ingestion status endpoint
- Task 24: Implement artifact download endpoint
- Webhook notifications on ingestion completion
- Support for additional formats (HTML, CSV, JSON)
- Incremental re-indexing on document updates
- Metadata extraction (author, title, creation date)
