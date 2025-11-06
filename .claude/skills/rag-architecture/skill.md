# RAG Architecture Skill

This skill provides deep expertise in the Retrieval-Augmented Generation (RAG) and Contextual-Augmented Generation (CAG) architecture specific to the knowledge-agent project.

## When to Activate

This skill should be active when:
- Implementing RAG or CAG features
- Working on vector search functionality
- Integrating external search capabilities
- Designing answer synthesis logic
- Optimizing retrieval quality
- Debugging search/retrieval issues

## Architecture Overview

The knowledge-agent uses a hybrid RAG + CAG approach:

### RAG (Retrieval-Augmented Generation)
**Internal Knowledge Retrieval**
- Search uploaded documents via vector similarity
- Provides grounded, factual answers from known sources
- High trust, full citation capability
- Limited to indexed content

### CAG (Contextual-Augmented Generation)
**External Intelligence**
- Live web search when internal knowledge insufficient
- Firecrawl extraction for web content
- Cross-verification of facts
- Broader knowledge, but requires validation

## System Components

```
┌─────────────────────────────────────────────────────────┐
│                    User Query                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           RAG Pipeline (Internal Search)                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 1. Embed query (sentence-transformers)           │  │
│  │ 2. Vector search (Qdrant COSINE similarity)      │  │
│  │ 3. Retrieve top-K chunks with metadata           │  │
│  │ 4. Assemble context with citations               │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
                 Sufficient?
                     │
         ┌───────────┴───────────┐
         │ No                    │ Yes
         ▼                       ▼
┌─────────────────────┐   ┌──────────────────────┐
│  CAG Pipeline       │   │  Answer Synthesis    │
│  (External Search)  │   │  (RAG only)          │
│                     │   │                      │
│  1. Web search      │   │  1. Format context   │
│  2. Firecrawl fetch │   │  2. LLM generation   │
│  3. Extract content │   │  3. Add citations    │
│  4. Synthesize      │   │  4. Return answer    │
└──────────┬──────────┘   └──────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│              Critical Reasoning Chain                    │
│  1. Compare internal vs external sources                │
│  2. Cross-check facts                                   │
│  3. Identify contradictions                             │
│  4. Synthesize coherent answer with confidence levels   │
└─────────────────────────────────────────────────────────┘
```

## Vector Embeddings

### Model
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Language**: English-optimized
- **Speed**: Fast (suitable for real-time)
- **Quality**: Good balance between speed and accuracy

### Why This Model?
- Lightweight: ~80MB, fast inference
- Good semantic understanding
- Well-suited for passage retrieval
- Compatible with Qdrant
- Open source (no API costs)

### Embedding Process

```python
from ingestion.embeddings import get_embedding_service

service = get_embedding_service()

# Single text
embedding = service.embed_text("What is machine learning?")
# Returns: List[float] of length 384

# Batch processing (efficient for multiple texts)
embeddings = service.embed_texts([
    "Text 1",
    "Text 2",
    "Text 3"
], batch_size=100)
# Returns: List[List[float]]
```

### Similarity Metric
- **Metric**: COSINE similarity
- **Range**: -1 (opposite) to 1 (identical)
- **Typical threshold**: 0.5-0.7 for relevant results
- **Interpretation**:
  - 0.9+: Very similar (near-duplicates)
  - 0.7-0.9: Highly relevant
  - 0.5-0.7: Moderately relevant
  - <0.5: Weakly relevant or unrelated

## Document Chunking Strategy

### Chunking Parameters

```python
from ingestion.chunker import chunk_text

chunks = chunk_text(
    text=document_text,
    doc_id="abc-123",
    filename="document.pdf",
    source="upload",
    chunk_size=1000,      # Max characters per chunk
    chunk_overlap=200     # Overlap between chunks
)
```

### Why These Parameters?

**Chunk Size: 1000 characters**
- Balances context vs specificity
- Fits in embedding model's context window
- Enough context for meaningful semantics
- Not so large that irrelevant content dilutes signal

**Chunk Overlap: 200 characters**
- Prevents splitting related sentences
- Ensures continuity across chunk boundaries
- Helps with cross-chunk queries
- 20% overlap is standard practice

### Chunking Algorithm

Uses `RecursiveCharacterTextSplitter` from LangChain:

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""],  # Priority order
    length_function=len
)
```

**Separators priority**:
1. Double newline (paragraph breaks) - preferred
2. Single newline (line breaks)
3. Period + space (sentence breaks)
4. Space (word breaks)
5. Character-level (last resort)

This preserves semantic coherence by splitting at natural boundaries.

### Chunk Metadata

Each chunk includes:

```python
{
    "doc_id": "unique-document-id",
    "filename": "original-filename.pdf",
    "chunk_index": 0,  # Position in document
    "source": "upload" | "url",
    "timestamp": "2025-11-06T12:00:00Z",
    "page_number": 3  # For PDFs (optional)
}
```

This enables:
- Citation to source documents
- Ordering chunks from same document
- Filtering by source type
- Time-based relevance

## Vector Store (Qdrant)

### Collection Configuration

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client.create_collection(
    collection_name="kb_passages",
    vectors_config=VectorParams(
        size=384,              # Match embedding dimension
        distance=Distance.COSINE
    )
)
```

