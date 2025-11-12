"""
AI Provider API Endpoints

This module provides RESTful API endpoints for managing AI providers
and handling AI communication within the AI Chat Assistant backend.
"""

from typing import List, Optional, Union
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse

from ..models.ai_provider import (
    AIProvider, AIProviderCreate, AIProviderUpdate, AIModel, AIRequest, AIResponse,
    AIError, AIProviderSummary, AIUsageStats, AIProviderHealth, AIConversationRequest,
    AIConversationResponse, ProviderType
)
from ..services.ai_provider_service import AIProviderService

# Create the router
router = APIRouter(prefix="/api/ai-providers", tags=["ai-providers"])

# Global singleton instance of the AI provider service
_ai_provider_service_instance: Optional[AIProviderService] = None

def get_ai_provider_service() -> AIProviderService:
    """Dependency to get the AI provider service instance (singleton pattern)."""
    global _ai_provider_service_instance
    if _ai_provider_service_instance is None:
        _ai_provider_service_instance = AIProviderService()
    return _ai_provider_service_instance


@router.post("/", response_model=AIProvider, status_code=201)
async def create_ai_provider(
    provider_data: AIProviderCreate,
    service: AIProviderService = Depends(get_ai_provider_service)
) -> AIProvider:
    """
    Create a new AI provider.

    - **name**: Provider name (e.g., 'OpenAI', 'Anthropic')
    - **provider_type**: Type of AI provider
    - **api_key**: API key for authentication
    - **base_url**: Optional custom base URL
    - **organization_id**: Optional organization ID
    - **rate_limit_requests**: Requests per minute limit (default: 60)
    - **rate_limit_tokens**: Tokens per minute limit (default: 100000)
    - **timeout_seconds**: Request timeout in seconds (default: 30)
    - **retry_attempts**: Number of retry attempts (default: 3)
    """
    try:
        provider = service.create_provider(provider_data)
        return provider
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create AI provider: {str(e)}")


@router.get("/{provider_id}", response_model=AIProvider)
async def get_ai_provider(
    provider_id: UUID,
    service: AIProviderService = Depends(get_ai_provider_service)
) -> AIProvider:
    """
    Get an AI provider by ID.

    - **provider_id**: UUID of the AI provider to retrieve
    """
    provider = service.get_provider(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail=f"AI provider {provider_id} not found")
    return provider


@router.get("/", response_model=List[AIProviderSummary])
async def list_ai_providers(
    include_inactive: bool = Query(False, description="Include inactive providers"),
    service: AIProviderService = Depends(get_ai_provider_service)
) -> List[AIProviderSummary]:
    """
    List all AI providers.

    - **include_inactive**: Whether to include inactive providers (default: false)
    """
    try:
        providers = service.list_providers(include_inactive=include_inactive)
        return providers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list AI providers: {str(e)}")


@router.put("/{provider_id}", response_model=AIProvider)
async def update_ai_provider(
    provider_id: UUID,
    update_data: AIProviderUpdate,
    service: AIProviderService = Depends(get_ai_provider_service)
) -> AIProvider:
    """
    Update an existing AI provider.

    - **provider_id**: UUID of the AI provider to update
    - **name**: Optional updated provider name
    - **api_key**: Optional updated API key
    - **base_url**: Optional updated base URL
    - **organization_id**: Optional updated organization ID
    - **is_active**: Optional updated active status
    - **rate_limit_requests**: Optional updated requests per minute limit
    - **rate_limit_tokens**: Optional updated tokens per minute limit
    - **timeout_seconds**: Optional updated timeout
    - **retry_attempts**: Optional updated retry attempts
    """
    try:
        provider = service.update_provider(provider_id, update_data)
        if not provider:
            raise HTTPException(status_code=404, detail=f"AI provider {provider_id} not found")
        return provider
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update AI provider: {str(e)}")


