"""
Chat Session API Endpoints

This module provides RESTful API endpoints for managing chat sessions
and their messages within the AI Chat Assistant backend.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse

from ..models.chat_session import (
    ChatSession, ChatSessionCreate, ChatSessionUpdate, Message, MessageCreate,
    ChatSessionSummary, ChatSessionStats, ChatSessionWithMessages
)
from ..services.chat_session_service import ChatSessionService

# Create the router
router = APIRouter(prefix="/api/chat-sessions", tags=["chat-sessions"])

# Dependency to get the chat session service
def get_chat_session_service() -> ChatSessionService:
    """Dependency to get the chat session service instance."""
    return ChatSessionService()


@router.post("/", response_model=ChatSession, status_code=201)
async def create_chat_session(
    session_data: ChatSessionCreate,
    service: ChatSessionService = Depends(get_chat_session_service)
) -> ChatSession:
    """
    Create a new chat session.

    - **project_id**: UUID of the project this session belongs to
    - **title**: Display title for the session (1-200 characters)
    - **description**: Optional description (max 1000 characters)
    - **metadata**: Optional additional metadata
    """
    try:
        session = service.create_session(session_data)
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chat session: {str(e)}")


@router.get("/{session_id}", response_model=ChatSession)
async def get_chat_session(
    session_id: UUID,
    project_id: Optional[str] = Query(None, description="Project ID for nested structure"),
    service: ChatSessionService = Depends(get_chat_session_service)
) -> ChatSession:
    """
    Get a chat session by ID.

    - **session_id**: UUID of the chat session to retrieve
    - **project_id**: Optional project ID for nested directory structure
    """
    session = service.get_session(session_id, project_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found")
    return session


@router.get("/", response_model=List[ChatSessionSummary])
async def list_chat_sessions(
    project_id: Optional[UUID] = Query(None, description="Filter by project ID"),
    include_inactive: bool = Query(False, description="Include inactive sessions"),
    service: ChatSessionService = Depends(get_chat_session_service)
) -> List[ChatSessionSummary]:
    """
    List chat sessions with optional filtering.

    - **project_id**: Optional UUID to filter sessions by project
    - **include_inactive**: Whether to include inactive sessions (default: false)
    """
    try:
        sessions = service.list_sessions(project_id=project_id, include_inactive=include_inactive)
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list chat sessions: {str(e)}")


@router.put("/{session_id}", response_model=ChatSession)
async def update_chat_session(
    session_id: UUID,
    update_data: ChatSessionUpdate,
    project_id: Optional[str] = Query(None, description="Project ID for nested structure"),
    service: ChatSessionService = Depends(get_chat_session_service)
) -> ChatSession:
    """
    Update an existing chat session.

    - **session_id**: UUID of the chat session to update
    - **project_id**: Optional project ID for nested directory structure
    - **title**: Optional new title (1-200 characters)
    - **description**: Optional new description (max 1000 characters)
    - **is_active**: Optional active status
    - **metadata**: Optional updated metadata
    """
    try:
        session = service.update_session(session_id, update_data, project_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found")
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update chat session: {str(e)}")


@router.delete("/{session_id}")
async def delete_chat_session(
    session_id: UUID,
    force: bool = Query(False, description="Force deletion even with messages"),
    project_id: Optional[str] = Query(None, description="Project ID for nested structure"),
    service: ChatSessionService = Depends(get_chat_session_service)
) -> JSONResponse:
    """
    Delete a chat session and all its messages.

    - **session_id**: UUID of the chat session to delete
    - **project_id**: Optional project ID for nested directory structure
    - **force**: Force deletion even if session has messages (default: false)
    """
    try:
        deleted = service.delete_session(session_id, force=force, project_id=project_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found")
        return JSONResponse(
            status_code=200,
            content={"message": f"Chat session {session_id} deleted successfully"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete chat session: {str(e)}")


@router.post("/{session_id}/messages", response_model=Message, status_code=201)
async def add_message_to_session(
    session_id: UUID,
    message_data: MessageCreate,
    project_id: Optional[str] = Query(None, description="Project ID for nested structure"),
    service: ChatSessionService = Depends(get_chat_session_service)
) -> Message:
    """
    Add a message to a chat session.

    - **session_id**: UUID of the chat session
    - **project_id**: Optional project ID for nested directory structure
    - **role**: Role of the message sender (user, assistant, system)
    - **content**: The message content
    - **metadata**: Optional additional metadata
    """
    try:
        message = service.add_message(session_id, message_data, project_id)
        return message
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add message: {str(e)}")


@router.get("/{session_id}/messages", response_model=List[Message])
async def get_session_messages(
    session_id: UUID,
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Maximum number of messages to return"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    project_id: Optional[str] = Query(None, description="Project ID for nested structure"),
    service: ChatSessionService = Depends(get_chat_session_service)
) -> List[Message]:
    """
    Get messages for a chat session.

    - **session_id**: UUID of the chat session
    - **project_id**: Optional project ID for nested directory structure
    - **limit**: Optional limit on number of messages (1-1000)
    - **offset**: Number of messages to skip from the beginning
    """
    try:
        messages = service.get_messages(session_id, limit=limit, offset=offset, project_id=project_id)
        return messages
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")


@router.get("/{session_id}/full", response_model=ChatSessionWithMessages)
async def get_session_with_messages(
    session_id: UUID,
    project_id: Optional[str] = Query(None, description="Project ID for nested structure"),
    service: ChatSessionService = Depends(get_chat_session_service)
) -> ChatSessionWithMessages:
    """
    Get a chat session with its full message history.

    - **session_id**: UUID of the chat session to retrieve
    - **project_id**: Optional project ID for nested directory structure
    """
    try:
        session_with_messages = service.get_session_with_messages(session_id, project_id)
        if not session_with_messages:
            raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found")
        return session_with_messages
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session with messages: {str(e)}")


@router.get("/stats/summary", response_model=ChatSessionStats)
async def get_chat_session_stats(
    project_id: Optional[UUID] = Query(None, description="Filter stats by project ID"),
    service: ChatSessionService = Depends(get_chat_session_service)
) -> ChatSessionStats:
    """
    Get statistics for chat sessions.

    - **project_id**: Optional UUID to filter stats by project
    """
    try:
        stats = service.get_session_stats(project_id=project_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session stats: {str(e)}")