### Upsert Process

```python
from ingestion.vector_store import get_vector_store

vs = get_vector_store()

# Upsert chunks (generates embeddings automatically)
result = vs.upsert_chunks(chunks)

# Batch processing for efficiency
# - Embeddings generated in batches of 100
# - Vectors upserted in batches of 100
# - Progress bar for large ingestions
```

### Search Process

```python
# Vector similarity search
results = vs.search(
    query="What is machine learning?",
    limit=5,                    # Top-K results
    score_threshold=0.5         # Minimum similarity
)

# Returns:
[
    {
        "id": "point-id",
        "score": 0.847,
        "text": "Machine learning is...",
        "metadata": {
            "filename": "ml-intro.pdf",
            "doc_id": "abc-123",
            "chunk_index": 3
        }
    },
    ...
]
```

### Deletion

```python
# Delete all chunks for a document
vs.delete_by_doc_id("abc-123")

# Used for:
# - Removing outdated documents
# - Rollback on ingestion failure
# - User-requested deletion
```

## Ingestion Pipeline

### End-to-End Flow

```python
from ingestion.pipeline import get_pipeline

pipeline = get_pipeline()

# For file uploads
result = pipeline.ingest_file(
    file_path="/tmp/upload.pdf",
    filename="research-paper.pdf"
)

# For URLs
result = pipeline.ingest_url(
    url="https://example.com/article",
    text_content="<extracted content>"
)

# Returns:
{
    "doc_id": "unique-id",
    "artifact_id": "artifact-id",
    "chunks_created": 18,
    "status": "success"
}
```

### Pipeline Steps

1. **Parse** (`ingestion/parsers.py`)
   - Extract text from PDF, DOCX, Markdown, TXT
   - Normalize whitespace
   - Handle encoding issues (UTF-8 with fallback)

2. **Chunk** (`ingestion/chunker.py`)
   - Split into semantic passages
   - Add metadata to each chunk
   - Maintain document structure

3. **Embed** (`ingestion/embeddings.py`)
   - Generate 384-dim vectors
   - Batch processing for efficiency
   - Cache embedding model in memory

4. **Store** (`ingestion/vector_store.py`)
   - Upsert vectors to Qdrant
   - Store with complete metadata
   - Index for fast retrieval

5. **Persist** (`ingestion/artifacts.py`)
   - Save original file/content
   - Save metadata JSON
   - Link to vector IDs for cleanup

### Error Handling & Rollback

```python
try:
    result = pipeline.ingest_file(file_path, filename)
except Exception as e:
    # Automatic rollback
    # - Deletes vectors from Qdrant
    # - Cleans up temp files
    # - Logs detailed error
    logger.error(f"Ingestion failed: {e}")
    raise
```

## Retrieval Optimization

### Query Expansion

```python
# Basic query
query = "machine learning"

# Expanded with synonyms (future enhancement)
expanded = [
    "machine learning",
    "ML",
    "artificial intelligence",
    "neural networks"
]

# Search with multiple queries, merge results
```

### Hybrid Search (Future)

Combine vector search with keyword search:

```python
# Vector search for semantic similarity
vector_results = vs.search(query, limit=10)

# Keyword search for exact matches
keyword_results = full_text_search(query, limit=10)

# Merge with reciprocal rank fusion (RRF)
final_results = merge_results(vector_results, keyword_results)
```

### Re-ranking (Future)

Use cross-encoder to re-rank top results:

```python
from sentence_transformers import CrossEncoder

model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# Get initial results
candidates = vs.search(query, limit=20)

# Re-rank with cross-encoder (more accurate but slower)
scores = model.predict([(query, c['text']) for c in candidates])
reranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
```

## Firecrawl Integration (CAG)

### Web Content Extraction

```python
from ingestion.firecrawl_client import get_firecrawl_client

firecrawl = get_firecrawl_client()

result = firecrawl.scrape(url)

# Returns:
{
    "success": True,
    "data": {
        "markdown": "# Extracted Content\n\n...",
        "content": "Plain text version...",
        "html": "<html>...</html>",
        "metadata": {
            "title": "Page Title",
            "description": "Meta description",
            ...
        }
    }
}
```

### SSRF Protection

URLs are validated before scraping:

```python
from app.routes.upload import LinkUploadRequest

# Validates:
# - Protocol (HTTP/HTTPS only)
# - No localhost/127.0.0.1
# - No private IP ranges (10.x, 192.168.x, 172.16-31.x)
# - No link-local addresses (169.254.x.x)
# - No cloud metadata endpoints (169.254.169.254)

request = LinkUploadRequest(url="https://example.com")
# Raises ValueError if URL is unsafe
```

### Error Handling

```python
try:
    result = firecrawl.scrape(url)
except ConnectionError:
    # Network unreachable
except TimeoutError:
    # Request timeout
except ValueError:
    # Invalid response format
except Exception:
    # Other errors (quota exceeded, etc.)
```

