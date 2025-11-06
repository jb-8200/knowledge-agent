Quickly ingest a document or URL for testing the ingestion pipeline.

## Usage

### Ingest a file:
```
/ingest tests/fixtures/sample.pdf
```

### Ingest a URL:
```
/ingest https://example.com/article
```

### Ingest and show details:
```
/ingest tests/fixtures/sample.pdf verbose:true
```

## What This Does

1. **Validates input**: Checks if file exists or URL is valid
2. **Runs ingestion pipeline**: Parse → Chunk → Embed → Store
3. **Shows progress**: Displays each pipeline step
4. **Reports results**: Shows doc_id, chunks created, artifact saved
5. **Verifies storage**: Confirms vectors in Qdrant

## Steps

### 1. Determine Input Type

Check if input is file or URL:

```python
import os
from urllib.parse import urlparse

def is_url(input_str):
    try:
        result = urlparse(input_str)
        return result.scheme in ('http', 'https')
    except:
        return False

if is_url(input_arg):
    mode = "url"
else:
    mode = "file"
```

### 2. Validate Input

**For files**:
```bash
# Check file exists
test -f {file_path} || echo "ERROR: File not found"

# Check file extension
file_ext=$(echo "{file_path}" | grep -oE '\.[^.]+$')
[[ "$file_ext" =~ \.(pdf|docx|md|txt)$ ]] || echo "WARNING: Unusual file type"
```

**For URLs**:
```python
from app.routes.upload import LinkUploadRequest

try:
    request = LinkUploadRequest(url=url)
    # Validates SSRF protection, allowed protocols, etc.
except ValueError as e:
    print(f"❌ Invalid URL: {e}")
    exit(1)
```

### 3. Run Ingestion Pipeline

**For files**:
```python
from ingestion.pipeline import get_pipeline

pipeline = get_pipeline()
result = pipeline.ingest_file(file_path, os.path.basename(file_path))
```

**For URLs**:
```python
from ingestion.firecrawl_client import get_firecrawl_client
from ingestion.pipeline import get_pipeline

# Fetch content
firecrawl = get_firecrawl_client()
scraped = firecrawl.scrape(url)
content = scraped["data"]["markdown"] or scraped["data"]["content"]

# Ingest content
pipeline = get_pipeline()
result = pipeline.ingest_url(url, content)
```

### 4. Display Progress

Show each step as it executes:

```
[1/4] Parsing document...
[2/4] Chunking text (12,543 chars)...
[3/4] Generating embeddings (18 chunks)...
[4/4] Storing vectors and artifacts...
```

### 5. Report Results

Show final outcome:

```python
print(f"✅ Ingestion complete")
print(f"   Doc ID: {result['doc_id']}")
print(f"   Artifact ID: {result['artifact_id']}")
print(f"   Chunks created: {result['chunks_created']}")
print(f"   Status: {result['status']}")
```

### 6. Verify Storage (Verbose Mode)

If `verbose:true`, query Qdrant to confirm:

```python
from ingestion.vector_store import get_vector_store

vs = get_vector_store()
stored_chunks = vs.client.scroll(
    collection_name="kb_passages",
    scroll_filter={
        "must": [{"key": "doc_id", "match": {"value": result['doc_id']}}]
    },
    limit=100
)

print(f"\n🔍 Verification:")
print(f"   Vectors in Qdrant: {len(stored_chunks[0])}")
print(f"   Sample chunk text: {stored_chunks[0][0].payload['text'][:100]}...")
```

## Output Format

### Successful File Ingestion

```
📄 Ingesting file: tests/fixtures/sample.pdf

[1/4] Parsing document...
      Extracted 12,543 characters from 8 pages

[2/4] Chunking text...
      Created 18 chunks (avg 697 chars/chunk, 200 char overlap)

[3/4] Generating embeddings...
      Generated 18 embeddings (384 dimensions each)
      Embedding time: 0.23s

[4/4] Storing vectors and artifacts...
      Upserted 18 vectors to Qdrant
      Saved artifact to artifacts/uploads/
      Upsert time: 0.15s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Ingestion Complete

Doc ID: 3f7b9c42-8d1a-4e5f-9a2c-6b8d1f4e3a7c
Artifact ID: 8a2f5c91-7e3b-4d2a-8c6f-1b9e4a7d3c5f
Chunks created: 18
Status: success
Total time: 0.52s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Next steps:

Test retrieval:
/test-rag "what is in sample.pdf?"

View artifact:
ls -lh artifacts/uploads/8a2f5c91-7e3b-4d2a-8c6f-1b9e4a7d3c5f.pdf

Query via API:
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "sample content", "limit": 5}'
```

### Successful URL Ingestion

