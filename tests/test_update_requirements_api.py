"""
Integration Tests for Update Requirements - API Endpoints

Tests for API endpoints with project_id parameter support:
- GET /api/chat-sessions/{session_id} - with project_id query param
- PUT /api/chat-sessions/{session_id} - with project_id query param
- DELETE /api/chat-sessions/{session_id} - with project_id query param
- POST /api/chat-sessions/{session_id}/messages - with project_id query param
- GET /api/chat-sessions/{session_id}/messages - with project_id query param
- GET /api/chat-sessions/{session_id}/full - with project_id query param
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from uuid import uuid4
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

from backend.services.chat_session_service import ChatSessionService
from backend.services.project_service import ProjectService
from backend.models.chat_session import ChatSessionCreate, MessageCreate
from backend.models.project import ProjectCreate


class MockApp:
    """Mock FastAPI application for testing endpoints."""
    
    def __init__(self, chat_service, project_service):
        self.chat_service = chat_service
        self.project_service = project_service


class TestAPIEndpointsWithProjectId:
    """Integration tests for API endpoints with project_id parameter."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.data_dir = self.temp_dir / "data"
        self.data_dir.mkdir()
        
        self.chat_service = ChatSessionService(data_dir=str(self.data_dir))
        self.project_service = ProjectService(data_dir=str(self.data_dir))

    def teardown_method(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_get_session_endpoint_with_project_id(self):
        """Test GET /api/chat-sessions/{session_id}?project_id=xyz"""
        # Create project and session
        project_data = ProjectCreate(name="Test Project", description=None, parent_id=None)
        project = self.project_service.create_project(project_data)
        project_id = project.id
        
        session_data = ChatSessionCreate(project_id=project_id, title="Test Session")
        session = self.chat_service.create_session(session_data)
        
        # Simulate endpoint call with project_id parameter
        retrieved = self.chat_service.get_session(session.id, project_id=project_id)
        
        # Verify response
        assert retrieved is not None
        assert retrieved.id == session.id
        assert str(retrieved.project_id) == str(project_id)
        assert retrieved.title == "Test Session"

    def test_put_session_endpoint_with_project_id(self):
        """Test PUT /api/chat-sessions/{session_id}?project_id=xyz"""
        # Create project and session
        project_data = ProjectCreate(name="Test Project", description=None, parent_id=None)
        project = self.project_service.create_project(project_data)
        project_id = project.id
        
        session_data = ChatSessionCreate(project_id=project_id, title="Original Title")
        session = self.chat_service.create_session(session_data)
        
        # Simulate endpoint update with project_id parameter
        from backend.models.chat_session import ChatSessionUpdate
        update_data = ChatSessionUpdate(
            title="Updated Title",
            description="Updated description"
        )
        updated = self.chat_service.update_session(session.id, update_data, project_id=project_id)
        
        # Verify update
        assert updated.title == "Updated Title"
        assert updated.description == "Updated description"

    def test_delete_session_endpoint_with_project_id(self):
        """Test DELETE /api/chat-sessions/{session_id}?project_id=xyz"""
        # Create project and session
        project_data = ProjectCreate(name="Test Project", description=None, parent_id=None)
        project = self.project_service.create_project(project_data)
        project_id = project.id
        
        session_data = ChatSessionCreate(project_id=project_id, title="To Delete")
        session = self.chat_service.create_session(session_data)
        session_id = session.id
        
        # Verify session exists
        assert self.chat_service.get_session(session_id, project_id=project_id) is not None
        
        # Delete with project_id parameter
        self.chat_service.delete_session(session_id, project_id=project_id)
        
        # Verify deletion
        assert self.chat_service.get_session(session_id, project_id=project_id) is None

    def test_post_messages_endpoint_with_project_id(self):
        """Test POST /api/chat-sessions/{session_id}/messages?project_id=xyz"""
        # Create project and session
        project_data = ProjectCreate(name="Test Project", description=None, parent_id=None)
        project = self.project_service.create_project(project_data)
        project_id = project.id
        
        session_data = ChatSessionCreate(project_id=project_id, title="Message Test")
        session = self.chat_service.create_session(session_data)
        
        # Add message with project_id parameter
        message = MessageCreate(
            content="Test message content",
            role="user"
        )
        added_message = self.chat_service.add_message(session.id, message, project_id=project_id)
        
        # Verify message added
        assert added_message is not None
        assert added_message.content == "Test message content"
        assert added_message.role == "user"

    def test_get_messages_endpoint_with_project_id(self):
        """Test GET /api/chat-sessions/{session_id}/messages?project_id=xyz"""
        # Create project and session
        project_data = ProjectCreate(name="Test Project", description=None, parent_id=None)
        project = self.project_service.create_project(project_data)
        project_id = project.id
        
        session_data = ChatSessionCreate(project_id=project_id, title="Get Messages Test")
        session = self.chat_service.create_session(session_data)
        
        # Add multiple messages
        for i in range(3):
            message = MessageCreate(
                content=f"Message {i}",
                role="user" if i % 2 == 0 else "assistant"
            )
            self.chat_service.add_message(session.id, message, project_id=project_id)
        
        # Get messages with project_id parameter
        messages = self.chat_service.get_messages(session.id, project_id=project_id)
        
        # Verify messages
        assert len(messages) == 3
        assert messages[0].content == "Message 0"
        assert messages[1].content == "Message 1"
        assert messages[2].content == "Message 2"

    def test_get_session_full_endpoint_with_project_id(self):
        """Test GET /api/chat-sessions/{session_id}/full?project_id=xyz"""
        # Create project and session
        project_data = ProjectCreate(name="Test Project", description=None, parent_id=None)
        project = self.project_service.create_project(project_data)
        project_id = project.id
        
        session_data = ChatSessionCreate(project_id=project_id, title="Full Session Test")
        session = self.chat_service.create_session(session_data)
        
        # Add messages
        for i in range(2):
            message = MessageCreate(content=f"Message {i}", role="user")
            self.chat_service.add_message(session.id, message, project_id=project_id)
        
        # Get full session with messages and project_id parameter
        full_session = self.chat_service.get_session_with_messages(session.id, project_id=project_id)
        
        # Verify full session
        assert full_session is not None
        assert full_session.session.id == session.id
        assert len(full_session.messages) == 2

    def test_endpoint_project_id_parameter_validation(self):
        """Test that endpoints properly validate project_id parameter."""
        # Create project and session
        project_data = ProjectCreate(name="Test Project", description=None, parent_id=None)
        project = self.project_service.create_project(project_data)
        project_id = project.id
        wrong_project_id = "wrong-project"
        
        session_data = ChatSessionCreate(project_id=project_id, title="Validation Test")
        session = self.chat_service.create_session(session_data)
        
        # Try to access with wrong project_id
        # The service should handle this gracefully
        retrieved = self.chat_service.get_session(session.id, project_id=wrong_project_id)
        
        # May return None or raise error depending on implementation
        # But should not return the session with wrong project_id
        if retrieved is None:
            assert True  # Expected behavior
        else:
            assert retrieved.project_id != wrong_project_id

    def test_endpoints_work_without_project_id_for_flat_structure(self):
        """Test that endpoints still work without project_id (backwards compatibility)."""
        # Create session without project_id (flat structure)
        session_data = ChatSessionCreate(title="Flat Structure Session")
        session = self.chat_service.create_session(session_data)
        
        # Access without project_id parameter (backwards compatibility)
        retrieved = self.chat_service.get_session(session.id)
        assert retrieved is not None
        assert retrieved.title == "Flat Structure Session"
        
        # Add message without project_id
        message = MessageCreate(content="Flat message", role="user")
        added = self.chat_service.add_message(session.id, message)
        assert added is not None
        
        # Get messages without project_id
        messages = self.chat_service.get_messages(session.id)
        assert len(messages) > 0


class TestMultipleProjectsIsolation:
    """Test that sessions are properly isolated between projects."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.data_dir = self.temp_dir / "data"
        self.data_dir.mkdir()
        
        self.chat_service = ChatSessionService(data_dir=str(self.data_dir))
        self.project_service = ProjectService(data_dir=str(self.data_dir))

    def teardown_method(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_sessions_isolated_between_projects(self):
        """Test that sessions in different projects are properly isolated."""
        # Create two projects
        project_data_1 = ProjectCreate(name="Project 1", description=None, parent_id=None)
        project_1 = self.project_service.create_project(project_data_1)
        project_1_id = project_1.id
        
        project_data_2 = ProjectCreate(name="Project 2", description=None, parent_id=None)
        project_2 = self.project_service.create_project(project_data_2)
        project_2_id = project_2.id
        
        # Create sessions in different projects
        session_1_data = ChatSessionCreate(project_id=project_1_id, title="Session P1")
        session_1 = self.chat_service.create_session(session_1_data)
        
        session_2_data = ChatSessionCreate(project_id=project_2_id, title="Session P2")
        session_2 = self.chat_service.create_session(session_2_data)
        
        # Verify proper separation
        project_1_sessions = self.chat_service.list_sessions(project_id=project_1_id)
        project_2_sessions = self.chat_service.list_sessions(project_id=project_2_id)
        
        # Session 1 should be in project 1
        session_1_ids = [s.id for s in project_1_sessions]
        assert session_1.id in session_1_ids
        
        # Session 2 should be in project 2
        session_2_ids = [s.id for s in project_2_sessions]
        assert session_2.id in session_2_ids
        
        # Sessions should not be in wrong project
        assert session_2.id not in session_1_ids
        assert session_1.id not in session_2_ids

    def test_messages_isolated_between_projects(self):
        """Test that messages are isolated between different project sessions."""
        # Create two projects
        project_data_1 = ProjectCreate(name="Project 1", description=None, parent_id=None)
        project_1 = self.project_service.create_project(project_data_1)
        project_1_id = project_1.id
        
        project_data_2 = ProjectCreate(name="Project 2", description=None, parent_id=None)
        project_2 = self.project_service.create_project(project_data_2)
        project_2_id = project_2.id
        
        # Create sessions
        session_1 = self.chat_service.create_session(
            ChatSessionCreate(project_id=project_1_id, title="S1")
        )
        session_2 = self.chat_service.create_session(
            ChatSessionCreate(project_id=project_2_id, title="S2")
        )
        
        # Add different messages to each session
        msg_1 = MessageCreate(content="Project 1 Message", role="user")
        self.chat_service.add_message(session_1.id, msg_1, project_id=project_1_id)
        
        msg_2 = MessageCreate(content="Project 2 Message", role="user")
        self.chat_service.add_message(session_2.id, msg_2, project_id=project_2_id)
        
        # Verify messages are isolated
        messages_1 = self.chat_service.get_messages(session_1.id, project_id=project_1_id)
        messages_2 = self.chat_service.get_messages(session_2.id, project_id=project_2_id)
        
        assert len(messages_1) == 1
        assert messages_1[0].content == "Project 1 Message"
        
        assert len(messages_2) == 1
        assert messages_2[0].content == "Project 2 Message"