## LangChain Integration (Future Features)

### Retrieval Chain

```python
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from ingestion.vector_store import get_vector_store

llm = ChatOpenAI(model="gpt-4", temperature=0)
vs = get_vector_store()

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",  # or "map_reduce", "refine"
    retriever=vs.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True
)

result = qa_chain({"query": "What is machine learning?"})
print(result["result"])  # Answer
print(result["source_documents"])  # Citations
```

### Agent with Tools

```python
from langchain.agents import initialize_agent, Tool
from langchain.tools import TavilySearchResults

tools = [
    Tool(
        name="Internal Knowledge Base",
        func=lambda q: vs.search(q, limit=5),
        description="Search uploaded documents"
    ),
    TavilySearchResults(max_results=5),  # External search
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)

response = agent.run("What is machine learning? Include recent developments.")
```

## Performance Optimization

### Embedding Caching

```python
# Model loaded once and cached
service = get_embedding_service()  # Singleton pattern

# Reused across requests
embedding1 = service.embed_text("query 1")
embedding2 = service.embed_text("query 2")  # No model reload
```

### Batch Processing

```python
# Efficient batch embedding
texts = ["text 1", "text 2", "text 3", ...]
embeddings = service.embed_texts(texts, batch_size=100)
# Processes 100 texts at a time, much faster than individual calls
```

### Vector Store Optimization

```python
# Create indexes for faster search
client.create_payload_index(
    collection_name="kb_passages",
    field_name="doc_id",
    field_schema="keyword"
)

# Enables fast filtering by doc_id
results = vs.search(
    query="...",
    filter={"doc_id": "specific-doc"}
)
```

## Monitoring & Debugging

### Ingestion Metrics

```python
# Logged during pipeline execution
logger.info(f"[1/4] Parsing document...")
logger.info(f"[2/4] Chunking text ({len(text)} chars)...")
logger.info(f"[3/4] Storing {len(chunks)} chunks...")
logger.info(f"[4/4] Completed: {result}")
```

### Search Quality Metrics

```python
results = vs.search(query, limit=5)

# Log relevance scores
for i, r in enumerate(results):
    logger.debug(f"Result {i+1}: score={r['score']:.3f}, source={r['metadata']['filename']}")

# Alert if scores are low
avg_score = sum(r['score'] for r in results) / len(results)
if avg_score < 0.6:
    logger.warning(f"Low average relevance score: {avg_score:.3f}")
```

### Test RAG Pipeline

Use `/test-rag` command:

```bash
/test-rag "machine learning basics"

# Shows:
# - Latency
# - Result count
# - Similarity scores
# - Source diversity
# - Assembled context
```

## Best Practices

### For Retrieval Quality

1. **Chunk size matters**: Too small = lack of context, too large = diluted signal
2. **Overlap prevents gaps**: 20% overlap catches cross-boundary content
3. **Score thresholds**: Start at 0.5, adjust based on precision/recall needs
4. **Top-K selection**: 5-10 results balances coverage vs noise
5. **Source diversity**: Prefer results from different documents

### For Ingestion Efficiency

1. **Batch uploads**: Group multiple documents for processing
2. **Async processing**: Use background tasks for large uploads
3. **Error handling**: Rollback on failure to maintain consistency
4. **Metadata richness**: More metadata = better filtering and citation

### For Answer Quality

1. **Citation required**: Always link answers to sources
2. **Confidence scores**: Show similarity scores to users
3. **External validation**: Use CAG for fact-checking RAG answers
4. **Contradiction detection**: Flag when sources disagree
5. **Recency awareness**: Prefer newer sources when relevant

## Common Issues & Solutions

### Low Relevance Scores

**Problem**: Search returns results but scores are low (<0.5)

**Solutions**:
- Rephrase query to match document language
- Check if relevant content is indexed
- Lower threshold temporarily
- Add more diverse training content

### No Results Found

**Problem**: Search returns empty array

**Solutions**:
- Check if Qdrant collection has vectors
- Verify embedding model consistency
- Check score threshold (might be too high)
- Verify query isn't empty

### Slow Ingestion

**Problem**: Document ingestion takes too long

**Solutions**:
- Use batch embedding (batch_size=100)
- Process large PDFs in chunks
- Use async/background processing
- Consider lighter parsing libraries

### Memory Issues

**Problem**: Out of memory during large ingestions

**Solutions**:
- Process documents one at a time
- Reduce batch size for embeddings
- Clear embedding model cache if needed
- Use streaming for very large files

## Future Enhancements

1. **Hybrid Search**: Combine vector + keyword search
2. **Re-ranking**: Cross-encoder for top results
3. **Query Expansion**: Automatic synonym expansion
4. **Semantic Caching**: Cache common query results
5. **Feedback Loop**: Learn from user feedback
6. **Multi-modal**: Support images, tables, charts
7. **Conversation Memory**: Remember context across queries

This skill provides deep understanding of the RAG/CAG architecture in the knowledge-agent project, enabling effective implementation and optimization of retrieval and generation features.
