"""
AI Provider Data Models

This module defines the Pydantic models for AI providers, models, and API
communication within the AI Chat Assistant backend.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class ProviderType(str, Enum):
    """Supported AI provider types."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"


class AIModel(BaseModel):
    """Represents an AI model within a provider."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Model identifier (e.g., 'gpt-4', 'claude-3-sonnet')")
    name: str = Field(..., description="Human-readable model name")
    provider_type: ProviderType = Field(..., description="The provider this model belongs to")
    context_window: int = Field(..., description="Maximum context window in tokens")
    max_tokens: int = Field(..., description="Maximum output tokens")
    supports_functions: bool = Field(default=False, description="Whether the model supports function calling")
    supports_vision: bool = Field(default=False, description="Whether the model supports vision/image inputs")
    input_pricing: float = Field(..., description="Cost per 1K input tokens (USD)")
    output_pricing: float = Field(..., description="Cost per 1K output tokens (USD)")
    is_active: bool = Field(default=True, description="Whether this model is currently available")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional model metadata")


class AIProvider(BaseModel):
    """Represents an AI provider configuration."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the provider")
    name: str = Field(..., description="Provider name (e.g., 'OpenAI', 'Anthropic')")
    provider_type: ProviderType = Field(..., description="Type of AI provider")
    api_key: str = Field(..., description="API key for authentication")
    base_url: Optional[str] = Field(None, description="Custom base URL for API calls")
    organization_id: Optional[str] = Field(None, description="Organization ID for enterprise accounts")
    is_active: bool = Field(default=True, description="Whether this provider is currently active")
    rate_limit_requests: int = Field(default=60, description="Requests per minute limit")
    rate_limit_tokens: int = Field(default=100000, description="Tokens per minute limit")
    timeout_seconds: int = Field(default=30, description="Request timeout in seconds")
    retry_attempts: int = Field(default=3, description="Number of retry attempts for failed requests")
    created_at: datetime = Field(default_factory=datetime.now, description="When the provider was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="When the provider was last updated")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional provider metadata")


class AIProviderCreate(BaseModel):
    """Model for creating a new AI provider."""

    name: str = Field(..., min_length=1, max_length=100, description="Provider name")
    provider_type: ProviderType = Field(..., description="Type of AI provider")
    api_key: str = Field(..., min_length=1, description="API key for authentication")
    base_url: Optional[str] = Field(None, description="Custom base URL for API calls")
    organization_id: Optional[str] = Field(None, description="Organization ID for enterprise accounts")
    rate_limit_requests: int = Field(default=60, ge=1, description="Requests per minute limit")
    rate_limit_tokens: int = Field(default=100000, ge=1, description="Tokens per minute limit")
    timeout_seconds: int = Field(default=30, ge=1, le=300, description="Request timeout in seconds")
    retry_attempts: int = Field(default=3, ge=0, le=10, description="Number of retry attempts")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional provider metadata")


class AIProviderUpdate(BaseModel):
    """Model for updating an existing AI provider."""

    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Updated provider name")
    api_key: Optional[str] = Field(None, min_length=1, description="Updated API key")
    base_url: Optional[str] = Field(None, description="Updated base URL")
    organization_id: Optional[str] = Field(None, description="Updated organization ID")
    is_active: Optional[bool] = Field(None, description="Updated active status")
    rate_limit_requests: Optional[int] = Field(None, ge=1, description="Updated requests per minute limit")
    rate_limit_tokens: Optional[int] = Field(None, ge=1, description="Updated tokens per minute limit")
    timeout_seconds: Optional[int] = Field(None, ge=1, le=300, description="Updated timeout")
    retry_attempts: Optional[int] = Field(None, ge=0, le=10, description="Updated retry attempts")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")


class AIRequest(BaseModel):
    """Model for AI API requests."""

    model: str = Field(..., description="Model identifier to use")
    messages: List[Dict[str, Any]] = Field(..., description="Conversation messages")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Top-p sampling parameter")
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0, description="Frequency penalty")
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0, description="Presence penalty")
    stop: Optional[Union[str, List[str]]] = Field(None, description="Stop sequences")
    functions: Optional[List[Dict[str, Any]]] = Field(None, description="Function definitions for function calling")
    function_call: Optional[Union[str, Dict[str, Any]]] = Field(None, description="Function call specification")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional request metadata")


class AIResponse(BaseModel):
    """Model for AI API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Response identifier")
    model: str = Field(..., description="Model used for generation")
    content: str = Field(..., description="Generated content")
    finish_reason: str = Field(..., description="Reason the generation finished")
    usage: Dict[str, int] = Field(..., description="Token usage statistics")
    created_at: datetime = Field(default_factory=datetime.now, description="When the response was created")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional response metadata")


class AIError(BaseModel):
    """Model for AI API errors."""

    model_config = ConfigDict(from_attributes=True)

    type: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")
    param: Optional[str] = Field(None, description="Parameter that caused the error")
    retry_after: Optional[int] = Field(None, description="Seconds to wait before retrying")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional error metadata")


class AIProviderSummary(BaseModel):
    """Summary representation of an AI provider."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Provider ID")
    name: str = Field(..., description="Provider name")
    provider_type: ProviderType = Field(..., description="Provider type")
    is_active: bool = Field(..., description="Whether the provider is active")
    models_count: int = Field(..., description="Number of available models")
    created_at: datetime = Field(..., description="When the provider was created")


class AIUsageStats(BaseModel):
    """Statistics for AI provider usage."""

    provider_id: UUID = Field(..., description="Provider ID")
    total_requests: int = Field(default=0, description="Total number of requests")
    total_tokens_input: int = Field(default=0, description="Total input tokens used")
    total_tokens_output: int = Field(default=0, description="Total output tokens used")
    total_cost: float = Field(default=0.0, description="Total cost in USD")
    average_response_time: float = Field(default=0.0, description="Average response time in seconds")
    error_rate: float = Field(default=0.0, description="Error rate as percentage")
    last_used: Optional[datetime] = Field(None, description="When the provider was last used")


class AIProviderHealth(BaseModel):
    """Health status of an AI provider."""

    provider_id: UUID = Field(..., description="Provider ID")
    status: str = Field(..., description="Health status (healthy, degraded, unhealthy)")
    last_check: datetime = Field(..., description="When health was last checked")
    response_time: Optional[float] = Field(None, description="Last response time in seconds")
    error_message: Optional[str] = Field(None, description="Last error message if any")
    consecutive_failures: int = Field(default=0, description="Number of consecutive failures")


class AIConversationRequest(BaseModel):
    """Request model for AI conversation within a chat session."""

    session_id: UUID = Field(..., description="Chat session ID")
    message: str = Field(..., description="User message to send to AI")
    model: Optional[str] = Field(None, description="Specific model to use (optional)")
    provider_id: Optional[UUID] = Field(None, description="Specific provider to use (optional)")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Sampling temperature")
    system_prompt: Optional[str] = Field(None, description="System prompt to use")


class AIConversationResponse(BaseModel):
    """Response model for AI conversation."""

    session_id: UUID = Field(..., description="Chat session ID")
    message_id: UUID = Field(..., description="ID of the AI response message")
    content: str = Field(..., description="AI generated response")
    model: str = Field(..., description="Model used")
    provider_id: UUID = Field(..., description="Provider used")
    usage: Dict[str, int] = Field(..., description="Token usage statistics")
    finish_reason: str = Field(..., description="Reason generation finished")
    created_at: datetime = Field(default_factory=datetime.now, description="When the response was created")