```
🔗 Ingesting URL: https://example.com/machine-learning-guide

[1/4] Fetching web page...
      Firecrawl extracting content...
      Retrieved 8,234 characters (markdown format)

[2/4] Chunking text...
      Created 12 chunks (avg 686 chars/chunk)

[3/4] Generating embeddings...
      Generated 12 embeddings (384 dimensions)
      Embedding time: 0.18s

[4/4] Storing vectors and artifacts...
      Upserted 12 vectors to Qdrant
      Saved artifact to artifacts/web/
      Saved HTML and text versions
      Upsert time: 0.11s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Ingestion Complete

Doc ID: web_9d4e2f8a-6c1b-4a3e-9f7c-2d8a5e1b6c4f
Artifact ID: 5c3a8f91-4e2b-6d1a-7c9f-8b4e3a2d1c6f
Chunks created: 12
URL: https://example.com/machine-learning-guide
Status: success
Total time: 1.85s (includes web fetch)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Next steps:

Test retrieval:
/test-rag "machine learning basics"

View artifact:
cat artifacts/web/5c3a8f91-4e2b-6d1a-7c9f-8b4e3a2d1c6f.txt
```

### File Not Found

```
📄 Ingesting file: tests/fixtures/missing.pdf

❌ Error: File not found

Path: tests/fixtures/missing.pdf

Available fixtures:
- tests/fixtures/sample.pdf
- tests/fixtures/sample.docx
- tests/fixtures/sample.md

Check file path and try again.
```

### Unsupported File Type

```
📄 Ingesting file: tests/fixtures/image.png

❌ Error: Unsupported file type

Extension: .png
Supported: .pdf, .docx, .md, .txt

Only document formats are supported for ingestion.
```

### URL Validation Failed (SSRF Protection)

```
🔗 Ingesting URL: http://localhost:8080/admin

❌ Error: Invalid URL

Reason: URLs pointing to localhost are not allowed

This is blocked for security (SSRF protection).
Only public HTTP/HTTPS URLs are allowed.
```

### Firecrawl Error

```
🔗 Ingesting URL: https://example.com/nonexistent

[1/4] Fetching web page...
      Firecrawl request failed

❌ Error: Failed to extract content from URL

Reason: HTTP 404 Not Found

Check the URL and ensure the page is publicly accessible.
```

### Parsing Error

```
📄 Ingesting file: tests/fixtures/corrupted.pdf

[1/4] Parsing document...

❌ Error: PDF parsing failed

Reason: File appears to be corrupted or invalid PDF format

Try:
1. Open file in PDF reader to verify it's valid
2. Re-download or re-export the PDF
3. Use a different file format (DOCX, Markdown, TXT)
```

### Verbose Mode Output

```
📄 Ingesting file: tests/fixtures/sample.pdf (verbose mode)

[1/4] Parsing document...
      ✅ Extracted 12,543 characters from 8 pages
      📄 Metadata: Title="Sample Document", Author="Test User"

[2/4] Chunking text...
      ✅ Created 18 chunks
      📊 Chunk size distribution:
          Min: 542 chars
          Max: 987 chars
          Avg: 697 chars
          Overlap: 200 chars
      🔖 Sample chunk metadata:
          {
            "doc_id": "3f7b9c42-...",
            "filename": "sample.pdf",
            "chunk_index": 0,
            "source": "upload",
            "timestamp": "2025-11-06T..."
          }

[3/4] Generating embeddings...
      ✅ Generated 18 embeddings
      📏 Dimensions: 384 (sentence-transformers/all-MiniLM-L6-v2)
      ⏱️  Time: 0.23s (12.8ms per chunk)
      🔢 Sample embedding (first 5 dims): [0.123, -0.456, 0.789, ...]

[4/4] Storing vectors and artifacts...
      ✅ Upserted 18 vectors to Qdrant collection 'kb_passages'
      📍 Vector IDs: vec_3f7b9c42..._0 through vec_3f7b9c42..._17
      💾 Artifact saved: artifacts/uploads/8a2f5c91...pdf
      📝 Metadata saved: artifacts/uploads/8a2f5c91...meta.json
      ⏱️  Upsert time: 0.15s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Verification (querying Qdrant)...

Vectors in Qdrant for this doc_id: 18 ✅
Collection total vectors: 360
Sample chunk:
  Text: "Machine learning is a subset of artificial..."
  Score (self-similarity): 1.000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Ingestion Complete & Verified

All pipeline steps successful and verified in vector store.
```

## Error Handling

The command handles common errors gracefully:

- **File not found**: Clear message with suggestions
- **Unsupported format**: List of supported formats
- **SSRF blocked URLs**: Security explanation
- **Network errors**: Retry suggestions for URLs
- **Parsing failures**: Format-specific troubleshooting
- **Qdrant down**: Service startup instructions
- **Embedding errors**: Model loading guidance

## Integration with Tests

Use this command to quickly populate test data:

```bash
# Ingest all test fixtures
for file in tests/fixtures/*.pdf; do
    /ingest "$file"
done

# Ingest specific documents for test case
/ingest tests/fixtures/ml-paper.pdf
/ingest https://example.com/ml-article

# Then run tests
pytest tests/test_vector_search.py -v
```

## Performance Notes

Typical ingestion times (local development):

- **Small PDF (5 pages)**: ~0.5s
- **Medium PDF (50 pages)**: ~2.5s
- **Large PDF (200 pages)**: ~8s
- **Web page**: ~2s (includes network fetch)
- **Markdown file**: ~0.3s

Factors affecting speed:
- PDF complexity (images, tables)
- Number of chunks (more chunks = more embeddings)
- Network latency (for URLs)
- Qdrant server load
