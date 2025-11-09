"""
User State Service for AI Chat Assistant

Service for managing user session data, state persistence, and user context
with comprehensive state management and synchronization.
"""

import json
import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
import uuid
import hashlib

from backend.models.user_state import (
    UserState, UserStateCreate, UserStateUpdate, UserStateSummary,
    UserStateType, UserPreferences, UIState, SessionState,
    RecentActivity, Bookmark, UserStateBackup, UserStateAnalytics
)


class UserStateService:
    """Service for managing user state data and persistence"""

    def __init__(self, base_path: str = None):
        """
        Initialize user state service

        Args:
            base_path: Base directory for storing user state. Defaults to user data directory.
        """
        if base_path is None:
            # Use platform-appropriate data directory
            if os.name == 'nt':  # Windows
                base_path = os.path.join(os.environ.get('APPDATA', ''), 'AI_Chat_Assistant')
            else:  # Unix-like systems
                base_path = os.path.join(os.path.expanduser('~'), '.local', 'share', 'ai_chat_assistant')

        self.base_path = Path(base_path)
        self.user_states_path = self.base_path / "user_states"
        self.backups_path = self.base_path / "state_backups"
        self.analytics_path = self.base_path / "state_analytics"

        # Ensure directories exist
        self.user_states_path.mkdir(parents=True, exist_ok=True)
        self.backups_path.mkdir(parents=True, exist_ok=True)
        self.analytics_path.mkdir(parents=True, exist_ok=True)

        # In-memory cache for faster access
        self._state_cache: Dict[str, Dict[str, UserState]] = {}
        self._analytics: Dict[str, UserStateAnalytics] = {}

        # Load existing states
        self._load_all_states()

    def _get_user_states_path(self, user_id: str) -> Path:
        """Get the path for a user's state files"""
        return self.user_states_path / user_id

    def _get_state_file_path(self, user_id: str, state_id: str) -> Path:
        """Get the file path for a specific state"""
        user_path = self._get_user_states_path(user_id)
        return user_path / f"{state_id}.json"

    def _load_all_states(self):
        """Load all user states from disk"""
        if self.user_states_path.exists():
            for user_dir in self.user_states_path.iterdir():
                if user_dir.is_dir():
                    user_id = user_dir.name
                    self._state_cache[user_id] = {}
                    self._load_user_states(user_id)

    def _load_user_states(self, user_id: str):
        """Load states for a specific user"""
        user_path = self._get_user_states_path(user_id)
        if user_path.exists():
            for state_file in user_path.glob("*.json"):
                try:
                    with open(state_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Convert datetime strings back to datetime objects
                        for dt_field in ['created_at', 'updated_at', 'expires_at']:
                            if data.get(dt_field):
                                data[dt_field] = datetime.fromisoformat(data[dt_field])

                        state = UserState(**data)
                        self._state_cache[user_id][state.id] = state
                except Exception:
                    continue

    def _save_state(self, state: UserState):
        """Save a state to disk"""
        user_path = self._get_user_states_path(state.user_id)
        user_path.mkdir(parents=True, exist_ok=True)

        state_file = self._get_state_file_path(state.user_id, state.id)

        # Update the updated_at timestamp
        state.updated_at = datetime.now()

        data = state.model_dump()
        # Convert datetime objects to ISO strings
        for dt_field in ['created_at', 'updated_at', 'expires_at']:
            if data.get(dt_field):
                data[dt_field] = data[dt_field].isoformat()

        # Handle datetime objects in nested data
        def serialize_datetimes(obj):
            if isinstance(obj, dict):
                return {k: serialize_datetimes(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [serialize_datetimes(item) for item in obj]
            elif isinstance(obj, datetime):
                return obj.isoformat()
            else:
                return obj

        data['data'] = serialize_datetimes(data['data'])

        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _calculate_state_size(self, data: Dict[str, Any]) -> int:
        """Calculate the size of state data in bytes"""
        return len(json.dumps(data, default=str).encode('utf-8'))

    def create_state(self, state_create: UserStateCreate) -> UserState:
        """
        Create a new user state

        Args:
            state_create: State creation data

        Returns:
            Created state
        """
        state = UserState(
            user_id=state_create.user_id,
            state_type=state_create.state_type,
            data=state_create.data,
            expires_at=state_create.expires_at,
            metadata=state_create.metadata
        )

        # Initialize cache for user if needed
        if state.user_id not in self._state_cache:
            self._state_cache[state.user_id] = {}

        self._state_cache[state.user_id][state.id] = state
        self._save_state(state)

        return state

    def get_state(self, user_id: str, state_id: str) -> Optional[UserState]:
        """
        Get a specific user state

        Args:
            user_id: User identifier
            state_id: State identifier

        Returns:
            State if found, None otherwise
        """
        # Check cache first
        user_cache = self._state_cache.get(user_id, {})
        if state_id in user_cache:
            state = user_cache[state_id]
            # Check if expired
            if state.expires_at and state.expires_at < datetime.now():
                self.delete_state(user_id, state_id)
                return None
            return state

        return None

    def get_user_states(self, user_id: str, state_type: Optional[UserStateType] = None) -> List[UserState]:
        """
        Get all states for a user, optionally filtered by type

        Args:
            user_id: User identifier
            state_type: Optional state type filter

        Returns:
            List of user states
        """
        user_cache = self._state_cache.get(user_id, {})
        states = list(user_cache.values())

        # Filter by type if specified
        if state_type:
            states = [s for s in states if s.state_type == state_type]

        # Filter out expired states
        current_time = datetime.now()
        valid_states = []
        for state in states:
            if state.expires_at and state.expires_at < current_time:
                self.delete_state(user_id, state.id)
            else:
                valid_states.append(state)

        return valid_states

    def update_state(self, user_id: str, state_id: str, update: UserStateUpdate) -> Optional[UserState]:
        """
        Update a user state

        Args:
            user_id: User identifier
            state_id: State identifier
            update: State update data

        Returns:
            Updated state if found, None otherwise
        """
        state = self.get_state(user_id, state_id)
        if not state:
            return None

        # Apply updates
        if update.data is not None:
            state.data.update(update.data)
        if update.expires_at is not None:
            state.expires_at = update.expires_at
        if update.metadata is not None:
            state.metadata.update(update.metadata)

        state.version += 1
        state.updated_at = datetime.now()

        self._state_cache[user_id][state_id] = state
        self._save_state(state)

        return state

    def delete_state(self, user_id: str, state_id: str) -> bool:
        """
        Delete a user state

        Args:
            user_id: User identifier
            state_id: State identifier

        Returns:
            True if deleted, False if not found
        """
        if user_id in self._state_cache and state_id in self._state_cache[user_id]:
            del self._state_cache[user_id][state_id]

            # Delete from disk
            state_file = self._get_state_file_path(user_id, state_id)
            if state_file.exists():
                state_file.unlink()

            return True

        return False

    def delete_user_states(self, user_id: str, state_type: Optional[UserStateType] = None) -> int:
        """
        Delete all states for a user, optionally filtered by type

        Args:
            user_id: User identifier
            state_type: Optional state type filter

        Returns:
            Number of states deleted
        """
        states = self.get_user_states(user_id, state_type)
        deleted_count = 0

        for state in states:
            if self.delete_state(user_id, state.id):
                deleted_count += 1

        return deleted_count

    def get_user_preferences(self, user_id: str) -> UserPreferences:
        """
        Get user preferences

        Args:
            user_id: User identifier

        Returns:
            User preferences
        """
        states = self.get_user_states(user_id, UserStateType.PREFERENCES)
        if states:
            try:
                return UserPreferences(**states[0].data)
            except Exception:
                pass

        return UserPreferences()

    def update_user_preferences(self, user_id: str, preferences: UserPreferences) -> UserState:
        """
        Update user preferences

        Args:
            user_id: User identifier
            preferences: Updated preferences

        Returns:
            Updated state
        """
        states = self.get_user_states(user_id, UserStateType.PREFERENCES)
        if states:
            # Update existing
            update = UserStateUpdate(data=preferences.model_dump())
            return self.update_state(user_id, states[0].id, update)
        else:
            # Create new
            state_create = UserStateCreate(
                user_id=user_id,
                state_type=UserStateType.PREFERENCES,
                data=preferences.model_dump()
            )
            return self.create_state(state_create)

    def get_ui_state(self, user_id: str) -> UIState:
        """
        Get UI state for user

        Args:
            user_id: User identifier

        Returns:
            UI state
        """
        states = self.get_user_states(user_id, UserStateType.UI_STATE)
        if states:
            try:
                return UIState(**states[0].data)
            except Exception:
                pass

        return UIState()

    def update_ui_state(self, user_id: str, ui_state: UIState) -> UserState:
        """
        Update UI state

        Args:
            user_id: User identifier
            ui_state: Updated UI state

        Returns:
            Updated state
        """
        states = self.get_user_states(user_id, UserStateType.UI_STATE)
        if states:
            # Update existing
            update = UserStateUpdate(data=ui_state.model_dump())
            return self.update_state(user_id, states[0].id, update)
        else:
            # Create new
            state_create = UserStateCreate(
                user_id=user_id,
                state_type=UserStateType.UI_STATE,
                data=ui_state.model_dump()
            )
            return self.create_state(state_create)

    def get_session_state(self, user_id: str, session_id: str) -> Optional[SessionState]:
        """
        Get session state

        Args:
            user_id: User identifier
            session_id: Session identifier

        Returns:
            Session state if found
        """
        states = self.get_user_states(user_id, UserStateType.SESSION)
        for state in states:
            if state.data.get('session_id') == session_id:
                try:
                    return SessionState(**state.data)
                except Exception:
                    pass

        return None

    def update_session_state(self, user_id: str, session_state: SessionState) -> UserState:
        """
        Update session state

        Args:
            user_id: User identifier
            session_state: Updated session state

        Returns:
            Updated state
        """
        # Look for existing session state
        states = self.get_user_states(user_id, UserStateType.SESSION)
        for state in states:
            if state.data.get('session_id') == session_state.session_id:
                # Update existing
                update = UserStateUpdate(data=session_state.model_dump())
                return self.update_state(user_id, state.id, update)

        # Create new
        state_create = UserStateCreate(
            user_id=user_id,
            state_type=UserStateType.SESSION,
            data=session_state.model_dump()
        )
        return self.create_state(state_create)

    def add_recent_activity(self, user_id: str, activity: RecentActivity):
        """
        Add recent activity for user

        Args:
            user_id: User identifier
            activity: Activity to add
        """
        states = self.get_user_states(user_id, UserStateType.RECENT_ACTIVITY)
        state_id = None
        activities = []

        if states:
            state_id = states[0].id
            activities = states[0].data.get('activities', [])

        # Add new activity
        activities.insert(0, activity.model_dump())

        # Keep only last 50 activities
        activities = activities[:50]

        data = {'activities': activities}

        if state_id:
            # Update existing
            update = UserStateUpdate(data=data)
            self.update_state(user_id, state_id, update)
        else:
            # Create new
            state_create = UserStateCreate(
                user_id=user_id,
                state_type=UserStateType.RECENT_ACTIVITY,
                data=data
            )
            self.create_state(state_create)

    def get_recent_activities(self, user_id: str, limit: int = 20) -> List[RecentActivity]:
        """
        Get recent activities for user

        Args:
            user_id: User identifier
            limit: Maximum number of activities to return

        Returns:
            List of recent activities
        """
        states = self.get_user_states(user_id, UserStateType.RECENT_ACTIVITY)
        if not states:
            return []

        activities_data = states[0].data.get('activities', [])
        activities = []

        for activity_data in activities_data[:limit]:
            try:
                activities.append(RecentActivity(**activity_data))
            except Exception:
                continue

        return activities

    def add_bookmark(self, user_id: str, bookmark: Bookmark):
        """
        Add bookmark for user

        Args:
            user_id: User identifier
            bookmark: Bookmark to add
        """
        states = self.get_user_states(user_id, UserStateType.BOOKMARKS)
        state_id = None
        bookmarks = []

        if states:
            state_id = states[0].id
            bookmarks = states[0].data.get('bookmarks', [])

        # Add new bookmark
        bookmarks.append(bookmark.model_dump())

        data = {'bookmarks': bookmarks}

        if state_id:
            # Update existing
            update = UserStateUpdate(data=data)
            self.update_state(user_id, state_id, update)
        else:
            # Create new
            state_create = UserStateCreate(
                user_id=user_id,
                state_type=UserStateType.BOOKMARKS,
                data=data
            )
            self.create_state(state_create)

    def get_bookmarks(self, user_id: str) -> List[Bookmark]:
        """
        Get bookmarks for user

        Args:
            user_id: User identifier

        Returns:
            List of bookmarks
        """
        states = self.get_user_states(user_id, UserStateType.BOOKMARKS)
        if not states:
            return []

        bookmarks_data = states[0].data.get('bookmarks', [])
        bookmarks = []

        for bookmark_data in bookmarks_data:
            try:
                bookmarks.append(Bookmark(**bookmark_data))
            except Exception:
                continue

        return bookmarks

    def delete_bookmark(self, user_id: str, bookmark_id: str) -> bool:
        """
        Delete a bookmark

        Args:
            user_id: User identifier
            bookmark_id: Bookmark identifier

        Returns:
            True if deleted, False otherwise
        """
        states = self.get_user_states(user_id, UserStateType.BOOKMARKS)
        if not states:
            return False

        bookmarks = states[0].data.get('bookmarks', [])
        original_count = len(bookmarks)

        # Remove bookmark
        bookmarks = [b for b in bookmarks if b.get('id') != bookmark_id]

        if len(bookmarks) < original_count:
            # Update state
            data = {'bookmarks': bookmarks}
            update = UserStateUpdate(data=data)
            self.update_state(user_id, states[0].id, update)
            return True

        return False

    def create_backup(self, user_id: str) -> UserStateBackup:
        """
        Create a backup of all user states

        Args:
            user_id: User identifier

        Returns:
            State backup
        """
        states = self.get_user_states(user_id)

        backup = UserStateBackup(
            user_id=user_id,
            states=states,
            version="1.0",
            metadata={
                'total_states': len(states),
                'backup_timestamp': datetime.now().isoformat()
            }
        )

        # Save backup to file
        backup_filename = f"{user_id}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_file = self.backups_path / backup_filename

        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup.model_dump(), f, indent=2, default=str)

        return backup

    def restore_backup(self, user_id: str, backup: UserStateBackup) -> int:
        """
        Restore user states from backup

        Args:
            user_id: User identifier
            backup: Backup to restore

        Returns:
            Number of states restored
        """
        restored_count = 0

        for state in backup.states:
            try:
                # Create state with new ID to avoid conflicts
                state_create = UserStateCreate(
                    user_id=user_id,
                    state_type=state.state_type,
                    data=state.data,
                    expires_at=state.expires_at,
                    metadata=state.metadata
                )
                self.create_state(state_create)
                restored_count += 1
            except Exception:
                continue

        return restored_count

    def get_analytics(self, user_id: str) -> UserStateAnalytics:
        """
        Get analytics for user state usage

        Args:
            user_id: User identifier

        Returns:
            State analytics
        """
        if user_id in self._analytics:
            return self._analytics[user_id]

        states = self.get_user_states(user_id)
        total_size = sum(self._calculate_state_size(state.data) for state in states)

        states_by_type = {}
        for state in states:
            state_type = state.state_type.value
            states_by_type[state_type] = states_by_type.get(state_type, 0) + 1

        last_activity = max((s.updated_at for s in states), default=datetime.now())

        analytics = UserStateAnalytics(
            user_id=user_id,
            total_states=len(states),
            states_by_type=states_by_type,
            average_state_size=total_size / max(1, len(states)),
            last_activity=last_activity,
            storage_used=total_size,
            period_start=datetime.now() - timedelta(days=30),
            period_end=datetime.now()
        )

        self._analytics[user_id] = analytics
        return analytics

    def cleanup_expired_states(self, user_id: Optional[str] = None) -> int:
        """
        Clean up expired states

        Args:
            user_id: Optional user ID to clean up for specific user

        Returns:
            Number of states cleaned up
        """
        cleaned_count = 0
        current_time = datetime.now()

        if user_id:
            users_to_check = [user_id]
        else:
            users_to_check = list(self._state_cache.keys())

        for uid in users_to_check:
            user_states = self._state_cache.get(uid, {})
            expired_ids = []

            for state_id, state in user_states.items():
                if state.expires_at and state.expires_at < current_time:
                    expired_ids.append(state_id)

            for state_id in expired_ids:
                if self.delete_state(uid, state_id):
                    cleaned_count += 1

        return cleaned_count

    def list_users(self) -> List[str]:
        """
        List all users with state data

        Returns:
            List of user IDs
        """
        return list(self._state_cache.keys())