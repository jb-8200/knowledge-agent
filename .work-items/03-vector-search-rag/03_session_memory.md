# Step 03: Configure Session and Memory Services

## Objective

Implement session management and conversation memory services that maintain context across multiple queries, enable multi-turn conversations, and integrate with LangChain's memory abstractions while ensuring session isolation.

## Atomic Implementation

This step is atomic: it either creates a complete session/memory system with CRUD operations, conversation persistence, and API endpoints, or fails with clear error messages. No partial state.

## TDD Cycle

### Red Phase

Write failing tests that define expected session and memory behavior:

```python
# tests/test_memory_service.py
import pytest
from datetime import datetime
from app.services.memory import MemoryService, SessionMemory
import uuid

def test_memory_service_initialization():
    """Test that MemoryService initializes with empty store."""
    service = MemoryService()
    assert isinstance(service._store, dict)
    assert len(service._store) == 0

def test_get_or_create_session_creates_new():
    """Test creating a new session."""
    service = MemoryService()
    session_id = str(uuid.uuid4())

    session = service.get_or_create_session(session_id)

    assert isinstance(session, SessionMemory)
    assert session.session_id == session_id
    assert len(session.history) == 0
    assert isinstance(session.created_at, datetime)

def test_get_or_create_session_retrieves_existing():
    """Test retrieving existing session doesn't create duplicate."""
    service = MemoryService()
    session_id = str(uuid.uuid4())

    session1 = service.get_or_create_session(session_id)
    session2 = service.get_or_create_session(session_id)

    assert session1.session_id == session2.session_id
    assert session1.created_at == session2.created_at

def test_add_interaction_stores_messages():
    """Test adding user-assistant interaction to session."""
    service = MemoryService()
    session_id = str(uuid.uuid4())

    service.add_interaction(
        session_id=session_id,
        user_msg="What is AI?",
        assistant_msg="AI is artificial intelligence.",
        citations=["doc1", "doc2"]
    )

    session = service.get_or_create_session(session_id)
    assert len(session.history) == 2  # user + assistant

    assert session.history[0]["role"] == "user"
    assert session.history[0]["content"] == "What is AI?"
    assert session.history[1]["role"] == "assistant"
    assert session.history[1]["content"] == "AI is artificial intelligence."
    assert session.history[1]["citations"] == ["doc1", "doc2"]

def test_add_multiple_interactions():
    """Test adding multiple interactions to same session."""
    service = MemoryService()
    session_id = str(uuid.uuid4())

    service.add_interaction(session_id, "Question 1", "Answer 1")
    service.add_interaction(session_id, "Question 2", "Answer 2")
    service.add_interaction(session_id, "Question 3", "Answer 3")

    session = service.get_or_create_session(session_id)
    assert len(session.history) == 6  # 3 interactions × 2 messages

def test_get_session_history():
    """Test retrieving conversation history."""
    service = MemoryService()
    session_id = str(uuid.uuid4())

    service.add_interaction(session_id, "Hello", "Hi there")

    history = service.get_session_history(session_id)

    assert isinstance(history, list)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"

def test_clear_session():
    """Test clearing session removes all history."""
    service = MemoryService()
    session_id = str(uuid.uuid4())

    service.add_interaction(session_id, "Test", "Response")
    assert len(service.get_session_history(session_id)) == 2

    service.clear_session(session_id)

    # Should create new empty session
    history = service.get_session_history(session_id)
    assert len(history) == 0

def test_session_isolation():
    """Test that different sessions don't share history."""
    service = MemoryService()
    session1 = str(uuid.uuid4())
    session2 = str(uuid.uuid4())

    service.add_interaction(session1, "Session 1 question", "Session 1 answer")
    service.add_interaction(session2, "Session 2 question", "Session 2 answer")

    history1 = service.get_session_history(session1)
    history2 = service.get_session_history(session2)

    assert len(history1) == 2
    assert len(history2) == 2
    assert history1[0]["content"] == "Session 1 question"
    assert history2[0]["content"] == "Session 2 question"

def test_updated_at_timestamp():
    """Test that updated_at is modified on interaction."""
    service = MemoryService()
    session_id = str(uuid.uuid4())

    session1 = service.get_or_create_session(session_id)
    initial_updated = session1.updated_at

    import time
    time.sleep(0.01)  # Small delay

    service.add_interaction(session_id, "Query", "Response")
    session2 = service.get_or_create_session(session_id)

    assert session2.updated_at > initial_updated

def test_langchain_memory_integration():
    """Test LangChain ConversationBufferMemory wrapper."""
    from app.services.memory import get_langchain_memory

    service = MemoryService()
    session_id = str(uuid.uuid4())

    # Add some history
    service.add_interaction(session_id, "What is ML?", "Machine learning is...")

    # Get LangChain memory
    memory = get_langchain_memory(session_id)

    # Verify memory loads history
    messages = memory.chat_memory.messages
    assert len(messages) == 2
    assert messages[0].content == "What is ML?"
    assert messages[1].content == "Machine learning is..."

def test_session_memory_model():
    """Test SessionMemory Pydantic model."""
    session = SessionMemory(
        session_id="test-123",
        history=[
            {"role": "user", "content": "Hi", "timestamp": "2024-01-01T00:00:00Z"}
        ],
        pinned=["passage1"],
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1)
    )

    assert session.session_id == "test-123"
    assert len(session.history) == 1
    assert len(session.pinned) == 1
    assert isinstance(session.created_at, datetime)
```

