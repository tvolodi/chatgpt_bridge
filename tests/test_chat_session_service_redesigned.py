"""
Unit Tests for Redesigned Chat Session Service (Project-Nested Structure)

Comprehensive test suite for the ChatSessionService class covering
all functionality aligned with BACKEND_SERVICES_PLAN.md requirements.

Key Changes from Previous Implementation:
- Sessions are ALWAYS nested under projects (data/projects/{project_id}/chat_sessions/)
- project_id is REQUIRED for all operations (no auto-discovery)
- All operations enforce project ID validation
"""

import json
import pytest
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

from backend.models.chat_session import (
    ChatSession, ChatSessionCreate, ChatSessionUpdate, Message, MessageCreate,
    ChatSessionSummary, ChatSessionStats, ChatSessionWithMessages
)
from backend.services.chat_session_service import ChatSessionService


class TestChatSessionServiceRedesigned:
    """Test suite for redesigned ChatSessionService with project nesting."""

    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.service = ChatSessionService(data_dir=str(self.temp_dir))

    def teardown_method(self):
        """Clean up test environment after each test."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    # ===== CREATE SESSION TESTS =====
    
    def test_create_session_with_project_id(self):
        """Test creating a new chat session requires and uses project_id."""
        project_id = uuid4()
        session_data = ChatSessionCreate(
            project_id=project_id,
            title="Test Session",
            description="A test chat session",
            metadata={"test": True}
        )

        session = self.service.create_session(session_data)

        assert isinstance(session, ChatSession)
        assert session.project_id == project_id
        assert session.title == "Test Session"
        assert session.description == "A test chat session"
        assert session.metadata == {"test": True}
        assert session.is_active is True
        assert session.message_count == 0
        assert isinstance(session.id, UUID)

        # Verify nested directory structure
        session_dir = self.temp_dir / "projects" / str(project_id) / "chat_sessions" / str(session.id)
        assert session_dir.exists()
        assert (session_dir / "metadata.json").exists()

    def test_create_session_without_project_id_fails(self):
        """Test that creating a session without project_id fails."""
        session_data = ChatSessionCreate(
            project_id=None,
            title="Test Session"
        )

        with pytest.raises(ValueError, match="project_id is required"):
            self.service.create_session(session_data)

    # ===== GET SESSION TESTS =====

    def test_get_session_requires_project_id(self):
        """Test that get_session requires project_id parameter."""
        project_id = uuid4()
        session_data = ChatSessionCreate(
            project_id=project_id,
            title="Test Session"
        )
        created_session = self.service.create_session(session_data)

        # Should fail without project_id
        with pytest.raises(ValueError, match="project_id is required"):
            self.service.get_session(created_session.id, None)

        # Should succeed with project_id
        retrieved_session = self.service.get_session(created_session.id, str(project_id))
        assert retrieved_session is not None
        assert retrieved_session.id == created_session.id
        assert retrieved_session.title == created_session.title
        assert retrieved_session.project_id == project_id

    def test_get_session_returns_none_if_not_found(self):
        """Test that get_session returns None for non-existent session."""
        project_id = uuid4()
        non_existent_id = uuid4()

        result = self.service.get_session(non_existent_id, str(project_id))
        assert result is None

    # ===== LIST SESSIONS TESTS =====

    def test_list_sessions_requires_project_id(self):
        """Test that list_sessions requires project_id parameter."""
        with pytest.raises(ValueError, match="project_id is required"):
            self.service.list_sessions()

    def test_list_sessions_for_project(self):
        """Test listing sessions within a specific project."""
        project1_id = uuid4()
        project2_id = uuid4()

        # Create sessions for different projects
        session1 = self.service.create_session(ChatSessionCreate(
            project_id=project1_id,
            title="Session 1"
        ))
        session2 = self.service.create_session(ChatSessionCreate(
            project_id=project1_id,
            title="Session 2"
        ))
        session3 = self.service.create_session(ChatSessionCreate(
            project_id=project2_id,
            title="Session 3"
        ))

        # List sessions for project 1
        project1_sessions = self.service.list_sessions(project_id=project1_id)
        assert len(project1_sessions) == 2
        assert all(isinstance(s, ChatSessionSummary) for s in project1_sessions)
        assert all(s.project_id == project1_id for s in project1_sessions)
        assert {s.id for s in project1_sessions} == {session1.id, session2.id}

        # List sessions for project 2
        project2_sessions = self.service.list_sessions(project_id=project2_id)
        assert len(project2_sessions) == 1
        assert project2_sessions[0].id == session3.id

    def test_list_sessions_include_inactive_filter(self):
        """Test listing sessions with inactive filter."""
        project_id = uuid4()

        # Create active and inactive sessions
        active_session = self.service.create_session(ChatSessionCreate(
            project_id=project_id,
            title="Active Session"
        ))
        inactive_session = self.service.create_session(ChatSessionCreate(
            project_id=project_id,
            title="Inactive Session"
        ))
        self.service.update_session(
            inactive_session.id,
            ChatSessionUpdate(is_active=False),
            str(project_id)
        )

        # List only active sessions
        active_list = self.service.list_sessions(project_id=project_id, include_inactive=False)
        assert len(active_list) == 1
        assert active_list[0].id == active_session.id

        # List all sessions
        all_list = self.service.list_sessions(project_id=project_id, include_inactive=True)
        assert len(all_list) == 2

    # ===== UPDATE SESSION TESTS =====

    def test_update_session_requires_project_id(self):
        """Test that update_session requires project_id parameter."""
        project_id = uuid4()
        session_data = ChatSessionCreate(
            project_id=project_id,
            title="Test Session"
        )
        session = self.service.create_session(session_data)

        update_data = ChatSessionUpdate(title="Updated Title")

        with pytest.raises(ValueError, match="project_id is required"):
            self.service.update_session(session.id, update_data, None)

    def test_update_session(self):
        """Test updating an existing chat session."""
        project_id = uuid4()
        session_data = ChatSessionCreate(
            project_id=project_id,
            title="Original Title",
            description="Original description"
        )
        session = self.service.create_session(session_data)
        original_updated_at = session.updated_at

        # Wait a bit to ensure timestamp difference
        import time
        time.sleep(0.01)

        # Update the session
        update_data = ChatSessionUpdate(
            title="Updated Title",
            description="Updated description",
            is_active=False,
            metadata={"updated": True}
        )
        updated_session = self.service.update_session(session.id, update_data, str(project_id))

        assert updated_session is not None
        assert updated_session.id == session.id
        assert updated_session.title == "Updated Title"
        assert updated_session.description == "Updated description"
        assert updated_session.is_active is False
        assert updated_session.metadata == {"updated": True}
        assert updated_session.updated_at > original_updated_at

    def test_update_nonexistent_session_returns_none(self):
        """Test that updating non-existent session returns None."""
        project_id = uuid4()
        non_existent_id = uuid4()
        update_data = ChatSessionUpdate(title="Updated Title")

        result = self.service.update_session(non_existent_id, update_data, str(project_id))
        assert result is None

    # ===== DELETE SESSION TESTS =====

    def test_delete_session_requires_project_id(self):
        """Test that delete_session requires project_id parameter."""
        project_id = uuid4()
        session = self.service.create_session(ChatSessionCreate(
            project_id=project_id,
            title="Test Session"
        ))

        with pytest.raises(ValueError, match="project_id is required"):
            self.service.delete_session(session.id)

    def test_delete_session(self):
        """Test deleting a chat session."""
        project_id = uuid4()
        session = self.service.create_session(ChatSessionCreate(
            project_id=project_id,
            title="Test Session"
        ))

        # Delete the session
        deleted = self.service.delete_session(session.id, project_id=str(project_id))
        assert deleted is True

        # Verify it's gone
        result = self.service.get_session(session.id, str(project_id))
        assert result is None

    def test_delete_nonexistent_session_returns_false(self):
        """Test that deleting non-existent session returns False."""
        project_id = uuid4()
        non_existent_id = uuid4()

        result = self.service.delete_session(non_existent_id, project_id=str(project_id))
        assert result is False

    def test_delete_session_with_messages_requires_force(self):
        """Test that deleting a session with messages requires force flag."""
        project_id = uuid4()
        session = self.service.create_session(ChatSessionCreate(
            project_id=project_id,
            title="Test Session"
        ))
        
        # Add a message
        self.service.add_message(
            session.id,
            MessageCreate(role="user", content="Test message"),
            str(project_id)
        )

        # Try to delete without force - should fail
        with pytest.raises(ValueError, match="Cannot delete session.*with.*messages"):
            self.service.delete_session(session.id, force=False, project_id=str(project_id))

        # Delete with force - should succeed
        deleted = self.service.delete_session(session.id, force=True, project_id=str(project_id))
        assert deleted is True

    # ===== ADD MESSAGE TESTS =====

    def test_add_message_requires_project_id(self):
        """Test that add_message requires project_id parameter."""
        project_id = uuid4()
        session = self.service.create_session(ChatSessionCreate(
            project_id=project_id,
            title="Test Session"
        ))

        message_data = MessageCreate(role="user", content="Test message")

        with pytest.raises(ValueError, match="project_id is required"):
            self.service.add_message(session.id, message_data, None)

    def test_add_message_to_existing_session(self):
        """Test adding a message to a chat session."""
        project_id = uuid4()
        session = self.service.create_session(ChatSessionCreate(
            project_id=project_id,
            title="Test Session"
        ))

        message_data = MessageCreate(
            role="user",
            content="Hello, AI!",
            metadata={"source": "test"}
        )

        message = self.service.add_message(session.id, message_data, str(project_id))

        assert isinstance(message, Message)
        assert message.role == "user"
        assert message.content == "Hello, AI!"
        assert message.metadata == {"source": "test"}
        assert isinstance(message.id, UUID)
        assert isinstance(message.timestamp, datetime)

    def test_add_message_validates_role(self):
        """Test that add_message validates message role."""
        project_id = uuid4()
        session = self.service.create_session(ChatSessionCreate(
            project_id=project_id,
            title="Test Session"
        ))

        invalid_message = MessageCreate(
            role="invalid_role",
            content="Test"
        )

        with pytest.raises(ValueError, match="Invalid message role"):
            self.service.add_message(session.id, invalid_message, str(project_id))

    def test_add_message_to_nonexistent_session_fails(self):
        """Test that adding message to non-existent session fails."""
        project_id = uuid4()
        non_existent_id = uuid4()

        message_data = MessageCreate(role="user", content="Test")

        with pytest.raises(ValueError, match="Chat session .* not found"):
            self.service.add_message(non_existent_id, message_data, str(project_id))

    # ===== GET MESSAGES TESTS =====

    def test_get_messages_requires_project_id(self):
        """Test that get_messages requires project_id parameter."""
        project_id = uuid4()
        session = self.service.create_session(ChatSessionCreate(
            project_id=project_id,
            title="Test Session"
        ))

        with pytest.raises(ValueError, match="project_id is required"):
            self.service.get_messages(session.id, project_id=None)

    def test_get_messages_from_session(self):
        """Test retrieving messages from a session."""
        project_id = uuid4()
        session = self.service.create_session(ChatSessionCreate(
            project_id=project_id,
            title="Test Session"
        ))

        # Add multiple messages
        msg1 = self.service.add_message(
            session.id,
            MessageCreate(role="user", content="Hello"),
            str(project_id)
        )
        msg2 = self.service.add_message(
            session.id,
            MessageCreate(role="assistant", content="Hi there"),
            str(project_id)
        )

        # Retrieve messages
        messages = self.service.get_messages(session.id, project_id=str(project_id))

        assert len(messages) == 2
        assert messages[0].id == msg1.id
        assert messages[1].id == msg2.id

    def test_get_messages_with_pagination(self):
        """Test retrieving messages with limit and offset."""
        project_id = uuid4()
        session = self.service.create_session(ChatSessionCreate(
            project_id=project_id,
            title="Test Session"
        ))

        # Add 5 messages
        for i in range(5):
            self.service.add_message(
                session.id,
                MessageCreate(role="user" if i % 2 == 0 else "assistant", content=f"Message {i}"),
                str(project_id)
            )

        # Get with limit
        limited_messages = self.service.get_messages(session.id, limit=2, project_id=str(project_id))
        assert len(limited_messages) == 2

        # Get with offset
        offset_messages = self.service.get_messages(session.id, offset=2, limit=2, project_id=str(project_id))
        assert len(offset_messages) == 2
        assert offset_messages[0].content == "Message 2"

    def test_get_messages_from_nonexistent_session_fails(self):
        """Test that getting messages from non-existent session fails."""
        project_id = uuid4()
        non_existent_id = uuid4()

        with pytest.raises(ValueError, match="Chat session .* not found"):
            self.service.get_messages(non_existent_id, project_id=str(project_id))

    # ===== GET SESSION WITH MESSAGES TESTS =====

    def test_get_session_with_messages_requires_project_id(self):
        """Test that get_session_with_messages requires project_id parameter."""
        project_id = uuid4()
        session = self.service.create_session(ChatSessionCreate(
            project_id=project_id,
            title="Test Session"
        ))

        with pytest.raises(ValueError, match="project_id is required"):
            self.service.get_session_with_messages(session.id, None)

    def test_get_session_with_messages(self):
        """Test retrieving a session with all its messages."""
        project_id = uuid4()
        session = self.service.create_session(ChatSessionCreate(
            project_id=project_id,
            title="Test Session"
        ))

        # Add messages
        self.service.add_message(
            session.id,
            MessageCreate(role="user", content="Hello"),
            str(project_id)
        )
        self.service.add_message(
            session.id,
            MessageCreate(role="assistant", content="Hi there"),
            str(project_id)
        )

        # Get session with messages
        session_with_messages = self.service.get_session_with_messages(session.id, str(project_id))

        assert session_with_messages is not None
        assert isinstance(session_with_messages, ChatSessionWithMessages)
        assert session_with_messages.session.id == session.id
        assert len(session_with_messages.messages) == 2
        assert session_with_messages.messages[0].content == "Hello"
        assert session_with_messages.messages[1].content == "Hi there"

    def test_get_session_with_messages_nonexistent_returns_none(self):
        """Test that getting non-existent session returns None."""
        project_id = uuid4()
        non_existent_id = uuid4()

        result = self.service.get_session_with_messages(non_existent_id, str(project_id))
        assert result is None

    # ===== SESSION STATS TESTS =====

    def test_get_session_stats_requires_project_id(self):
        """Test that get_session_stats requires project_id parameter."""
        with pytest.raises(ValueError, match="project_id is required"):
            self.service.get_session_stats(project_id=None)

    def test_get_session_stats_for_project(self):
        """Test getting statistics for sessions in a project."""
        project_id = uuid4()

        # Create multiple sessions with messages
        session1 = self.service.create_session(ChatSessionCreate(
            project_id=project_id,
            title="Session 1"
        ))
        session2 = self.service.create_session(ChatSessionCreate(
            project_id=project_id,
            title="Session 2"
        ))

        # Add messages
        self.service.add_message(
            session1.id,
            MessageCreate(role="user", content="Msg1"),
            str(project_id)
        )
        self.service.add_message(
            session1.id,
            MessageCreate(role="assistant", content="Msg2"),
            str(project_id)
        )
        self.service.add_message(
            session2.id,
            MessageCreate(role="user", content="Msg3"),
            str(project_id)
        )

        # Get stats
        stats = self.service.get_session_stats(project_id=project_id)

        assert isinstance(stats, ChatSessionStats)
        assert stats.total_sessions == 2
        assert stats.active_sessions == 2
        assert stats.total_messages == 3
        assert stats.average_messages_per_session == 1.5
        assert stats.sessions_by_project[str(project_id)] == 2
