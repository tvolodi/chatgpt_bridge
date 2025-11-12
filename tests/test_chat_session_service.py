"""
Unit Tests for Chat Session Service

Comprehensive test suite for the ChatSessionService class covering
all functionality, edge cases, and error scenarios.
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


class TestChatSessionService:
    """Test suite for ChatSessionService."""

    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.service = ChatSessionService(data_dir=str(self.temp_dir))

    def teardown_method(self):
        """Clean up test environment after each test."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_create_session_with_project_id(self):
        """Test creating a new chat session requires project_id."""
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
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.updated_at, datetime)

        # Verify persistence
        loaded_session = self.service.get_session(session.id, str(project_id))
        assert loaded_session is not None
        assert loaded_session.id == session.id
        assert loaded_session.title == session.title

    def test_create_session_without_project_id_fails(self):
        """Test that creating a session without project_id fails."""
        session_data = ChatSessionCreate(
            project_id=None,
            title="Test Session"
        )

        with pytest.raises(ValueError, match="project_id is required"):
            self.service.create_session(session_data)

    def test_get_session_requires_project_id(self):
        """Test that retrieving a session requires project_id."""
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

        # Test retrieving non-existent session
        non_existent_id = uuid4()
        assert self.service.get_session(non_existent_id, str(project_id)) is None

    def test_list_sessions_requires_project_id(self):
        """Test that listing sessions requires project_id."""
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

        # Test list all sessions - requires project_id
        with pytest.raises(ValueError, match="project_id is required"):
            self.service.list_sessions()

        # Test filter by project - should return only sessions in that project
        project1_sessions = self.service.list_sessions(project_id=project1_id)
        assert len(project1_sessions) == 2
        assert all(s.project_id == project1_id for s in project1_sessions)

        # Test filter by project 2
        project2_sessions = self.service.list_sessions(project_id=project2_id)
        assert len(project2_sessions) == 1
        assert all(s.project_id == project2_id for s in project2_sessions)

        # Test include inactive (all are active by default)
        project1_including_inactive = self.service.list_sessions(project_id=project1_id, include_inactive=True)
        assert len(project1_including_inactive) == 2

    def test_update_session(self):
        """Test updating an existing chat session."""
        # Create a session
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

        # Test updating without project_id fails
        with pytest.raises(ValueError, match="project_id is required"):
            self.service.update_session(session.id, update_data, None)

        # Test updating non-existent session
        non_existent_update = self.service.update_session(uuid4(), update_data, str(uuid4()))
        assert non_existent_update is None

    def test_delete_session(self):
        """Test deleting a chat session."""
        # Create a session
        project_id = uuid4()
        session = self.service.create_session(ChatSessionCreate(
            project_id=project_id,
            title="Test Session"
        ))

        # Delete the session
        deleted = self.service.delete_session(session.id, project_id=str(project_id))
        assert deleted is True

        # Verify it's gone
        assert self.service.get_session(session.id, str(project_id)) is None

        # Test deleting without project_id fails
        with pytest.raises(ValueError, match="project_id is required"):
            self.service.delete_session(session.id)

        # Test deleting non-existent session
        assert self.service.delete_session(uuid4(), project_id=str(uuid4())) is False

    def test_delete_session_with_messages_force_required(self):
        """Test that deleting a session with messages requires force flag."""
        # Create a session and add a message
        project_id = uuid4()
        session = self.service.create_session(ChatSessionCreate(
            project_id=project_id,
            title="Test Session"
        ))
        self.service.add_message(session.id, MessageCreate(
            role="user",
            content="Test message"
        ), str(project_id))

        # Try to delete without force - should fail
        with pytest.raises(ValueError, match="Cannot delete session.*with.*messages"):
            self.service.delete_session(session.id, force=False, project_id=str(project_id))

        # Delete with force - should succeed
        deleted = self.service.delete_session(session.id, force=True, project_id=str(project_id))
        assert deleted is True

    def test_add_message(self):
        """Test adding a message to a chat session."""
        # Create a session
        project_id = uuid4()
        session = self.service.create_session(ChatSessionCreate(
            project_id=project_id,
            title="Test Session"
        ))

        # Add a message
        message_data = MessageCreate(
            role="user",
            content="Hello, world!",
            metadata={"test": True}
        )
        message = self.service.add_message(session.id, message_data)

        assert isinstance(message, Message)
        assert message.role == "user"
        assert message.content == "Hello, world!"
        assert message.metadata == {"test": True}
        assert isinstance(message.id, UUID)
        assert isinstance(message.timestamp, datetime)

        # Verify session was updated
        updated_session = self.service.get_session(session.id)
        assert updated_session.message_count == 1
        assert updated_session.updated_at > session.updated_at

        # Test adding message to non-existent session
        with pytest.raises(ValueError, match="Chat session.*not found"):
            self.service.add_message(uuid4(), message_data)

    def test_add_message_invalid_role(self):
        """Test adding a message with invalid role."""
        session = self.service.create_session(ChatSessionCreate(
            project_id=uuid4(),
            title="Test Session"
        ))

        with pytest.raises(ValueError, match="Invalid message role"):
            self.service.add_message(session.id, MessageCreate(
                role="invalid_role",
                content="Test"
            ))

    def test_get_messages(self):
        """Test retrieving messages from a chat session."""
        # Create a session and add messages
        session = self.service.create_session(ChatSessionCreate(
            project_id=uuid4(),
            title="Test Session"
        ))

        messages_data = [
            MessageCreate(role="user", content="Message 1"),
            MessageCreate(role="assistant", content="Message 2"),
            MessageCreate(role="user", content="Message 3"),
        ]

        for msg_data in messages_data:
            self.service.add_message(session.id, msg_data)

        # Get all messages
        messages = self.service.get_messages(session.id)
        assert len(messages) == 3
        assert all(isinstance(m, Message) for m in messages)
        assert messages[0].content == "Message 1"
        assert messages[1].content == "Message 2"
        assert messages[2].content == "Message 3"

        # Test pagination
        limited_messages = self.service.get_messages(session.id, limit=2)
        assert len(limited_messages) == 2

        offset_messages = self.service.get_messages(session.id, offset=1, limit=1)
        assert len(offset_messages) == 1
        assert offset_messages[0].content == "Message 2"

        # Test getting messages from non-existent session
        with pytest.raises(ValueError, match="Chat session.*not found"):
            self.service.get_messages(uuid4())

    def test_get_session_with_messages(self):
        """Test getting a session with its full message history."""
        # Create a session and add messages
        session = self.service.create_session(ChatSessionCreate(
            project_id=uuid4(),
            title="Test Session"
        ))

        self.service.add_message(session.id, MessageCreate(role="user", content="Hello"))
        self.service.add_message(session.id, MessageCreate(role="assistant", content="Hi there"))

        # Get session with messages
        session_with_messages = self.service.get_session_with_messages(session.id)

        assert isinstance(session_with_messages, ChatSessionWithMessages)
        assert session_with_messages.session.id == session.id
        assert len(session_with_messages.messages) == 2
        assert session_with_messages.messages[0].content == "Hello"
        assert session_with_messages.messages[1].content == "Hi there"

        # Test with non-existent session
        assert self.service.get_session_with_messages(uuid4()) is None

    def test_session_validation(self):
        """Test session creation validation."""
        # Test title validation
        with pytest.raises(ValueError):
            self.service.create_session(ChatSessionCreate(
                project_id=uuid4(),
                title=""  # Empty title should fail
            ))

        with pytest.raises(ValueError):
            self.service.create_session(ChatSessionCreate(
                project_id=uuid4(),
                title="A" * 201  # Too long title should fail
            ))

        # Test description validation
        with pytest.raises(ValueError):
            self.service.create_session(ChatSessionCreate(
                project_id=uuid4(),
                title="Test",
                description="A" * 1001  # Too long description should fail
            ))

    def test_session_timestamps(self):
        """Test that session timestamps are properly managed."""
        # Create a session
        session = self.service.create_session(ChatSessionCreate(
            project_id=uuid4(),
            title="Test Session"
        ))

        # Timestamps should be set
        assert session.created_at is not None
        assert session.updated_at is not None
        assert abs((datetime.now() - session.created_at).total_seconds()) < 1
        assert abs((datetime.now() - session.updated_at).total_seconds()) < 1

        # Update should change updated_at
        import time
        time.sleep(0.01)
        original_updated_at = session.updated_at

        self.service.update_session(session.id, ChatSessionUpdate(title="Updated"))
        updated_session = self.service.get_session(session.id)
        assert updated_session.updated_at > original_updated_at

    def test_session_directory_structure(self):
        """Test that session data is stored in proper directory structure."""
        session = self.service.create_session(ChatSessionCreate(
            project_id=uuid4(),
            title="Test Session"
        ))

        # Check directory structure
        session_dir = self.temp_dir / "chat_sessions" / str(session.id)
        assert session_dir.exists()
        assert session_dir.is_dir()

        # Check metadata file
        metadata_file = session_dir / "metadata.json"
        assert metadata_file.exists()

        # Check messages file (should not exist until messages are added)
        messages_file = session_dir / "messages.json"
        assert not messages_file.exists()  # Messages file is created lazily

        # Verify metadata content
        with open(metadata_file, 'r') as f:
            data = json.load(f)
            assert data['title'] == "Test Session"
            assert data['message_count'] == 0

    def test_session_metadata_persistence(self):
        """Test that session metadata persists across service restarts."""
        # Create a session
        session = self.service.create_session(ChatSessionCreate(
            project_id=uuid4(),
            title="Test Session",
            metadata={"custom": "data"}
        ))

        # Add a message to update the session
        self.service.add_message(session.id, MessageCreate(
            role="user",
            content="Test message"
        ))

        # Create a new service instance (simulating restart)
        new_service = ChatSessionService(data_dir=str(self.temp_dir))

        # Verify session data persists
        loaded_session = new_service.get_session(session.id)
        assert loaded_session is not None
        assert loaded_session.title == "Test Session"
        assert loaded_session.metadata == {"custom": "data"}
        assert loaded_session.message_count == 1

        # Verify messages persist
        messages = new_service.get_messages(session.id)
        assert len(messages) == 1
        assert messages[0].content == "Test message"

    def test_session_filtering(self):
        """Test session listing with various filters."""
        project1_id = uuid4()
        project2_id = uuid4()

        # Create sessions
        active_session = self.service.create_session(ChatSessionCreate(
            project_id=project1_id,
            title="Active Session"
        ))
        inactive_session = self.service.create_session(ChatSessionCreate(
            project_id=project1_id,
            title="Inactive Session"
        ))
        self.service.update_session(inactive_session.id, ChatSessionUpdate(is_active=False))

        other_project_session = self.service.create_session(ChatSessionCreate(
            project_id=project2_id,
            title="Other Project"
        ))

        # Test default listing (active only)
        sessions = self.service.list_sessions()
        assert len(sessions) == 2  # active_session and other_project_session
        assert all(s.is_active for s in sessions)

        # Test include inactive
        all_sessions = self.service.list_sessions(include_inactive=True)
        assert len(all_sessions) == 3

        # Test project filtering
        project1_sessions = self.service.list_sessions(project_id=project1_id)
        assert len(project1_sessions) == 1  # only active_session
        assert project1_sessions[0].id == active_session.id

        # Test project filtering with inactive
        project1_all = self.service.list_sessions(project_id=project1_id, include_inactive=True)
        assert len(project1_all) == 2

    def test_session_stats(self):
        """Test session statistics calculation."""
        project1_id = uuid4()
        project2_id = uuid4()

        # Create sessions with messages
        session1 = self.service.create_session(ChatSessionCreate(project_id=project1_id, title="Session 1"))
        session2 = self.service.create_session(ChatSessionCreate(project_id=project1_id, title="Session 2"))
        session3 = self.service.create_session(ChatSessionCreate(project_id=project2_id, title="Session 3"))

        # Add messages
        self.service.add_message(session1.id, MessageCreate(role="user", content="Msg1"))
        self.service.add_message(session1.id, MessageCreate(role="assistant", content="Msg2"))
        self.service.add_message(session2.id, MessageCreate(role="user", content="Msg3"))

        # Make one session inactive
        self.service.update_session(session3.id, ChatSessionUpdate(is_active=False))

        # Get overall stats
        stats = self.service.get_session_stats()
        assert stats.total_sessions == 3
        assert stats.active_sessions == 2
        assert stats.total_messages == 3
        assert stats.average_messages_per_session == 1.0
        assert len(stats.sessions_by_project) == 2
        assert stats.sessions_by_project[str(project1_id)] == 2
        assert stats.sessions_by_project[str(project2_id)] == 1

        # Get project-specific stats
        project1_stats = self.service.get_session_stats(project_id=project1_id)
        assert project1_stats.total_sessions == 2
        assert project1_stats.total_messages == 3
        assert project1_stats.average_messages_per_session == 1.5

    def test_complex_message_history(self):
        """Test complex message history scenarios."""
        session = self.service.create_session(ChatSessionCreate(
            project_id=uuid4(),
            title="Complex Session"
        ))

        # Add various types of messages
        messages = [
            MessageCreate(role="system", content="You are a helpful assistant."),
            MessageCreate(role="user", content="Hello!"),
            MessageCreate(role="assistant", content="Hi there! How can I help?"),
            MessageCreate(role="user", content="Tell me about Python."),
            MessageCreate(role="assistant", content="Python is a programming language..."),
        ]

        for msg in messages:
            self.service.add_message(session.id, msg)

        # Verify message order and content
        retrieved_messages = self.service.get_messages(session.id)
        assert len(retrieved_messages) == 5
        assert retrieved_messages[0].role == "system"
        assert retrieved_messages[1].role == "user"
        assert retrieved_messages[2].role == "assistant"
        assert retrieved_messages[3].role == "user"
        assert retrieved_messages[4].role == "assistant"

        # Verify chronological order
        for i in range(1, len(retrieved_messages)):
            assert retrieved_messages[i].timestamp >= retrieved_messages[i-1].timestamp

    def test_empty_session_operations(self):
        """Test operations on sessions with no messages."""
        session = self.service.create_session(ChatSessionCreate(
            project_id=uuid4(),
            title="Empty Session"
        ))

        # Get messages should return empty list
        messages = self.service.get_messages(session.id)
        assert messages == []

        # Session with messages should have empty messages list
        session_with_messages = self.service.get_session_with_messages(session.id)
        assert len(session_with_messages.messages) == 0

        # Stats should reflect zero messages
        assert session.message_count == 0

    def test_concurrent_session_operations(self):
        """Test that multiple session operations work correctly."""
        # Create multiple sessions
        sessions = []
        for i in range(3):
            session = self.service.create_session(ChatSessionCreate(
                project_id=uuid4(),
                title=f"Session {i+1}"
            ))
            sessions.append(session)

        # Add messages to each session
        for i, session in enumerate(sessions):
            for j in range(i + 1):  # Different number of messages per session
                self.service.add_message(session.id, MessageCreate(
                    role="user",
                    content=f"Message {j+1} in session {i+1}"
                ))

        # Verify each session has correct message count
        for i, session in enumerate(sessions):
            loaded_session = self.service.get_session(session.id)
            assert loaded_session.message_count == i + 1

            messages = self.service.get_messages(session.id)
            assert len(messages) == i + 1

        # Verify listing includes all sessions
        all_sessions = self.service.list_sessions()
        assert len(all_sessions) == 3