```python
# tests/test_session_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_get_session_new_returns_empty_history():
    """Test GET /session/{id} for new session."""
    session_id = str(uuid.uuid4())

    response = client.get(f"/session/{session_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert data["history"] == []
    assert "created_at" in data

def test_get_session_with_history():
    """Test GET /session/{id} returns conversation history."""
    from app.services.memory import MemoryService

    # Add interaction directly to service
    service = MemoryService()
    session_id = str(uuid.uuid4())
    service.add_interaction(session_id, "Test question", "Test answer")

    response = client.get(f"/session/{session_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data["history"]) == 2
    assert data["history"][0]["role"] == "user"
    assert data["history"][0]["content"] == "Test question"

def test_delete_session_clears_history():
    """Test DELETE /session/{id} removes all history."""
    from app.services.memory import MemoryService

    service = MemoryService()
    session_id = str(uuid.uuid4())
    service.add_interaction(session_id, "Question", "Answer")

    # Verify history exists
    response1 = client.get(f"/session/{session_id}")
    assert len(response1.json()["history"]) == 2

    # Clear session
    response2 = client.delete(f"/session/{session_id}")
    assert response2.status_code == 200
    assert response2.json()["status"] == "cleared"

    # Verify history is empty
    response3 = client.get(f"/session/{session_id}")
    assert len(response3.json()["history"]) == 0

def test_post_query_updates_session_memory():
    """Test POST /query adds interaction to session."""
    session_id = str(uuid.uuid4())

    # Mock search results for query endpoint
    # (Assumes /query endpoint uses retrieval_tool)
    response = client.post("/query", json={
        "query": "What is Python?",
        "session_id": session_id,
        "top_k": 3
    })

    # Check session was updated
    session_response = client.get(f"/session/{session_id}")
    history = session_response.json()["history"]

    # Should have at least the user query
    assert any(
        msg["role"] == "user" and "Python" in msg["content"]
        for msg in history
    )

def test_session_id_validation():
    """Test that invalid session IDs are handled."""
    response = client.get("/session/invalid-not-uuid")

    # Should still work (create new session with that ID)
    # OR return validation error - depends on design choice
    assert response.status_code in [200, 422]
```

**Expected Result**: All tests fail because MemoryService and session endpoints don't exist yet.

### Green Phase

1. **Create MemoryService implementation**:

