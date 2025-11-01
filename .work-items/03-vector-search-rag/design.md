# Design: Vector Search and RAG Retrieval

## Objective

Implement a complete RAG (Retrieval-Augmented Generation) retrieval system with vector similarity search over Qdrant, LangChain tool integration for composable workflows, and session-based conversation memory for multi-turn interactions. This feature enables natural language querying of the indexed knowledge base with contextual follow-up support.

## Technical Design

### System Architecture

The RAG retrieval system consists of three main components:

1. **Vector Search Engine** - Similarity search over Qdrant vector database
2. **LangChain Retrieval Tool** - Wrapper exposing search as composable LangChain tool
3. **Session Memory Service** - Conversation history and context management

### Data Flow

```
User Query → Embed Query → Vector Search → Rank Results → Return Passages
                                                              ↓
                                                    LangChain Tool Output
                                                              ↓
                                               Session Memory Update
```

## Key Components

### 2.1 API Endpoints

**POST /query**
- Accepts: JSON `{"query": "What is machine learning?", "session_id": "<uuid>", "top_k": 5}`
- Query embedding: Same model as document embeddings (all-MiniLM-L6-v2)
- Vector search: Qdrant similarity search with cosine distance
- Returns:
  ```json
  {
    "query": "What is machine learning?",
    "passages": [
      {
        "text": "Machine learning is...",
        "metadata": {
          "doc_id": "uuid",
          "filename": "ml_basics.pdf",
          "chunk_index": 3,
          "page_number": 12,
          "source": "upload"
        },
        "score": 0.89
      }
    ],
    "session_id": "uuid"
  }
  ```
- Error codes: 400 (empty query), 404 (no documents), 500 (search error)

**GET /session/{session_id}**
- Returns conversation history for a session
- Response: `{"session_id": "uuid", "history": [...], "created_at": "timestamp"}`

**DELETE /session/{session_id}**
- Clears all conversation history for session
- Returns: `{"status": "cleared", "session_id": "uuid"}`

### 2.2 Data Models

**SearchRequest**:
```python
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)
```

**SearchResult**:
```python
class SearchResult(BaseModel):
    text: str
    metadata: dict = {
        "doc_id": str,
        "filename": str,
        "chunk_index": int,
        "page_number": Optional[int],
        "source": str,
        "timestamp": str
    }
    score: float
```

**SearchResponse**:
```python
class SearchResponse(BaseModel):
    query: str
    passages: list[SearchResult]
    session_id: str
    result_count: int
```

**SessionMemory**:
```python
class SessionMemory(BaseModel):
    session_id: str
    history: list[dict] = []  # [{role: "user", content: "..."}, {role: "assistant", content: "..."}]
    pinned: list[str] = []     # Pinned passage IDs
    created_at: datetime
    updated_at: datetime
```

### 2.3 Component Responsibilities

**VectorSearchService** (`app/services/vector_search.py`):
- Embed queries using same model as documents
- Query Qdrant for similar vectors with configurable top-K
- Filter by metadata (optional: document type, source, date range)
- Return ranked passages with scores and metadata
- Handle edge cases: empty queries, empty database, connection errors

Methods:
```python
def embed_query(query: str) -> list[float]:
    """Convert query text to 384-dimensional vector."""

def search_vectors(query: str, top_k: int = 5, filters: dict = None) -> list[SearchResult]:
    """Search Qdrant for most similar passages."""

def validate_query(query: str) -> None:
    """Validate query length and content."""
```

**RetrieverTool** (`app/tools/retriever.py`):
- Wrap vector search as LangChain Tool or StructuredTool
- Define clear name, description, and input schema
- Return JSON-serializable output for chain composition
- Support both direct invocation and chain integration
- Enable use in LangGraph workflows

Implementation:
```python
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

class RetrievalInput(BaseModel):
    query: str = Field(description="The question or search query")
    top_k: int = Field(default=5, description="Number of passages to retrieve")

def retrieve_passages(query: str, top_k: int = 5) -> dict:
    """Retrieve top-k passages relevant to the query.

    Returns:
        Dictionary with keys:
        - passages: List of passage objects with text, metadata, scores
        - query: Original query string
        - count: Number of results
    """
    search_service = VectorSearchService()
    results = search_service.search_vectors(query, top_k)
    return {
        "passages": [r.dict() for r in results],
        "query": query,
        "count": len(results)
    }

retrieval_tool = StructuredTool(
    name="search_knowledge_base",
    description="Search the internal knowledge base for passages relevant to a query. Returns text snippets with metadata and similarity scores.",
    func=retrieve_passages,
    args_schema=RetrievalInput,
    return_direct=False
)
```

**MemoryService** (`app/services/memory.py`):
- Maintain session store keyed by session_id (UUID)
- Store conversation history (user queries, assistant responses)
- Support CRUD operations: create, get, update, clear sessions
- Persist pinned passages/notes for user reference
- LangChain memory integration (ConversationBufferMemory)

In-memory implementation:
```python
from typing import Dict, Any
from datetime import datetime

class MemoryService:
    def __init__(self):
        self._store: Dict[str, SessionMemory] = {}

    def get_or_create_session(self, session_id: str) -> SessionMemory:
        """Get existing session or create new one."""
        if session_id not in self._store:
            self._store[session_id] = SessionMemory(
                session_id=session_id,
                history=[],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        return self._store[session_id]

    def add_interaction(self, session_id: str, user_msg: str, assistant_msg: str, citations: list = None):
        """Record a query-response interaction."""
        session = self.get_or_create_session(session_id)
        session.history.extend([
            {"role": "user", "content": user_msg, "timestamp": datetime.utcnow().isoformat()},
            {"role": "assistant", "content": assistant_msg, "citations": citations or [], "timestamp": datetime.utcnow().isoformat()}
        ])
        session.updated_at = datetime.utcnow()

    def clear_session(self, session_id: str) -> None:
        """Remove all history for a session."""
        self._store.pop(session_id, None)

    def get_session_history(self, session_id: str) -> list[dict]:
        """Retrieve conversation history for a session."""
        session = self.get_or_create_session(session_id)
        return session.history
```