@router.delete("/{provider_id}")
async def delete_ai_provider(
    provider_id: UUID,
    service: AIProviderService = Depends(get_ai_provider_service)
) -> JSONResponse:
    """
    Delete an AI provider.

    - **provider_id**: UUID of the AI provider to delete
    """
    try:
        deleted = service.delete_provider(provider_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"AI provider {provider_id} not found")
        return JSONResponse(
            status_code=200,
            content={"message": f"AI provider {provider_id} deleted successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete AI provider: {str(e)}")


@router.get("/models/available", response_model=List[AIModel])
async def get_available_models(
    provider_type: Optional[ProviderType] = Query(None, description="Filter by provider type"),
    service: AIProviderService = Depends(get_ai_provider_service)
) -> List[AIModel]:
    """
    Get available AI models.

    - **provider_type**: Optional filter by provider type (openai, anthropic, etc.)
    """
    try:
        models = service.get_available_models(provider_type=provider_type)
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available models: {str(e)}")


@router.post("/{provider_id}/request", response_model=Union[AIResponse, AIError])
async def send_ai_request(
    provider_id: UUID,
    request: AIRequest,
    service: AIProviderService = Depends(get_ai_provider_service)
) -> Union[AIResponse, AIError]:
    """
    Send a request to an AI provider.

    - **provider_id**: UUID of the AI provider to use
    - **model**: Model identifier to use
    - **messages**: Conversation messages
    - **max_tokens**: Optional maximum tokens to generate
    - **temperature**: Sampling temperature (0.0-2.0, default: 0.7)
    - **top_p**: Optional top-p sampling parameter
    - **frequency_penalty**: Frequency penalty (-2.0-2.0, default: 0.0)
    - **presence_penalty**: Presence penalty (-2.0-2.0, default: 0.0)
    - **stop**: Optional stop sequences
    - **functions**: Optional function definitions
    - **function_call**: Optional function call specification
    """
    try:
        async with service:
            response = await service.send_request(provider_id, request)
            return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send AI request: {str(e)}")


@router.get("/{provider_id}/usage", response_model=AIUsageStats)
async def get_provider_usage(
    provider_id: UUID,
    service: AIProviderService = Depends(get_ai_provider_service)
) -> AIUsageStats:
    """
    Get usage statistics for a specific provider.

    - **provider_id**: UUID of the AI provider
    """
    try:
        stats = service.get_usage_stats(provider_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get usage stats: {str(e)}")


@router.get("/usage/all", response_model=List[AIUsageStats])
async def get_all_usage_stats(
    service: AIProviderService = Depends(get_ai_provider_service)
) -> List[AIUsageStats]:
    """
    Get usage statistics for all providers.
    """
    try:
        stats = service.get_usage_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get usage stats: {str(e)}")


@router.get("/{provider_id}/health", response_model=AIProviderHealth)
async def get_provider_health(
    provider_id: UUID,
    service: AIProviderService = Depends(get_ai_provider_service)
) -> AIProviderHealth:
    """
    Get health status for a specific provider.

    - **provider_id**: UUID of the AI provider
    """
    try:
        health = service.get_health_status(provider_id)
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get health status: {str(e)}")


@router.post("/{provider_id}/health/check", response_model=AIProviderHealth)
async def check_provider_health(
    provider_id: UUID,
    background_tasks: BackgroundTasks,
    service: AIProviderService = Depends(get_ai_provider_service)
) -> AIProviderHealth:
    """
    Check the health of a specific provider.

    - **provider_id**: UUID of the AI provider to check
    """
    try:
        async with service:
            health = await service.check_provider_health(provider_id)
            return health
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check provider health: {str(e)}")


@router.get("/health/all", response_model=List[AIProviderHealth])
async def get_all_health_status(
    service: AIProviderService = Depends(get_ai_provider_service)
) -> List[AIProviderHealth]:
    """
    Get health status for all providers.
    """
    try:
        health_status = service.get_health_status()
        return health_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get health status: {str(e)}")


@router.post("/conversation", response_model=AIConversationResponse)
async def send_conversation_message(
    request: AIConversationRequest,
    service: AIProviderService = Depends(get_ai_provider_service)
) -> AIConversationResponse:
    """
    Send a conversation message to an AI provider.

    This is a high-level endpoint that handles the full conversation flow
    including message persistence and provider selection.

    - **session_id**: Chat session ID
    - **message**: User message to send to AI
    - **model**: Optional specific model to use
    - **provider_id**: Optional specific provider to use
    - **max_tokens**: Optional maximum tokens to generate
    - **temperature**: Optional sampling temperature
    - **system_prompt**: Optional system prompt to use
    """
    # This would integrate with the chat session service
    # For now, return a placeholder response
    raise HTTPException(
        status_code=501,
        detail="Conversation endpoint not yet implemented - requires chat session integration"
    )