"""
Tests for User State Service

Comprehensive unit tests for user state management functionality.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from backend.models.user_state import (
    UserState, UserStateCreate, UserStateUpdate, UserStateType,
    UserPreferences, UIState, SessionState, RecentActivity, Bookmark,
    UserStateBackup, UserStateAnalytics
)
from backend.services.user_state_service import UserStateService


class TestUserStateService:
    """Test suite for UserStateService"""

    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.service = UserStateService(base_path=str(self.temp_dir))

    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)

    def test_create_state(self):
        """Test creating a new user state"""
        state_create = UserStateCreate(
            user_id="user1",
            state_type=UserStateType.PREFERENCES,
            data={"theme": "dark"},
            metadata={"source": "test"}
        )

        state = self.service.create_state(state_create)

        assert state.user_id == "user1"
        assert state.state_type == UserStateType.PREFERENCES
        assert state.data == {"theme": "dark"}
        assert state.metadata == {"source": "test"}
        assert state.version == 1
        assert state.created_at is not None
        assert state.updated_at is not None

    def test_get_state(self):
        """Test retrieving a user state"""
        # Create state
        state_create = UserStateCreate(
            user_id="user1",
            state_type=UserStateType.PREFERENCES,
            data={"theme": "dark"}
        )
        created_state = self.service.create_state(state_create)

        # Retrieve state
        retrieved_state = self.service.get_state("user1", created_state.id)

        assert retrieved_state is not None
        assert retrieved_state.id == created_state.id
        assert retrieved_state.data == {"theme": "dark"}

    def test_get_state_not_found(self):
        """Test retrieving non-existent state"""
        state = self.service.get_state("user1", "nonexistent")
        assert state is None

    def test_get_user_states(self):
        """Test retrieving all states for a user"""
        # Create multiple states
        state1 = self.service.create_state(UserStateCreate(
            user_id="user1",
            state_type=UserStateType.PREFERENCES,
            data={"theme": "dark"}
        ))
        state2 = self.service.create_state(UserStateCreate(
            user_id="user1",
            state_type=UserStateType.UI_STATE,
            data={"sidebar": True}
        ))

        states = self.service.get_user_states("user1")
        assert len(states) == 2
        state_ids = {s.id for s in states}
        assert state1.id in state_ids
        assert state2.id in state_ids

    def test_get_user_states_filtered(self):
        """Test retrieving states filtered by type"""
        # Create states of different types
        self.service.create_state(UserStateCreate(
            user_id="user1",
            state_type=UserStateType.PREFERENCES,
            data={"theme": "dark"}
        ))
        self.service.create_state(UserStateCreate(
            user_id="user1",
            state_type=UserStateType.UI_STATE,
            data={"sidebar": True}
        ))

        preferences_states = self.service.get_user_states("user1", UserStateType.PREFERENCES)
        assert len(preferences_states) == 1
        assert preferences_states[0].state_type == UserStateType.PREFERENCES

    def test_update_state(self):
        """Test updating a user state"""
        # Create state
        state_create = UserStateCreate(
            user_id="user1",
            state_type=UserStateType.PREFERENCES,
            data={"theme": "dark"}
        )
        created_state = self.service.create_state(state_create)

        # Update state
        update = UserStateUpdate(data={"theme": "light", "font_size": 14})
        updated_state = self.service.update_state("user1", created_state.id, update)

        assert updated_state is not None
        assert updated_state.data == {"theme": "light", "font_size": 14}
        assert updated_state.version == 2
        # Allow for small timing differences
        assert updated_state.updated_at >= created_state.updated_at

    def test_update_state_not_found(self):
        """Test updating non-existent state"""
        update = UserStateUpdate(data={"theme": "light"})
        result = self.service.update_state("user1", "nonexistent", update)
        assert result is None

    def test_delete_state(self):
        """Test deleting a user state"""
        # Create state
        state_create = UserStateCreate(
            user_id="user1",
            state_type=UserStateType.PREFERENCES,
            data={"theme": "dark"}
        )
        created_state = self.service.create_state(state_create)

        # Delete state
        result = self.service.delete_state("user1", created_state.id)
        assert result is True

        # Verify deletion
        retrieved_state = self.service.get_state("user1", created_state.id)
        assert retrieved_state is None

    def test_delete_state_not_found(self):
        """Test deleting non-existent state"""
        result = self.service.delete_state("user1", "nonexistent")
        assert result is False

    def test_delete_user_states(self):
        """Test deleting all states for a user"""
        # Create states
        self.service.create_state(UserStateCreate(
            user_id="user1",
            state_type=UserStateType.PREFERENCES,
            data={"theme": "dark"}
        ))
        self.service.create_state(UserStateCreate(
            user_id="user1",
            state_type=UserStateType.UI_STATE,
            data={"sidebar": True}
        ))

        # Delete all states
        deleted_count = self.service.delete_user_states("user1")
        assert deleted_count == 2

        # Verify deletion
        states = self.service.get_user_states("user1")
        assert len(states) == 0

    def test_delete_user_states_filtered(self):
        """Test deleting states filtered by type"""
        # Create states
        self.service.create_state(UserStateCreate(
            user_id="user1",
            state_type=UserStateType.PREFERENCES,
            data={"theme": "dark"}
        ))
        self.service.create_state(UserStateCreate(
            user_id="user1",
            state_type=UserStateType.UI_STATE,
            data={"sidebar": True}
        ))

        # Delete only preferences
        deleted_count = self.service.delete_user_states("user1", UserStateType.PREFERENCES)
        assert deleted_count == 1

        # Verify only UI state remains
        states = self.service.get_user_states("user1")
        assert len(states) == 1
        assert states[0].state_type == UserStateType.UI_STATE

    def test_expired_state_handling(self):
        """Test handling of expired states"""
        # Create state with expiration
        past_time = datetime.now() - timedelta(hours=1)
        state_create = UserStateCreate(
            user_id="user1",
            state_type=UserStateType.SESSION,
            data={"session_id": "session1"},
            expires_at=past_time
        )
        self.service.create_state(state_create)

        # Try to retrieve expired state
        states = self.service.get_user_states("user1")
        assert len(states) == 0  # Should be cleaned up

    def test_user_preferences_management(self):
        """Test user preferences management"""
        # Get default preferences
        prefs = self.service.get_user_preferences("user1")
        assert isinstance(prefs, UserPreferences)

        # Update preferences
        new_prefs = UserPreferences(theme="dark", language="en", timezone="UTC")
        state = self.service.update_user_preferences("user1", new_prefs)

        assert state.state_type == UserStateType.PREFERENCES
        assert state.data["theme"] == "dark"
        assert state.data["language"] == "en"

        # Get updated preferences
        retrieved_prefs = self.service.get_user_preferences("user1")
        assert retrieved_prefs.theme == "dark"
        assert retrieved_prefs.language == "en"

    def test_ui_state_management(self):
        """Test UI state management"""
        # Get default UI state
        ui_state = self.service.get_ui_state("user1")
        assert isinstance(ui_state, UIState)

        # Update UI state
        new_ui_state = UIState(sidebar_collapsed=True, active_panel="chat")
        state = self.service.update_ui_state("user1", new_ui_state)

        assert state.state_type == UserStateType.UI_STATE
        assert state.data["sidebar_collapsed"] is True
        assert state.data["active_panel"] == "chat"

        # Get updated UI state
        retrieved_ui_state = self.service.get_ui_state("user1")
        assert retrieved_ui_state.sidebar_collapsed is True
        assert retrieved_ui_state.active_panel == "chat"

    def test_session_state_management(self):
        """Test session state management"""
        # Create session state
        session_state = SessionState(
            session_id="session1",
            active_session="conv1",
            last_activity=datetime.now()
        )
        state = self.service.update_session_state("user1", session_state)

        assert state.state_type == UserStateType.SESSION
        assert state.data["session_id"] == "session1"

        # Get session state
        retrieved_session = self.service.get_session_state("user1", "session1")
        assert retrieved_session is not None
        assert retrieved_session.session_id == "session1"
        assert retrieved_session.active_session == "conv1"

    def test_recent_activity_management(self):
        """Test recent activity management"""
        # Add activities
        activity1 = RecentActivity(
            action="create",
            resource_type="conversation",
            resource_id="conv1",
            title="Started new conversation",
            metadata={"conversation_id": "conv1"}
        )
        activity2 = RecentActivity(
            action="upload",
            resource_type="file",
            resource_id="file1",
            title="Uploaded file",
            metadata={"file_name": "test.txt"}
        )

        self.service.add_recent_activity("user1", activity1)
        self.service.add_recent_activity("user1", activity2)

        # Get activities
        activities = self.service.get_recent_activities("user1")
        assert len(activities) == 2
        assert activities[0].action == "upload"  # Most recent first
        assert activities[1].action == "create"

    def test_recent_activity_limit(self):
        """Test recent activity limit"""
        # Add more than limit
        for i in range(60):
            activity = RecentActivity(
                action="test",
                resource_type="test",
                resource_id=f"resource_{i}",
                title=f"Activity {i}",
                metadata={"index": i}
            )
            self.service.add_recent_activity("user1", activity)

        # Get activities (should be limited to 50)
        activities = self.service.get_recent_activities("user1", limit=100)
        assert len(activities) == 50

    def test_bookmark_management(self):
        """Test bookmark management"""
        # Add bookmarks
        bookmark1 = Bookmark(
            title="Important Chat",
            resource_type="conversation",
            resource_id="conv1",
            url="/chat/conv1",
            description="Important conversation"
        )
        bookmark2 = Bookmark(
            title="Project Notes",
            resource_type="project",
            resource_id="proj1",
            url="/notes/project1",
            description="Project documentation"
        )

        self.service.add_bookmark("user1", bookmark1)
        self.service.add_bookmark("user1", bookmark2)

        # Get bookmarks
        bookmarks = self.service.get_bookmarks("user1")
        assert len(bookmarks) == 2
        titles = {b.title for b in bookmarks}
        assert "Important Chat" in titles
        assert "Project Notes" in titles

    def test_delete_bookmark(self):
        """Test bookmark deletion"""
        # Add bookmark
        bookmark = Bookmark(
            title="Test Bookmark",
            resource_type="test",
            resource_id="test1",
            url="/test",
            description="Test bookmark"
        )
        self.service.add_bookmark("user1", bookmark)

        # Get bookmark ID
        bookmarks = self.service.get_bookmarks("user1")
        bookmark_id = bookmarks[0].id

        # Delete bookmark
        result = self.service.delete_bookmark("user1", bookmark_id)
        assert result is True

        # Verify deletion
        bookmarks = self.service.get_bookmarks("user1")
        assert len(bookmarks) == 0

    def test_delete_bookmark_not_found(self):
        """Test deleting non-existent bookmark"""
        result = self.service.delete_bookmark("user1", "nonexistent")
        assert result is False

    def test_backup_and_restore(self):
        """Test backup and restore functionality"""
        # Create some states
        self.service.create_state(UserStateCreate(
            user_id="user1",
            state_type=UserStateType.PREFERENCES,
            data={"theme": "dark"}
        ))
        self.service.create_state(UserStateCreate(
            user_id="user1",
            state_type=UserStateType.UI_STATE,
            data={"sidebar": True}
        ))

        # Create backup
        backup = self.service.create_backup("user1")
        assert backup.user_id == "user1"
        assert len(backup.states) == 2

        # Clear states
        self.service.delete_user_states("user1")

        # Restore from backup
        restored_count = self.service.restore_backup("user1", backup)
        assert restored_count == 2

        # Verify restoration
        states = self.service.get_user_states("user1")
        assert len(states) == 2

    def test_analytics(self):
        """Test analytics functionality"""
        # Create some states
        self.service.create_state(UserStateCreate(
            user_id="user1",
            state_type=UserStateType.PREFERENCES,
            data={"theme": "dark", "language": "en"}
        ))
        self.service.create_state(UserStateCreate(
            user_id="user1",
            state_type=UserStateType.UI_STATE,
            data={"sidebar": True}
        ))

        # Get analytics
        analytics = self.service.get_analytics("user1")
        assert analytics.user_id == "user1"
        assert analytics.total_states == 2
        assert analytics.states_by_type["preferences"] == 1
        assert analytics.states_by_type["ui_state"] == 1
        assert analytics.average_state_size > 0
        assert analytics.storage_used > 0

    def test_cleanup_expired_states(self):
        """Test cleanup of expired states"""
        # Create expired state
        past_time = datetime.now() - timedelta(hours=1)
        self.service.create_state(UserStateCreate(
            user_id="user1",
            state_type=UserStateType.SESSION,
            data={"session_id": "expired"},
            expires_at=past_time
        ))

        # Create valid state
        future_time = datetime.now() + timedelta(hours=1)
        self.service.create_state(UserStateCreate(
            user_id="user1",
            state_type=UserStateType.PREFERENCES,
            data={"theme": "dark"},
            expires_at=future_time
        ))

        # Cleanup expired states
        cleaned_count = self.service.cleanup_expired_states("user1")
        assert cleaned_count == 1

        # Verify only valid state remains
        states = self.service.get_user_states("user1")
        assert len(states) == 1
        assert states[0].state_type == UserStateType.PREFERENCES

    def test_list_users(self):
        """Test listing users"""
        # Create states for different users
        self.service.create_state(UserStateCreate(
            user_id="user1",
            state_type=UserStateType.PREFERENCES,
            data={"theme": "dark"}
        ))
        self.service.create_state(UserStateCreate(
            user_id="user2",
            state_type=UserStateType.PREFERENCES,
            data={"theme": "light"}
        ))

        users = self.service.list_users()
        assert len(users) == 2
        assert "user1" in users
        assert "user2" in users

    def test_persistence(self):
        """Test state persistence across service instances"""
        # Create state with first service instance
        state_create = UserStateCreate(
            user_id="user1",
            state_type=UserStateType.PREFERENCES,
            data={"theme": "dark"}
        )
        created_state = self.service.create_state(state_create)

        # Create new service instance (simulating restart)
        new_service = UserStateService(base_path=str(self.temp_dir))

        # Retrieve state with new instance
        retrieved_state = new_service.get_state("user1", created_state.id)
        assert retrieved_state is not None
        assert retrieved_state.data == {"theme": "dark"}

    def test_state_size_calculation(self):
        """Test state size calculation"""
        data = {"large_field": "x" * 1000, "nested": {"data": [1, 2, 3] * 100}}
        state_create = UserStateCreate(
            user_id="user1",
            state_type=UserStateType.PREFERENCES,
            data=data
        )
        state = self.service.create_state(state_create)

        # Size should be reasonable
        size = self.service._calculate_state_size(state.data)
        assert size > 1000  # Should account for the large field

    def test_concurrent_access_simulation(self):
        """Test concurrent access simulation"""
        import threading
        import time

        results = []
        errors = []

        def create_states(user_id, count):
            try:
                for i in range(count):
                    state_create = UserStateCreate(
                        user_id=user_id,
                        state_type=UserStateType.PREFERENCES,
                        data={"index": i}
                    )
                    self.service.create_state(state_create)
                results.append(f"user_{user_id}_done")
            except Exception as e:
                errors.append(str(e))

        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=create_states, args=(f"user{i}", 5))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        assert len(results) == 3
        assert len(errors) == 0

        # Verify all states were created
        total_states = sum(len(self.service.get_user_states(f"user{i}")) for i in range(3))
        assert total_states == 15