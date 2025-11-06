"""Session management API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.services.memory import get_memory_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/session", tags=["session"])


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

    logger.info(f"Retrieved session {session_id}: {len(session.history)} messages")

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
        Status confirmation
    """
    service = get_memory_service()
    service.clear_session(session_id)

    logger.info(f"Cleared session {session_id}")

    return ClearSessionResponse(
        status="cleared",
        session_id=session_id
    )
