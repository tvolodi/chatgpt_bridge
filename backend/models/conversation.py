"""
Conversation Service Data Models

This module defines the Pydantic models for conversation management,
bridging chat sessions with AI providers for actual conversation flow.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict


class ConversationMessage(BaseModel):
    """Represents a message in a conversation with AI context."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the message")
    session_id: UUID = Field(..., description="Chat session this message belongs to")
    role: str = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="The actual message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the message was created")
    model: Optional[str] = Field(None, description="AI model used for generation (for assistant messages)")
    provider_id: Optional[UUID] = Field(None, description="AI provider used (for assistant messages)")
    usage: Optional[Dict[str, int]] = Field(None, description="Token usage statistics (for assistant messages)")
    finish_reason: Optional[str] = Field(None, description="Reason generation finished (for assistant messages)")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional message metadata")

    def __str__(self) -> str:
        return f"ConversationMessage(id={self.id}, role={self.role}, content={self.content[:50]}...)"


class ConversationContext(BaseModel):
    """Context information for a conversation."""

    model_config = ConfigDict(from_attributes=True)

    session_id: UUID = Field(..., description="Chat session ID")
    message_count: int = Field(default=0, description="Total messages in the conversation")
    last_message_at: Optional[datetime] = Field(None, description="When the last message was sent")
    total_tokens_input: int = Field(default=0, description="Total input tokens used")
    total_tokens_output: int = Field(default=0, description="Total output tokens used")
    total_cost: float = Field(default=0.0, description="Total conversation cost")
    preferred_model: Optional[str] = Field(None, description="Preferred AI model for this conversation")
    preferred_provider_id: Optional[UUID] = Field(None, description="Preferred AI provider for this conversation")
    system_prompt: Optional[str] = Field(None, description="System prompt for this conversation")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context metadata")


class ConversationRequest(BaseModel):
    """Request model for sending a message in a conversation."""

    session_id: UUID = Field(..., description="Chat session ID")
    message: str = Field(..., min_length=1, description="User message to send")
    model: Optional[str] = Field(None, description="Specific AI model to use")
    provider_id: Optional[UUID] = Field(None, description="Specific AI provider to use")
    max_tokens: Optional[int] = Field(None, ge=1, le=4096, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Sampling temperature")
    system_prompt: Optional[str] = Field(None, description="Override system prompt for this message")
    include_history: bool = Field(default=True, description="Whether to include conversation history")
    max_history_messages: Optional[int] = Field(None, ge=1, le=100, description="Maximum history messages to include")


class ConversationResponse(BaseModel):
    """Response model for conversation messages."""

    model_config = ConfigDict(from_attributes=True)

    session_id: UUID = Field(..., description="Chat session ID")
    user_message_id: UUID = Field(..., description="ID of the user message")
    ai_message_id: UUID = Field(..., description="ID of the AI response message")
    content: str = Field(..., description="AI generated response")
    model: str = Field(..., description="AI model used")
    provider_id: UUID = Field(..., description="AI provider used")
    usage: Dict[str, int] = Field(..., description="Token usage statistics")
    finish_reason: str = Field(..., description="Reason generation finished")
    created_at: datetime = Field(default_factory=datetime.now, description="When the response was created")
    conversation_context: ConversationContext = Field(..., description="Updated conversation context")


class ConversationHistory(BaseModel):
    """Conversation history with messages and context."""

    model_config = ConfigDict(from_attributes=True)

    session_id: UUID = Field(..., description="Chat session ID")
    context: ConversationContext = Field(..., description="Conversation context")
    messages: List[ConversationMessage] = Field(..., description="Conversation messages")
    total_messages: int = Field(..., description="Total number of messages")
    has_more: bool = Field(default=False, description="Whether there are more messages available")


class ConversationStats(BaseModel):
    """Statistics for conversations."""

    total_conversations: int = Field(..., description="Total number of conversations")
    active_conversations: int = Field(..., description="Number of active conversations")
    total_messages: int = Field(..., description="Total messages across all conversations")
    total_tokens_input: int = Field(..., description="Total input tokens used")
    total_tokens_output: int = Field(..., description="Total output tokens used")
    total_cost: float = Field(default=0.0, description="Total cost across all conversations")
    average_response_time: float = Field(..., description="Average response time in seconds")
    conversations_by_provider: Dict[str, int] = Field(default_factory=dict, description="Conversations by provider")
    messages_by_model: Dict[str, int] = Field(default_factory=dict, description="Messages by model")


class ConversationSettings(BaseModel):
    """Settings for conversation behavior."""

    default_model: Optional[str] = Field(None, description="Default AI model to use")
    default_provider_id: Optional[UUID] = Field(None, description="Default AI provider to use")
    default_max_tokens: int = Field(default=1000, ge=1, le=4096, description="Default maximum tokens")
    default_temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Default sampling temperature")
    default_system_prompt: Optional[str] = Field(None, description="Default system prompt")
    max_history_messages: int = Field(default=50, ge=1, le=100, description="Maximum history messages to include")
    enable_cost_tracking: bool = Field(default=True, description="Whether to track conversation costs")
    enable_usage_stats: bool = Field(default=True, description="Whether to collect usage statistics")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional settings")


class ConversationError(BaseModel):
    """Error model for conversation operations."""

    type: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    session_id: Optional[UUID] = Field(None, description="Chat session ID if applicable")
    provider_id: Optional[UUID] = Field(None, description="AI provider ID if applicable")
    retry_after: Optional[int] = Field(None, description="Seconds to wait before retrying")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional error metadata")