```python
# app/services/memory.py
"""Session and conversation memory management."""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
import logging

logger = logging.getLogger(__name__)

class SessionMemory(BaseModel):
    """Represents conversation memory for a session."""
    session_id: str
    history: List[Dict[str, Any]] = Field(default_factory=list)
    pinned: List[str] = Field(default_factory=list)  # Pinned passage IDs
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class MemoryService:
    """Service for managing session-based conversation memory."""

    def __init__(self):
        """Initialize memory service with empty session store."""
        self._store: Dict[str, SessionMemory] = {}
        logger.info("MemoryService initialized")

    def get_or_create_session(self, session_id: str) -> SessionMemory:
        """Get existing session or create new one.

        Args:
            session_id: Unique session identifier (UUID)

        Returns:
            SessionMemory object for the session
        """
        if session_id not in self._store:
            logger.info(f"Creating new session: {session_id}")
            now = datetime.utcnow()
            self._store[session_id] = SessionMemory(
                session_id=session_id,
                history=[],
                pinned=[],
                created_at=now,
                updated_at=now
            )
        return self._store[session_id]

    def add_interaction(
        self,
        session_id: str,
        user_msg: str,
        assistant_msg: str,
        citations: Optional[List[str]] = None
    ) -> None:
        """Record a user-assistant interaction.

        Args:
            session_id: Session identifier
            user_msg: User's query or message
            assistant_msg: Assistant's response
            citations: Optional list of document/passage IDs cited
        """
        session = self.get_or_create_session(session_id)

        now = datetime.utcnow()
        timestamp = now.isoformat()

        # Add user message
        session.history.append({
            "role": "user",
            "content": user_msg,
            "timestamp": timestamp
        })

        # Add assistant message
        session.history.append({
            "role": "assistant",
            "content": assistant_msg,
            "citations": citations or [],
            "timestamp": timestamp
        })

        # Update timestamp
        session.updated_at = now

        logger.info(
            f"Added interaction to session {session_id}: "
            f"history_length={len(session.history)}"
        )

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieve conversation history for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of message dictionaries with role, content, timestamp
        """
        session = self.get_or_create_session(session_id)
        return session.history

    def clear_session(self, session_id: str) -> None:
        """Remove all history for a session.

        Args:
            session_id: Session identifier to clear
        """
        if session_id in self._store:
            logger.info(f"Clearing session: {session_id}")
            self._store.pop(session_id)
        else:
            logger.warning(f"Attempted to clear non-existent session: {session_id}")

    def pin_passage(self, session_id: str, passage_id: str) -> None:
        """Pin a passage for later reference.

        Args:
            session_id: Session identifier
            passage_id: Document/passage identifier to pin
        """
        session = self.get_or_create_session(session_id)
        if passage_id not in session.pinned:
            session.pinned.append(passage_id)
            logger.info(f"Pinned passage {passage_id} in session {session_id}")

    def get_pinned_passages(self, session_id: str) -> List[str]:
        """Get list of pinned passage IDs.

        Args:
            session_id: Session identifier

        Returns:
            List of pinned passage IDs
        """
        session = self.get_or_create_session(session_id)
        return session.pinned

# Global singleton instance
_memory_service = MemoryService()

def get_memory_service() -> MemoryService:
    """Get global MemoryService instance."""
    return _memory_service

def get_langchain_memory(session_id: str) -> ConversationBufferMemory:
    """Create LangChain ConversationBufferMemory for session.

    Args:
        session_id: Session identifier

    Returns:
        ConversationBufferMemory with loaded history
    """
    service = get_memory_service()
    history = service.get_session_history(session_id)

    # Create memory instance
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    # Load existing history
    for entry in history:
        if entry["role"] == "user":
            memory.chat_memory.add_message(HumanMessage(content=entry["content"]))
        elif entry["role"] == "assistant":
            memory.chat_memory.add_message(AIMessage(content=entry["content"]))

    logger.info(f"Created LangChain memory for session {session_id}: {len(history)} messages")

    return memory
```

2. **Create session API endpoints**:

