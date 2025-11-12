"""
Chat Session API Endpoints

This module provides RESTful API endpoints for managing chat sessions
nested within projects, as per BACKEND_SERVICES_PLAN.md.

API Structure:
- POST   /api/projects/{project_id}/sessions              - Create new session
- GET    /api/projects/{project_id}/sessions              - List sessions in project
- GET    /api/projects/{project_id}/sessions/{session_id} - Get session details
- PUT    /api/projects/{project_id}/sessions/{session_id} - Update session
- DELETE /api/projects/{project_id}/sessions/{session_id} - Delete session
- POST   /api/projects/{project_id}/sessions/{session_id}/messages - Add message
- GET    /api/projects/{project_id}/sessions/{session_id}/messages - Get messages
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse

from ..models.chat_session import (
    ChatSession, ChatSessionCreate, ChatSessionUpdate, Message, MessageCreate,
    ChatSessionSummary, ChatSessionWithMessages
)
from ..services.chat_session_service import ChatSessionService

# Create the router for project-nested sessions
# This will be included with prefix /api/projects in main.py
router = APIRouter(tags=["chat-sessions"])

# Dependency to get the chat session service
def get_chat_session_service() -> ChatSessionService:
    """Dependency to get the chat session service instance."""
    return ChatSessionService()


@router.post("/{project_id}/sessions", response_model=ChatSession, status_code=201)
async def create_chat_session(
    project_id: UUID,
    session_data: ChatSessionCreate,
    service: ChatSessionService = Depends(get_chat_session_service)
) -> ChatSession:
    """
    Create a new chat session within a project.

    **Path Parameters:**
    - **project_id**: UUID of the parent project

    **Request Body:**
    - **title**: Display title for the session (1-200 characters)
    - **description**: Optional description (max 1000 characters)
    - **metadata**: Optional additional metadata

    **Returns:**
    - Created ChatSession object
    """
    try:
        # Ensure project_id is set in the session data
        session_data.project_id = project_id
        session = service.create_session(session_data)
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chat session: {str(e)}")


@router.get("/{project_id}/sessions", response_model=List[ChatSessionSummary])
async def list_sessions_in_project(
    project_id: UUID,
    include_inactive: bool = Query(False, description="Include inactive sessions"),
    service: ChatSessionService = Depends(get_chat_session_service)
) -> List[ChatSessionSummary]:
    """
    List all chat sessions within a specific project.

    **Path Parameters:**
    - **project_id**: UUID of the parent project

    **Query Parameters:**
    - **include_inactive**: Whether to include inactive sessions (default: false)

    **Returns:**
    - List of ChatSessionSummary objects for the project
    """
    try:
        sessions = service.list_sessions(project_id=project_id, include_inactive=include_inactive)
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list chat sessions: {str(e)}")


@router.get("/{project_id}/sessions/{session_id}", response_model=ChatSession)
async def get_chat_session(
    project_id: UUID,
    session_id: UUID,
    service: ChatSessionService = Depends(get_chat_session_service)
) -> ChatSession:
    """
    Get a specific chat session details.

    **Path Parameters:**
    - **project_id**: UUID of the parent project
    - **session_id**: UUID of the chat session to retrieve

    **Returns:**
    - ChatSession object with full details
    """
    session = service.get_session(session_id, str(project_id))
    if not session:
        raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found in project {project_id}")
    
    # Verify session belongs to this project
    if session.project_id != project_id:
        raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found in project {project_id}")
    
    return session


@router.put("/{project_id}/sessions/{session_id}", response_model=ChatSession)
async def update_chat_session(
    project_id: UUID,
    session_id: UUID,
    update_data: ChatSessionUpdate,
    service: ChatSessionService = Depends(get_chat_session_service)
) -> ChatSession:
    """
    Update an existing chat session.

    **Path Parameters:**
    - **project_id**: UUID of the parent project
    - **session_id**: UUID of the chat session to update

    **Request Body:**
    - **title**: Optional new title (1-200 characters)
    - **description**: Optional new description (max 1000 characters)
    - **is_active**: Optional active status
    - **metadata**: Optional updated metadata

    **Returns:**
    - Updated ChatSession object
    """
    try:
        session = service.update_session(session_id, update_data, str(project_id))
        if not session:
            raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found in project {project_id}")
        
        # Verify session belongs to this project
        if session.project_id != project_id:
            raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found in project {project_id}")
        
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update chat session: {str(e)}")


@router.delete("/{project_id}/sessions/{session_id}")
async def delete_chat_session(
    project_id: UUID,
    session_id: UUID,
    force: bool = Query(False, description="Force deletion even with messages"),
    service: ChatSessionService = Depends(get_chat_session_service)
) -> JSONResponse:
    """
    Delete a chat session and all its messages.

    **Path Parameters:**
    - **project_id**: UUID of the parent project
    - **session_id**: UUID of the chat session to delete

    **Query Parameters:**
    - **force**: Force deletion even if session has messages (default: false)

    **Returns:**
    - Confirmation message
    """
    try:
        # First verify the session exists and belongs to this project
        session = service.get_session(session_id, str(project_id))
        if not session:
            raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found in project {project_id}")
        
        if session.project_id != project_id:
            raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found in project {project_id}")
        
        deleted = service.delete_session(session_id, force=force, project_id=str(project_id))
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found")
        
        return JSONResponse(
            status_code=200,
            content={"message": f"Chat session {session_id} deleted successfully from project {project_id}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete chat session: {str(e)}")


@router.post("/{project_id}/sessions/{session_id}/messages", response_model=Message, status_code=201)
async def add_message_to_session(
    project_id: UUID,
    session_id: UUID,
    message_data: MessageCreate,
    service: ChatSessionService = Depends(get_chat_session_service)
) -> Message:
    """
    Add a message to a chat session.

    **Path Parameters:**
    - **project_id**: UUID of the parent project
    - **session_id**: UUID of the chat session

    **Request Body:**
    - **role**: Role of the message sender (user, assistant, system)
    - **content**: The message content
    - **metadata**: Optional additional metadata

    **Returns:**
    - Created Message object
    """
    try:
        # Verify session exists and belongs to this project
        session = service.get_session(session_id, str(project_id))
        if not session:
            raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found in project {project_id}")
        
        if session.project_id != project_id:
            raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found in project {project_id}")
        
        message = service.add_message(session_id, message_data, str(project_id))
        return message
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add message: {str(e)}")


@router.get("/{project_id}/sessions/{session_id}/messages", response_model=List[Message])
async def get_session_messages(
    project_id: UUID,
    session_id: UUID,
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Maximum number of messages to return"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    service: ChatSessionService = Depends(get_chat_session_service)
) -> List[Message]:
    """
    Get messages for a chat session.

    **Path Parameters:**
    - **project_id**: UUID of the parent project
    - **session_id**: UUID of the chat session

    **Query Parameters:**
    - **limit**: Optional limit on number of messages (1-1000)
    - **offset**: Number of messages to skip from the beginning

    **Returns:**
    - List of Message objects
    """
    try:
        # Verify session exists and belongs to this project
        session = service.get_session(session_id, str(project_id))
        if not session:
            raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found in project {project_id}")
        
        if session.project_id != project_id:
            raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found in project {project_id}")
        
        messages = service.get_messages(session_id, limit=limit, offset=offset, project_id=str(project_id))
        return messages
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")


@router.get("/{project_id}/sessions/{session_id}/full", response_model=ChatSessionWithMessages)
async def get_session_with_messages(
    project_id: UUID,
    session_id: UUID,
    service: ChatSessionService = Depends(get_chat_session_service)
) -> ChatSessionWithMessages:
    """
    Get a chat session with its full message history (BONUS ENDPOINT).

    **Path Parameters:**
    - **project_id**: UUID of the parent project
    - **session_id**: UUID of the chat session to retrieve

    **Returns:**
    - ChatSessionWithMessages object containing session and all messages
    """
    try:
        # Verify session exists and belongs to this project
        session = service.get_session(session_id, str(project_id))
        if not session:
            raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found in project {project_id}")
        
        if session.project_id != project_id:
            raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found in project {project_id}")
        
        session_with_messages = service.get_session_with_messages(session_id, str(project_id))
        if not session_with_messages:
            raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found")
        
        return session_with_messages
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session with messages: {str(e)}")