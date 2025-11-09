"""
Conversation API Endpoints

This module provides REST API endpoints for conversation management,
bridging chat sessions with AI providers for actual conversation flow.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Union
from uuid import UUID

from ..models.conversation import (
    ConversationRequest,
    ConversationResponse,
    ConversationHistory,
    ConversationStats,
    ConversationSettings,
    ConversationError
)
from ..services.conversation_service import ConversationService

router = APIRouter()


def get_conversation_service() -> ConversationService:
    """Dependency to get conversation service instance."""
    return ConversationService()


@router.post("/send", response_model=Union[ConversationResponse, ConversationError])
async def send_message(
    request: ConversationRequest,
    service: ConversationService = Depends(get_conversation_service)
):
    """
    Send a message in a conversation and get AI response.

    This endpoint handles the core conversation flow:
    1. Validates the chat session exists
    2. Prepares conversation context and history
    3. Sends request to AI provider
    4. Stores both user and AI messages
    5. Updates conversation statistics

    Args:
        request: Conversation request with message and settings
        service: Conversation service instance

    Returns:
        Conversation response with AI reply or error
    """
    result = await service.send_message(request)

    if isinstance(result, ConversationError):
        # Convert conversation error to HTTP exception
        status_code = 400
        if result.type in ["provider_error", "rate_limit_exceeded"]:
            status_code = 429 if result.retry_after else 502
        elif result.type == "session_not_found":
            status_code = 404

        raise HTTPException(
            status_code=status_code,
            detail=result.message,
            headers={"Retry-After": str(result.retry_after)} if result.retry_after else None
        )

    return result


@router.get("/history/{session_id}", response_model=ConversationHistory)
async def get_conversation_history(
    session_id: UUID,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    service: ConversationService = Depends(get_conversation_service)
):
    """
    Get the conversation history for a chat session.

    Args:
        session_id: Chat session ID
        limit: Maximum number of messages to return
        offset: Number of messages to skip
        service: Conversation service instance

    Returns:
        Conversation history with messages and context
    """
    try:
        return service.get_conversation_history(session_id, limit, offset)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/stats", response_model=ConversationStats)
async def get_conversation_stats(
    service: ConversationService = Depends(get_conversation_service)
):
    """
    Get statistics for all conversations.

    Returns:
        Conversation statistics including usage, costs, and activity metrics
    """
    try:
        return service.get_conversation_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/settings", response_model=ConversationSettings)
async def get_conversation_settings(
    service: ConversationService = Depends(get_conversation_service)
):
    """
    Get current conversation settings.

    Returns:
        Current conversation settings
    """
    try:
        return service.get_conversation_settings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.put("/settings", response_model=ConversationSettings)
async def update_conversation_settings(
    settings: ConversationSettings,
    service: ConversationService = Depends(get_conversation_service)
):
    """
    Update conversation settings.

    Args:
        settings: New conversation settings
        service: Conversation service instance

    Returns:
        Updated conversation settings
    """
    try:
        service.update_conversation_settings(settings)
        return service.get_conversation_settings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.delete("/context/{session_id}")
async def clear_conversation_context(
    session_id: UUID,
    service: ConversationService = Depends(get_conversation_service)
):
    """
    Clear the conversation context for a session.

    This removes cached context data but preserves the actual messages
    in the chat session. Useful for resetting conversation state.

    Args:
        session_id: Chat session ID
        service: Conversation service instance

    Returns:
        Success status
    """
    try:
        cleared = service.clear_conversation_context(session_id)
        if not cleared:
            raise HTTPException(status_code=404, detail=f"Conversation context for session {session_id} not found")

        return {"status": "cleared", "session_id": str(session_id)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")