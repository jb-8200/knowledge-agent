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