LangChain integration:
```python
from langchain.memory import ConversationBufferMemory

def get_langchain_memory(session_id: str) -> ConversationBufferMemory:
    """Create LangChain memory instance for session."""
    memory_service = MemoryService()
    history = memory_service.get_session_history(session_id)

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    # Load existing history
    for entry in history:
        if entry["role"] == "user":
            memory.chat_memory.add_user_message(entry["content"])
        elif entry["role"] == "assistant":
            memory.chat_memory.add_ai_message(entry["content"])

    return memory
```

### 2.4 External Services Integration

**Qdrant Vector Search**:
- Collection: `kb_passages` (created in F02: Document Ingestion)
- Query method: `client.search(collection_name, query_vector, limit, with_payload)`
- Distance metric: Cosine similarity
- Response includes: point ID, score, payload (text + metadata)

**Embedding Model**:
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Must use same model as document ingestion (consistency critical)
- Dimension: 384
- Normalization: L2 (handled by sentence-transformers)

## Technical Constraints

### Query Processing
- Minimum query length: 1 character (but recommend 3+)
- Maximum query length: 1000 characters
- Empty queries return validation error (HTTP 400)
- Query embedding timeout: 5 seconds

### Search Parameters
- Default top_k: 5 results
- Maximum top_k: 20 results (prevent excessive response size)
- Minimum relevance score: 0.0 (no filtering by default)
- Optional: filter by score threshold (e.g., only return score > 0.7)

### Session Management
- Session ID format: UUID v4
- Session lifetime: In-memory (persists for application lifetime)
- Production requirement: Replace with Redis/database for multi-worker support
- Maximum history per session: 100 interactions (prevent memory bloat)

### Performance
- Query embedding: <100ms (local model)
- Qdrant search: <200ms for 10k documents
- Total response time: <500ms target
- Memory per session: ~10KB (100 interactions × ~100 bytes)

## Alternatives Considered

1. **Vector Database**:
   - Considered: Pinecone, Weaviate, Chroma
   - Chose: Qdrant (already selected in F02)
   - Reason: Consistency with ingestion pipeline

2. **Embedding Strategy**:
   - Considered: Query-specific model vs. same as documents
   - Chose: Same model (all-MiniLM-L6-v2)
   - Reason: Ensures embedding space compatibility

3. **Retrieval Tool Framework**:
   - Considered: Custom implementation vs. LangChain Tool
   - Chose: LangChain StructuredTool
   - Reason: Enables composition with chains/agents, type validation

4. **Memory Backend**:
   - Considered: In-memory dict, Redis, PostgreSQL, DynamoDB
   - Chose: In-memory for MVP, Redis for production
   - Reason: Simple for single-worker, scalable path for multi-worker

5. **Memory Strategy**:
   - Considered: ConversationBufferMemory, ConversationSummaryMemory, Custom
   - Chose: Custom store + ConversationBufferMemory wrapper
   - Reason: Flexibility for pinning, citations, metadata while maintaining LangChain compatibility

6. **Session ID Generation**:
   - Considered: Server-generated vs. client-generated
   - Chose: Server-generated (optional client override)
   - Reason: Prevents ID collisions, easier to audit

## Out of Scope

- Advanced search features (boolean operators, phrase matching, fuzzy search)
- Hybrid search (keyword + vector)
- Re-ranking with cross-encoder models
- Query expansion or reformulation
- Multi-index search (searching across multiple collections)
- Session persistence to disk/database (MVP is in-memory)
- Session authentication/authorization
- Rate limiting per session
- Analytics and search metrics
- Query auto-completion
- Search result highlighting
- Faceted search (filter UI)

## Dependencies

- Feature F02: Document Ingestion (must have documents indexed in Qdrant)
- Qdrant instance running with `kb_passages` collection
- Embedding model downloaded (sentence-transformers/all-MiniLM-L6-v2)
- LangChain and LangGraph installed

## Security Considerations

1. **Query Injection**:
   - Validate query length and characters
   - Sanitize before logging to prevent log injection
   - Use parameterized Qdrant queries (prevent vector injection)

2. **Session Isolation**:
   - UUIDs prevent session guessing
   - No cross-session data leakage in memory store
   - Production: Add session-to-user mapping for authorization

3. **Resource Limits**:
   - Cap top_k to prevent expensive searches
   - Limit session history size to prevent memory exhaustion
   - Timeout on embedding and search operations

4. **Privacy**:
   - Session data stored in-memory (ephemeral)
   - No persistent logging of user queries (except app logs)
   - Clear session endpoint for user privacy control

## Future Enhancements

- Task 11: Integrate retrieval tool into LangGraph RAG workflow
- Task 12: Add citation generation and answer synthesis
- Persistent session storage (Redis/PostgreSQL)
- Multi-tenant session isolation with user authentication
- Search analytics and monitoring dashboard
- Hybrid search combining vector and keyword search
- Custom re-ranking models for improved relevance
- Session export for analysis
- A/B testing different retrieval strategies
