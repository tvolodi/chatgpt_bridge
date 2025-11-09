"""
User State API for AI Chat Assistant

REST API endpoints for user state management, session data, and user context.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from backend.models.user_state import (
    UserState, UserStateCreate, UserStateUpdate, UserStateSummary,
    UserStateType, UserPreferences, UIState, SessionState,
    RecentActivity, Bookmark, UserStateBackup, UserStateAnalytics
)
from backend.services.user_state_service import UserStateService


# Dependency to get user state service
def get_user_state_service() -> UserStateService:
    """Get user state service instance"""
    return UserStateService()


router = APIRouter(prefix="/user-state", tags=["user-state"])


@router.post("/states", response_model=UserState)
async def create_state(
    state: UserStateCreate,
    service: UserStateService = Depends(get_user_state_service)
):
    """
    Create a new user state

    Args:
        state: State creation data
        service: User state service

    Returns:
        Created state
    """
    try:
        return service.create_state(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create state: {str(e)}")


@router.get("/states/{state_id}", response_model=UserState)
async def get_state(
    state_id: str,
    user_id: str = Query(..., description="User identifier"),
    service: UserStateService = Depends(get_user_state_service)
):
    """
    Get a specific user state

    Args:
        state_id: State identifier
        user_id: User identifier
        service: User state service

    Returns:
        User state
    """
    state = service.get_state(user_id, state_id)
    if not state:
        raise HTTPException(status_code=404, detail="State not found")

    return state


@router.get("/states", response_model=List[UserState])
async def get_user_states(
    user_id: str = Query(..., description="User identifier"),
    state_type: Optional[UserStateType] = Query(None, description="Optional state type filter"),
    service: UserStateService = Depends(get_user_state_service)
):
    """
    Get all states for a user

    Args:
        user_id: User identifier
        state_type: Optional state type filter
        service: User state service

    Returns:
        List of user states
    """
    return service.get_user_states(user_id, state_type)


@router.put("/states/{state_id}", response_model=UserState)
async def update_state(
    state_id: str,
    update: UserStateUpdate,
    user_id: str = Query(..., description="User identifier"),
    service: UserStateService = Depends(get_user_state_service)
):
    """
    Update a user state

    Args:
        state_id: State identifier
        update: State update data
        user_id: User identifier
        service: User state service

    Returns:
        Updated state
    """
    state = service.update_state(user_id, state_id, update)
    if not state:
        raise HTTPException(status_code=404, detail="State not found")

    return state


@router.delete("/states/{state_id}")
async def delete_state(
    state_id: str,
    user_id: str = Query(..., description="User identifier"),
    service: UserStateService = Depends(get_user_state_service)
):
    """
    Delete a user state

    Args:
        state_id: State identifier
        user_id: User identifier
        service: User state service

    Returns:
        Success message
    """
    if not service.delete_state(user_id, state_id):
        raise HTTPException(status_code=404, detail="State not found")

    return {"message": "State deleted successfully"}


@router.delete("/states")
async def delete_user_states(
    user_id: str = Query(..., description="User identifier"),
    state_type: Optional[UserStateType] = Query(None, description="Optional state type filter"),
    service: UserStateService = Depends(get_user_state_service)
):
    """
    Delete all states for a user

    Args:
        user_id: User identifier
        state_type: Optional state type filter
        service: User state service

    Returns:
        Success message with count
    """
    deleted_count = service.delete_user_states(user_id, state_type)
    return {"message": f"Deleted {deleted_count} states successfully"}


# Preferences endpoints
@router.get("/preferences", response_model=UserPreferences)
async def get_user_preferences(
    user_id: str = Query(..., description="User identifier"),
    service: UserStateService = Depends(get_user_state_service)
):
    """
    Get user preferences

    Args:
        user_id: User identifier
        service: User state service

    Returns:
        User preferences
    """
    return service.get_user_preferences(user_id)


@router.put("/preferences", response_model=UserState)
async def update_user_preferences(
    preferences: UserPreferences,
    user_id: str = Query(..., description="User identifier"),
    service: UserStateService = Depends(get_user_state_service)
):
    """
    Update user preferences

    Args:
        preferences: Updated preferences
        user_id: User identifier
        service: User state service

    Returns:
        Updated state
    """
    return service.update_user_preferences(user_id, preferences)


# UI State endpoints
@router.get("/ui-state", response_model=UIState)
async def get_ui_state(
    user_id: str = Query(..., description="User identifier"),
    service: UserStateService = Depends(get_user_state_service)
):
    """
    Get UI state for user

    Args:
        user_id: User identifier
        service: User state service

    Returns:
        UI state
    """
    return service.get_ui_state(user_id)


@router.put("/ui-state", response_model=UserState)
async def update_ui_state(
    ui_state: UIState,
    user_id: str = Query(..., description="User identifier"),
    service: UserStateService = Depends(get_user_state_service)
):
    """
    Update UI state

    Args:
        ui_state: Updated UI state
        user_id: User identifier
        service: User state service

    Returns:
        Updated state
    """
    return service.update_ui_state(user_id, ui_state)


# Session State endpoints
@router.get("/session/{session_id}", response_model=SessionState)
async def get_session_state(
    session_id: str,
    user_id: str = Query(..., description="User identifier"),
    service: UserStateService = Depends(get_user_state_service)
):
    """
    Get session state

    Args:
        session_id: Session identifier
        user_id: User identifier
        service: User state service

    Returns:
        Session state
    """
    session_state = service.get_session_state(user_id, session_id)
    if not session_state:
        raise HTTPException(status_code=404, detail="Session state not found")

    return session_state


@router.put("/session", response_model=UserState)
async def update_session_state(
    session_state: SessionState,
    user_id: str = Query(..., description="User identifier"),
    service: UserStateService = Depends(get_user_state_service)
):
    """
    Update session state

    Args:
        session_state: Updated session state
        user_id: User identifier
        service: User state service

    Returns:
        Updated state
    """
    return service.update_session_state(user_id, session_state)


# Recent Activity endpoints
@router.post("/activity")
async def add_recent_activity(
    activity: RecentActivity,
    user_id: str = Query(..., description="User identifier"),
    service: UserStateService = Depends(get_user_state_service)
):
    """
    Add recent activity

    Args:
        activity: Activity to add
        user_id: User identifier
        service: User state service

    Returns:
        Success message
    """
    service.add_recent_activity(user_id, activity)
    return {"message": "Activity added successfully"}


@router.get("/activity", response_model=List[RecentActivity])
async def get_recent_activities(
    user_id: str = Query(..., description="User identifier"),
    limit: int = Query(20, description="Maximum number of activities to return"),
    service: UserStateService = Depends(get_user_state_service)
):
    """
    Get recent activities

    Args:
        user_id: User identifier
        limit: Maximum number of activities
        service: User state service

    Returns:
        List of recent activities
    """
    return service.get_recent_activities(user_id, limit)


# Bookmark endpoints
@router.post("/bookmarks")
async def add_bookmark(
    bookmark: Bookmark,
    user_id: str = Query(..., description="User identifier"),
    service: UserStateService = Depends(get_user_state_service)
):
    """
    Add bookmark

    Args:
        bookmark: Bookmark to add
        user_id: User identifier
        service: User state service

    Returns:
        Success message
    """
    service.add_bookmark(user_id, bookmark)
    return {"message": "Bookmark added successfully"}


@router.get("/bookmarks", response_model=List[Bookmark])
async def get_bookmarks(
    user_id: str = Query(..., description="User identifier"),
    service: UserStateService = Depends(get_user_state_service)
):
    """
    Get bookmarks

    Args:
        user_id: User identifier
        service: User state service

    Returns:
        List of bookmarks
    """
    return service.get_bookmarks(user_id)


@router.delete("/bookmarks/{bookmark_id}")
async def delete_bookmark(
    bookmark_id: str,
    user_id: str = Query(..., description="User identifier"),
    service: UserStateService = Depends(get_user_state_service)
):
    """
    Delete a bookmark

    Args:
        bookmark_id: Bookmark identifier
        user_id: User identifier
        service: User state service

    Returns:
        Success message
    """
    if not service.delete_bookmark(user_id, bookmark_id):
        raise HTTPException(status_code=404, detail="Bookmark not found")

    return {"message": "Bookmark deleted successfully"}


# Backup and restore endpoints
@router.post("/backup", response_model=UserStateBackup)
async def create_backup(
    user_id: str = Query(..., description="User identifier"),
    service: UserStateService = Depends(get_user_state_service)
):
    """
    Create a backup of user states

    Args:
        user_id: User identifier
        service: User state service

    Returns:
        State backup
    """
    return service.create_backup(user_id)


@router.post("/restore")
async def restore_backup(
    backup: UserStateBackup,
    user_id: str = Query(..., description="User identifier"),
    service: UserStateService = Depends(get_user_state_service)
):
    """
    Restore user states from backup

    Args:
        backup: Backup to restore
        user_id: User identifier
        service: User state service

    Returns:
        Success message with count
    """
    restored_count = service.restore_backup(user_id, backup)
    return {"message": f"Restored {restored_count} states successfully"}


# Analytics endpoints
@router.get("/analytics", response_model=UserStateAnalytics)
async def get_analytics(
    user_id: str = Query(..., description="User identifier"),
    service: UserStateService = Depends(get_user_state_service)
):
    """
    Get user state analytics

    Args:
        user_id: User identifier
        service: User state service

    Returns:
        State analytics
    """
    return service.get_analytics(user_id)


# Maintenance endpoints
@router.post("/cleanup")
async def cleanup_expired_states(
    user_id: Optional[str] = Query(None, description="Optional user ID to clean up for specific user"),
    service: UserStateService = Depends(get_user_state_service)
):
    """
    Clean up expired states

    Args:
        user_id: Optional user ID
        service: User state service

    Returns:
        Success message with count
    """
    cleaned_count = service.cleanup_expired_states(user_id)
    return {"message": f"Cleaned up {cleaned_count} expired states"}


@router.get("/users", response_model=List[str])
async def list_users(
    service: UserStateService = Depends(get_user_state_service)
):
    """
    List all users with state data

    Args:
        service: User state service

    Returns:
        List of user IDs
    """
    return service.list_users()