"""Tests for memory service."""

import pytest
from datetime import datetime
from app.services.memory import MemoryService, SessionMemory, get_langchain_memory
import uuid
import time


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

    time.sleep(0.01)  # Small delay

    service.add_interaction(session_id, "Query", "Response")
    session2 = service.get_or_create_session(session_id)

    assert session2.updated_at > initial_updated


def test_langchain_memory_integration():
    """Test LangChain ConversationBufferMemory wrapper."""
    from app.services.memory import get_memory_service

    service = get_memory_service()
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


def test_pin_passage():
    """Test pinning passages for reference."""
    service = MemoryService()
    session_id = str(uuid.uuid4())

    service.pin_passage(session_id, "passage_123")
    service.pin_passage(session_id, "passage_456")

    pinned = service.get_pinned_passages(session_id)
    assert len(pinned) == 2
    assert "passage_123" in pinned
    assert "passage_456" in pinned


def test_pin_passage_no_duplicates():
    """Test that pinning same passage twice doesn't duplicate."""
    service = MemoryService()
    session_id = str(uuid.uuid4())

    service.pin_passage(session_id, "passage_123")
    service.pin_passage(session_id, "passage_123")

    pinned = service.get_pinned_passages(session_id)
    assert len(pinned) == 1
