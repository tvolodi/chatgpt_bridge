"""
User State Models for AI Chat Assistant

Data models for managing user session data, state persistence, and user context.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from enum import Enum
import uuid


class UserStateType(str, Enum):
    """Types of user state data"""
    SESSION = "session"
    PREFERENCES = "preferences"
    UI_STATE = "ui_state"
    RECENT_ACTIVITY = "recent_activity"
    BOOKMARKS = "bookmarks"
    CUSTOM = "custom"


class UITheme(str, Enum):
    """UI theme preferences"""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"
    AUTO = "auto"


class UILayout(str, Enum):
    """UI layout preferences"""
    COMPACT = "compact"
    COMFORTABLE = "comfortable"
    SPACIOUS = "spacious"


class NotificationPreferences(BaseModel):
    """User notification preferences"""
    model_config = ConfigDict(from_attributes=True)

    enabled: bool = Field(default=True, description="Whether notifications are enabled")
    sound_enabled: bool = Field(default=True, description="Whether notification sounds are enabled")
    desktop_notifications: bool = Field(default=True, description="Whether desktop notifications are enabled")
    email_notifications: bool = Field(default=False, description="Whether email notifications are enabled")
    notification_types: Dict[str, bool] = Field(default_factory=dict, description="Specific notification types")


class UserPreferences(BaseModel):
    """User preference settings"""
    model_config = ConfigDict(from_attributes=True)

    theme: UITheme = Field(default=UITheme.SYSTEM, description="UI theme preference")
    layout: UILayout = Field(default=UILayout.COMFORTABLE, description="UI layout preference")
    language: str = Field(default="en", description="Preferred language")
    timezone: str = Field(default="UTC", description="User timezone")
    date_format: str = Field(default="YYYY-MM-DD", description="Preferred date format")
    time_format: str = Field(default="24h", description="Preferred time format (12h/24h)")
    notifications: NotificationPreferences = Field(default_factory=NotificationPreferences, description="Notification preferences")
    auto_save: bool = Field(default=True, description="Whether to auto-save work")
    auto_save_interval: int = Field(default=30, description="Auto-save interval in seconds")
    keyboard_shortcuts: Dict[str, str] = Field(default_factory=dict, description="Custom keyboard shortcuts")


class UIState(BaseModel):
    """UI state information"""
    model_config = ConfigDict(from_attributes=True)

    sidebar_collapsed: bool = Field(default=False, description="Whether sidebar is collapsed")
    active_panel: Optional[str] = Field(None, description="Currently active panel")
    window_size: Optional[Dict[str, int]] = Field(None, description="Window dimensions")
    window_position: Optional[Dict[str, int]] = Field(None, description="Window position")
    split_pane_sizes: Optional[List[int]] = Field(None, description="Split pane sizes")
    expanded_sections: List[str] = Field(default_factory=list, description="Expanded UI sections")
    last_viewed_project: Optional[str] = Field(None, description="Last viewed project ID")
    last_viewed_session: Optional[str] = Field(None, description="Last viewed session ID")


class RecentActivity(BaseModel):
    """Recent user activity"""
    model_config = ConfigDict(from_attributes=True)

    action: str = Field(..., description="Activity action type")
    resource_type: str = Field(..., description="Type of resource (conversation, file, project)")
    resource_id: str = Field(..., description="Resource identifier")
    title: str = Field(..., description="Human-readable title")
    timestamp: datetime = Field(default_factory=datetime.now, description="When activity occurred")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional activity metadata")


class Bookmark(BaseModel):
    """User bookmark"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Bookmark identifier")
    title: str = Field(..., description="Bookmark title")
    resource_type: str = Field(..., description="Type of bookmarked resource")
    resource_id: str = Field(..., description="Resource identifier")
    url: Optional[str] = Field(None, description="Bookmark URL if applicable")
    description: Optional[str] = Field(None, description="Bookmark description")
    tags: List[str] = Field(default_factory=list, description="Bookmark tags")
    created_at: datetime = Field(default_factory=datetime.now, description="When bookmark was created")
    last_accessed: datetime = Field(default_factory=datetime.now, description="When bookmark was last accessed")


class SessionState(BaseModel):
    """User session state"""
    model_config = ConfigDict(from_attributes=True)

    session_id: str = Field(..., description="Session identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    login_time: datetime = Field(default_factory=datetime.now, description="Session login time")
    last_activity: datetime = Field(default_factory=datetime.now, description="Last activity timestamp")
    active_project: Optional[str] = Field(None, description="Currently active project")
    active_session: Optional[str] = Field(None, description="Currently active chat session")
    open_tabs: List[str] = Field(default_factory=list, description="Open tab identifiers")
    draft_content: Optional[str] = Field(None, description="Unsaved draft content")
    clipboard_history: List[str] = Field(default_factory=list, description="Recent clipboard items")


class UserState(BaseModel):
    """Complete user state container"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="State identifier")
    user_id: str = Field(..., description="User identifier")
    state_type: UserStateType = Field(..., description="Type of state data")
    data: Dict[str, Any] = Field(default_factory=dict, description="State data")
    version: int = Field(default=1, description="State version for optimistic locking")
    created_at: datetime = Field(default_factory=datetime.now, description="When state was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="When state was last updated")
    expires_at: Optional[datetime] = Field(None, description="When state expires")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class UserStateSummary(BaseModel):
    """Summary of user state"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="State identifier")
    user_id: str = Field(..., description="User identifier")
    state_type: UserStateType = Field(..., description="Type of state data")
    version: int = Field(..., description="State version")
    created_at: datetime = Field(..., description="When state was created")
    updated_at: datetime = Field(..., description="When state was last updated")
    size_bytes: int = Field(..., description="Size of state data in bytes")


class UserStateCreate(BaseModel):
    """Model for creating user state"""
    model_config = ConfigDict(from_attributes=True)

    user_id: str = Field(..., description="User identifier")
    state_type: UserStateType = Field(..., description="Type of state data")
    data: Dict[str, Any] = Field(default_factory=dict, description="State data")
    expires_at: Optional[datetime] = Field(None, description="When state expires")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class UserStateUpdate(BaseModel):
    """Model for updating user state"""
    model_config = ConfigDict(from_attributes=True)

    data: Optional[Dict[str, Any]] = Field(None, description="Updated state data")
    expires_at: Optional[datetime] = Field(None, description="Updated expiration")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")


class UserStateBackup(BaseModel):
    """User state backup"""
    model_config = ConfigDict(from_attributes=True)

    user_id: str = Field(..., description="User identifier")
    states: List[UserState] = Field(default_factory=list, description="All user states")
    backup_time: datetime = Field(default_factory=datetime.now, description="When backup was created")
    version: str = Field(..., description="Backup version")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Backup metadata")


class UserStateAnalytics(BaseModel):
    """Analytics for user state usage"""
    model_config = ConfigDict(from_attributes=True)

    user_id: str = Field(..., description="User identifier")
    total_states: int = Field(0, description="Total number of state entries")
    states_by_type: Dict[str, int] = Field(default_factory=dict, description="States by type")
    average_state_size: float = Field(0.0, description="Average state size in bytes")
    last_activity: datetime = Field(default_factory=datetime.now, description="Last state activity")
    storage_used: int = Field(0, description="Total storage used in bytes")
    period_start: datetime = Field(..., description="Analytics period start")
    period_end: datetime = Field(..., description="Analytics period end")