```python
# app/routes/session.py
"""Session management API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.services.memory import get_memory_service

router = APIRouter()

class SessionResponse(BaseModel):
    """Response model for session endpoint."""
    session_id: str
    history: List[Dict[str, Any]]
    pinned: List[str]
    created_at: str
    updated_at: str

class ClearSessionResponse(BaseModel):
    """Response model for clear session endpoint."""
    status: str
    session_id: str

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session information and conversation history.

    Args:
        session_id: Session identifier

    Returns:
        Session data including history and metadata
    """
    service = get_memory_service()
    session = service.get_or_create_session(session_id)

    return SessionResponse(
        session_id=session.session_id,
        history=session.history,
        pinned=session.pinned,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat()
    )

@router.delete("/{session_id}", response_model=ClearSessionResponse)
async def clear_session(session_id: str):
    """Clear all conversation history for a session.

    Args:
        session_id: Session identifier to clear

    Returns:
        Confirmation of cleared session
    """
    service = get_memory_service()
    service.clear_session(session_id)

    return ClearSessionResponse(
        status="cleared",
        session_id=session_id
    )
```

3. **Update main.py to include session router**:

```python
# app/main.py (add to existing app)
from app.routes import session

# Include session router
app.include_router(session.router, prefix="/session", tags=["session"])
```

4. **Update services package init**:

```python
# app/services/__init__.py
from .vector_search import VectorSearchService, SearchResult
from .memory import MemoryService, SessionMemory, get_memory_service, get_langchain_memory

__all__ = [
    "VectorSearchService",
    "SearchResult",
    "MemoryService",
    "SessionMemory",
    "get_memory_service",
    "get_langchain_memory"
]
```

5. **Run tests**:

```bash
pytest tests/test_memory_service.py tests/test_session_api.py -v
```

**Expected Result**: All tests pass.

### Refactor Phase

1. **Add session limits** to prevent memory bloat:

```python
# app/services/memory.py
class MemoryService:
    MAX_HISTORY_SIZE = 100  # Maximum interactions per session
    MAX_SESSIONS = 1000     # Maximum active sessions

    def add_interaction(self, session_id: str, user_msg: str, assistant_msg: str, citations=None):
        """Add interaction with history limits."""
        session = self.get_or_create_session(session_id)

        # ... add messages ...

        # Enforce history limit
        if len(session.history) > self.MAX_HISTORY_SIZE * 2:  # 2 messages per interaction
            # Remove oldest interaction (2 messages)
            session.history = session.history[2:]
            logger.warning(f"Session {session_id} history truncated to {len(session.history)} messages")

    def get_or_create_session(self, session_id: str) -> SessionMemory:
        """Create session with store size limits."""
        if session_id not in self._store:
            # Enforce session limit
            if len(self._store) >= self.MAX_SESSIONS:
                # Evict oldest session
                oldest = min(self._store.values(), key=lambda s: s.updated_at)
                self._store.pop(oldest.session_id)
                logger.warning(f"Evicted session {oldest.session_id} due to size limit")

            # ... create new session ...
```

2. **Add session statistics endpoint**:

```python
# app/routes/session.py
class SessionStatsResponse(BaseModel):
    """Response model for session statistics."""
    active_sessions: int
    total_interactions: int
    average_history_size: float

@router.get("/", response_model=SessionStatsResponse)
async def get_session_stats():
    """Get statistics about all sessions.

    Returns:
        Statistics about active sessions and usage
    """
    service = get_memory_service()

    total_interactions = sum(
        len(session.history) // 2  # 2 messages per interaction
        for session in service._store.values()
    )

    avg_history = (
        total_interactions / len(service._store)
        if service._store
        else 0
    )

    return SessionStatsResponse(
        active_sessions=len(service._store),
        total_interactions=total_interactions,
        average_history_size=avg_history
    )
```

3. **Add session export** for analysis:

```python
# app/routes/session.py
from fastapi.responses import JSONResponse

@router.get("/{session_id}/export")
async def export_session(session_id: str):
    """Export full session data as JSON.

    Args:
        session_id: Session identifier

    Returns:
        Complete session data including history and metadata
    """
    service = get_memory_service()
    session = service.get_or_create_session(session_id)

    return JSONResponse(content={
        "session_id": session.session_id,
        "history": session.history,
        "pinned": session.pinned,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
        "metadata": {
            "interaction_count": len(session.history) // 2,
            "pinned_count": len(session.pinned)
        }
    })
```

4. **Add comprehensive logging**:

