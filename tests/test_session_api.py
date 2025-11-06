"""Tests for session API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.memory import get_memory_service
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
    # Add interaction directly to service
    service = get_memory_service()
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
    service = get_memory_service()
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


def test_get_session_returns_pinned_passages():
    """Test that GET /session/{id} includes pinned passages."""
    service = get_memory_service()
    session_id = str(uuid.uuid4())

    # Add some pinned passages
    service.pin_passage(session_id, "passage_1")
    service.pin_passage(session_id, "passage_2")

    response = client.get(f"/session/{session_id}")

    assert response.status_code == 200
    data = response.json()
    assert "pinned" in data
    assert len(data["pinned"]) == 2
    assert "passage_1" in data["pinned"]
    assert "passage_2" in data["pinned"]


def test_session_response_includes_timestamps():
    """Test that session response includes created_at and updated_at."""
    service = get_memory_service()
    session_id = str(uuid.uuid4())
    service.add_interaction(session_id, "Test", "Response")

    response = client.get(f"/session/{session_id}")

    assert response.status_code == 200
    data = response.json()
    assert "created_at" in data
    assert "updated_at" in data
    # Should be ISO format strings
    assert isinstance(data["created_at"], str)
    assert isinstance(data["updated_at"], str)
