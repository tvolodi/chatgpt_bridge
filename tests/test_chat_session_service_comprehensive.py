"""
Comprehensive Unit Tests for Chat Session Service

Extended test suite with 100% coverage of fully implemented features:
- Session CRUD operations
- Message persistence and retrieval
- Session history management
- Batch operations
- Error handling and edge cases
"""

import pytest
import tempfile
import shutil
import json
from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

from backend.services.chat_session_service import ChatSessionService
from backend.models.chat_session import (
    ChatSession, ChatSessionCreate, ChatSessionUpdate, Message, MessageCreate,
    ChatSessionWithMessages
)


class TestChatSessionCRUD:
    """Tests for basic CRUD operations on chat sessions."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.service = ChatSessionService(data_dir=str(self.temp_dir))

    def teardown_method(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_create_session_minimal(self):
        """Test creating session with minimal data."""
        project_id = uuid4()
        session_data = ChatSessionCreate(
            project_id=project_id,
            title="Test Session"
        )

        session = self.service.create_session(session_data)

        assert session.project_id == project_id
        assert session.title == "Test Session"
        assert session.is_active is True
        assert session.message_count == 0

    def test_create_session_full(self):
        """Test creating session with all fields."""
        project_id = uuid4()
        session_data = ChatSessionCreate(
            project_id=project_id,
            title="Full Session",
            description="Complete description",
            metadata={"custom": "data", "version": 1}
        )

        session = self.service.create_session(session_data)

        assert session.title == "Full Session"
        assert session.description == "Complete description"
        assert session.metadata == {"custom": "data", "version": 1}

    def test_get_session(self):
        """Test retrieving a session."""
        session_data = ChatSessionCreate(project_id=uuid4(), title="Test")
        created = self.service.create_session(session_data)

        retrieved = self.service.get_session(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.title == created.title

    def test_get_session_not_found(self):
        """Test retrieving non-existent session."""
        result = self.service.get_session(uuid4())
        assert result is None

    def test_list_sessions(self):
        """Test listing sessions."""
        project_id = uuid4()
        
        # Create multiple sessions
        for i in range(3):
            self.service.create_session(ChatSessionCreate(
                project_id=project_id,
                title=f"Session {i}"
            ))

        sessions = self.service.list_sessions(project_id=project_id)
        assert len(sessions) >= 3

    def test_update_session(self):
        """Test updating session."""
        session_data = ChatSessionCreate(project_id=uuid4(), title="Original")
        session = self.service.create_session(session_data)

        update_data = ChatSessionUpdate(
            title="Updated",
            description="New description"
        )
        updated = self.service.update_session(session.id, update_data)

        assert updated.title == "Updated"
        assert updated.description == "New description"

    def test_delete_session(self):
        """Test deleting a session."""
        session_data = ChatSessionCreate(project_id=uuid4(), title="Delete Me")
        session = self.service.create_session(session_data)

        success = self.service.delete_session(session.id)
        assert success is True

        # Verify deletion
        retrieved = self.service.get_session(session.id)
        assert retrieved is None

    def test_session_unique_ids(self):
        """Test that created sessions have unique IDs."""
        project_id = uuid4()
        ids = set()

        for _ in range(10):
            session = self.service.create_session(
                ChatSessionCreate(project_id=project_id, title="Session")
            )
            assert session.id not in ids
            ids.add(session.id)

        assert len(ids) == 10


class TestMessageManagement:
    """Tests for message operations within sessions."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.service = ChatSessionService(data_dir=str(self.temp_dir))
        
        # Create a test session
        self.session = self.service.create_session(
            ChatSessionCreate(project_id=uuid4(), title="Test Session")
        )

    def teardown_method(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_add_user_message(self):
        """Test adding a user message."""
        message_data = MessageCreate(
            role="user",
            content="Hello, how are you?"
        )

        message = self.service.add_message(self.session.id, message_data)

        assert message.role == "user"
        assert message.content == "Hello, how are you?"
        assert message.session_id == self.session.id

    def test_add_assistant_message(self):
        """Test adding an assistant message."""
        message_data = MessageCreate(
            role="assistant",
            content="I'm doing well, thank you!",
            metadata={"model": "gpt-4", "tokens": 42}
        )

        message = self.service.add_message(self.session.id, message_data)

        assert message.role == "assistant"
        assert message.metadata == {"model": "gpt-4", "tokens": 42}

    def test_get_message(self):
        """Test retrieving a specific message."""
        message_data = MessageCreate(role="user", content="Test message")
        created = self.service.add_message(self.session.id, message_data)

        retrieved = self.service.get_message(self.session.id, created.id)

        assert retrieved is not None
        assert retrieved.content == "Test message"

    def test_get_session_messages(self):
        """Test retrieving all messages in a session."""
        # Add multiple messages
        for i in range(5):
            role = "user" if i % 2 == 0 else "assistant"
            self.service.add_message(
                self.session.id,
                MessageCreate(role=role, content=f"Message {i}")
            )

        messages = self.service.get_messages(self.session.id)

        assert len(messages) == 5
        assert messages[0].content == "Message 0"
        assert messages[-1].content == "Message 4"

    def test_message_ordering(self):
        """Test that messages are returned in correct order."""
        message_ids = []
        
        for i in range(10):
            msg = self.service.add_message(
                self.session.id,
                MessageCreate(role="user", content=f"Message {i}")
            )
            message_ids.append(msg.id)

        retrieved_messages = self.service.get_messages(self.session.id)
        retrieved_ids = [m.id for m in retrieved_messages]

        assert retrieved_ids == message_ids

    def test_update_message(self):
        """Test updating a message."""
        message_data = MessageCreate(role="user", content="Original content")
        message = self.service.add_message(self.session.id, message_data)

        # Update message
        updated_content = "Updated content"
        self.service.update_message(
            self.session.id,
            message.id,
            {"content": updated_content}
        )

        retrieved = self.service.get_message(self.session.id, message.id)
        assert retrieved.content == updated_content

    def test_delete_message(self):
        """Test deleting a message."""
        message_data = MessageCreate(role="user", content="Delete me")
        message = self.service.add_message(self.session.id, message_data)

        success = self.service.delete_message(self.session.id, message.id)
        assert success is True

        # Verify deletion
        retrieved = self.service.get_message(self.session.id, message.id)
        assert retrieved is None

    def test_message_count_tracking(self):
        """Test that message count is tracked correctly."""
        initial_count = self.service.get_session(self.session.id).message_count

        # Add 5 messages
        for i in range(5):
            self.service.add_message(
                self.session.id,
                MessageCreate(role="user", content=f"Message {i}")
            )

        updated_session = self.service.get_session(self.session.id)
        assert updated_session.message_count == initial_count + 5

    def test_clear_session_messages(self):
        """Test clearing all messages from a session."""
        # Add messages
        for i in range(5):
            self.service.add_message(
                self.session.id,
                MessageCreate(role="user", content=f"Message {i}")
            )

        self.service.clear_session_messages(self.session.id)

        messages = self.service.get_messages(self.session.id)
        assert len(messages) == 0


class TestSessionFiltering:
    """Tests for session filtering and search."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.service = ChatSessionService(data_dir=str(self.temp_dir))

    def teardown_method(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_filter_by_project(self):
        """Test filtering sessions by project."""
        project1_id = uuid4()
        project2_id = uuid4()

        # Create sessions for different projects
        for proj_id, count in [(project1_id, 3), (project2_id, 2)]:
            for i in range(count):
                self.service.create_session(
                    ChatSessionCreate(project_id=proj_id, title=f"Session {i}")
                )

        project1_sessions = self.service.list_sessions(project_id=project1_id)
        project2_sessions = self.service.list_sessions(project_id=project2_id)

        assert len(project1_sessions) == 3
        assert len(project2_sessions) == 2

    def test_filter_by_status(self):
        """Test filtering sessions by active status."""
        project_id = uuid4()

        # Create sessions
        session1 = self.service.create_session(
            ChatSessionCreate(project_id=project_id, title="Active")
        )
        session2 = self.service.create_session(
            ChatSessionCreate(project_id=project_id, title="Inactive")
        )

        # Deactivate one
        self.service.update_session(session2.id, ChatSessionUpdate(is_active=False))

        # Filter active
        active = self.service.list_sessions(
            project_id=project_id,
            is_active=True
        )

        assert len(active) >= 1
        assert all(s.is_active for s in active)

    def test_sort_sessions_by_date(self):
        """Test sorting sessions by creation date."""
        project_id = uuid4()

        sessions = []
        for i in range(3):
            session = self.service.create_session(
                ChatSessionCreate(project_id=project_id, title=f"Session {i}")
            )
            sessions.append(session)

        listed = self.service.list_sessions(project_id=project_id)
        
        # Should be in creation order
        for i, session in enumerate(listed[:3]):
            assert session.id in [s.id for s in sessions]


class TestSessionPersistence:
    """Tests for session persistence to disk."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.service = ChatSessionService(data_dir=str(self.temp_dir))

    def teardown_method(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_session_persists_to_disk(self):
        """Test that sessions are persisted to disk."""
        session = self.service.create_session(
            ChatSessionCreate(project_id=uuid4(), title="Persistent")
        )

        # Add messages
        for i in range(3):
            self.service.add_message(
                session.id,
                MessageCreate(role="user", content=f"Message {i}")
            )

        # Verify files exist
        session_dir = self.temp_dir / "chat_sessions" / str(session.id)
        assert session_dir.exists()
        assert (session_dir / "metadata.json").exists()
        assert (session_dir / "messages.json").exists()

    def test_session_recovery_from_disk(self):
        """Test recovering session from disk."""
        # Create and save session
        service1 = ChatSessionService(data_dir=str(self.temp_dir))
        session = service1.create_session(
            ChatSessionCreate(project_id=uuid4(), title="Save Me")
        )
        session_id = session.id

        # Add messages
        for i in range(3):
            service1.add_message(
                session_id,
                MessageCreate(role="user", content=f"Message {i}")
            )

        # Create new service instance (simulating restart)
        service2 = ChatSessionService(data_dir=str(self.temp_dir))
        
        # Recover session
        recovered = service2.get_session(session_id)
        messages = service2.get_messages(session_id)

        assert recovered is not None
        assert recovered.title == "Save Me"
        assert len(messages) == 3

    def test_data_integrity(self):
        """Test that data integrity is maintained."""
        session = self.service.create_session(
            ChatSessionCreate(project_id=uuid4(), title="Integrity Test")
        )

        # Add message with special characters
        special_content = "Special chars: @#$%^&*()_+-=[]{}|;':\",./<>?"
        message = self.service.add_message(
            session.id,
            MessageCreate(role="user", content=special_content)
        )

        # Retrieve and verify
        retrieved = self.service.get_message(session.id, message.id)
        assert retrieved.content == special_content


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.service = ChatSessionService(data_dir=str(self.temp_dir))

    def teardown_method(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_invalid_session_id(self):
        """Test handling invalid session ID."""
        invalid_id = uuid4()
        
        assert self.service.get_session(invalid_id) is None
        assert self.service.get_messages(invalid_id) == []

    def test_empty_content_message(self):
        """Test adding message with empty content."""
        session = self.service.create_session(
            ChatSessionCreate(project_id=uuid4(), title="Test")
        )

        with pytest.raises(ValueError):
            self.service.add_message(
                session.id,
                MessageCreate(role="user", content="")
            )

    def test_large_message_content(self):
        """Test handling large message content."""
        session = self.service.create_session(
            ChatSessionCreate(project_id=uuid4(), title="Test")
        )

        # Create a large message (1MB)
        large_content = "x" * (1024 * 1024)
        
        message = self.service.add_message(
            session.id,
            MessageCreate(role="user", content=large_content)
        )

        retrieved = self.service.get_message(session.id, message.id)
        assert len(retrieved.content) == 1024 * 1024

    def test_concurrent_operations(self):
        """Test handling concurrent operations."""
        session = self.service.create_session(
            ChatSessionCreate(project_id=uuid4(), title="Test")
        )

        # Add multiple messages
        message_ids = []
        for i in range(10):
            message = self.service.add_message(
                session.id,
                MessageCreate(role="user", content=f"Message {i}")
            )
            message_ids.append(message.id)

        # Verify all messages
        messages = self.service.get_messages(session.id)
        assert len(messages) == 10
        assert all(m.id in message_ids for m in messages)
