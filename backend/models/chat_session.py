"""
Chat Session Data Models

This module defines the Pydantic models for chat sessions and messages
within the AI Chat Assistant backend.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict


class Message(BaseModel):
    """Represents a single message in a chat session."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the message")
    role: str = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="The actual message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the message was created")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional message metadata")

    def __str__(self) -> str:
        return f"Message(id={self.id}, role={self.role}, content={self.content[:50]}...)"


class ChatSession(BaseModel):
    """Represents a chat session within a project."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the chat session")
    project_id: Optional[UUID] = Field(None, description="ID of the project this session belongs to (optional for backwards compatibility)")
    title: str = Field(..., min_length=1, max_length=200, description="Display title for the session")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description of the session")
    created_at: datetime = Field(default_factory=datetime.now, description="When the session was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="When the session was last updated")
    is_active: bool = Field(default=True, description="Whether the session is currently active")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional session metadata")
    message_count: int = Field(default=0, description="Number of messages in the session")

    def __str__(self) -> str:
        return f"ChatSession(id={self.id}, title={self.title}, project_id={self.project_id})"


class ChatSessionCreate(BaseModel):
    """Model for creating a new chat session."""

    project_id: Optional[UUID] = Field(None, description="ID of the project this session belongs to (optional for backwards compatibility)")
    title: str = Field(..., min_length=1, max_length=200, description="Display title for the session")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description of the session")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional session metadata")


class ChatSessionUpdate(BaseModel):
    """Model for updating an existing chat session."""

    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Updated title for the session")
    description: Optional[str] = Field(None, max_length=1000, description="Updated description of the session")
    is_active: Optional[bool] = Field(None, description="Updated active status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated session metadata")


class MessageCreate(BaseModel):
    """Model for creating a new message in a chat session."""

    role: str = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="The actual message content")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional message metadata")


class ChatSessionSummary(BaseModel):
    """Summary representation of a chat session for listing."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique identifier for the chat session")
    project_id: UUID = Field(..., description="ID of the project this session belongs to")
    title: str = Field(..., description="Display title for the session")
    created_at: datetime = Field(..., description="When the session was created")
    updated_at: datetime = Field(..., description="When the session was last updated")
    is_active: bool = Field(..., description="Whether the session is currently active")
    message_count: int = Field(..., description="Number of messages in the session")
    last_message_preview: Optional[str] = Field(None, description="Preview of the last message content")


class ChatSessionStats(BaseModel):
    """Statistics for chat sessions."""

    total_sessions: int = Field(..., description="Total number of chat sessions")
    active_sessions: int = Field(..., description="Number of active sessions")
    total_messages: int = Field(..., description="Total number of messages across all sessions")
    average_messages_per_session: float = Field(..., description="Average number of messages per session")
    sessions_by_project: Dict[str, int] = Field(default_factory=dict, description="Session count by project")


class ChatSessionWithMessages(BaseModel):
    """Chat session with full message history."""

    model_config = ConfigDict(from_attributes=True)

    session: ChatSession = Field(..., description="The chat session details")
    messages: List[Message] = Field(default_factory=list, description="All messages in the session")

    def __str__(self) -> str:
        return f"ChatSessionWithMessages(session={self.session}, messages={len(self.messages)})"