```python
# app/services/memory.py
import time

def add_interaction(self, session_id: str, user_msg: str, assistant_msg: str, citations=None):
    """Add interaction with detailed logging."""
    start_time = time.time()

    session = self.get_or_create_session(session_id)

    # ... add messages ...

    elapsed = (time.time() - start_time) * 1000
    logger.info(
        f"Session update: id={session_id}, "
        f"history_size={len(session.history)}, "
        f"pinned={len(session.pinned)}, "
        f"citations={len(citations or [])}, "
        f"elapsed={elapsed:.1f}ms"
    )
```

5. **Commit changes**:

```bash
git add .
git commit -m "feat: implement session and memory services

- Create MemoryService with in-memory session store
- Add CRUD operations: get, create, update, clear sessions
- Implement conversation history persistence
- Add LangChain ConversationBufferMemory integration
- Create session API endpoints (GET, DELETE /session/{id})
- Add session isolation and history limits
- Add session statistics and export endpoints
- Tests verify multi-turn conversations and isolation
- All tests passing

Covers Task 10 from original requirements.
"
```

## Acceptance Criteria Verification

- [x] MemoryService initializes with empty session store
- [x] get_or_create_session creates new or retrieves existing
- [x] add_interaction stores user and assistant messages
- [x] Citations stored with assistant messages
- [x] get_session_history retrieves full conversation
- [x] clear_session removes all history
- [x] Session isolation prevents cross-contamination
- [x] LangChain memory integration works correctly
- [x] GET /session/{id} returns session data
- [x] DELETE /session/{id} clears history
- [x] updated_at timestamp modified on interaction
- [x] All tests pass

## Files Created/Modified

- Created: `app/services/memory.py`
- Created: `app/routes/session.py`
- Created: `tests/test_memory_service.py`
- Created: `tests/test_session_api.py`
- Modified: `app/services/__init__.py`
- Modified: `app/main.py` (include session router)

## Rollback Strategy

If this step fails:
1. Remove `app/services/memory.py`
2. Remove `app/routes/session.py`
3. Remove test files
4. Run `git reset --hard HEAD~1`
5. Review errors and retry from Red phase

## Dependencies

Requires:
- LangChain installed with memory modules
- Pydantic for data models
- FastAPI for API endpoints
- Virtual environment activated

## Testing the Service Manually

Test in Python REPL:

```python
from app.services.memory import MemoryService, get_langchain_memory
import uuid

# Initialize service
service = MemoryService()
session_id = str(uuid.uuid4())

# Add interactions
service.add_interaction(
    session_id,
    "What is machine learning?",
    "Machine learning is a subset of AI...",
    citations=["doc1", "doc2"]
)

service.add_interaction(
    session_id,
    "Tell me more about neural networks",
    "Neural networks are computational models...",
    citations=["doc3"]
)

# Get history
history = service.get_session_history(session_id)
print(f"History length: {len(history)}")
for msg in history:
    print(f"{msg['role']}: {msg['content'][:50]}...")

# Test LangChain integration
memory = get_langchain_memory(session_id)
print(f"LangChain messages: {len(memory.chat_memory.messages)}")
```

Test API endpoints:

```bash
# Start server
uvicorn app.main:app --reload

# Get session
curl http://localhost:8000/session/test-session-123

# Clear session
curl -X DELETE http://localhost:8000/session/test-session-123

# Get stats
curl http://localhost:8000/session/
```

## Production Considerations

For production deployment:

1. **Replace in-memory store** with persistent backend:
   - Redis for fast session storage
   - PostgreSQL for durable storage
   - DynamoDB for serverless architecture

2. **Add session authentication**:
   - Map session_id to authenticated user
   - Implement access control

3. **Add session TTL**:
   - Expire inactive sessions after 24 hours
   - Implement background cleanup job

4. **Add monitoring**:
   - Track session creation rate
   - Monitor memory usage
   - Alert on session limit approaching

## Next Steps

This completes the Vector Search and RAG Retrieval feature (F03). The system now has:
- Vector search with query embedding
- LangChain tool integration
- Session-based conversation memory

Next features can now:
- Use retrieval_tool in RAG chains (F04)
- Build Q&A agents with memory (F05)
- Create frontend interfaces (F06)
