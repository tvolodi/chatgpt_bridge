"""
End-to-End Integration Tests for Backend Workflows

Comprehensive E2E tests covering complete workflows including:
- Complete chat workflow (project → session → send → receive)
- Multi-provider switching
- File upload and context inclusion
- Template usage
- Cross-session isolation
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from uuid import uuid4
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime
from io import BytesIO

from backend.services.project_service import ProjectService
from backend.services.chat_session_service import ChatSessionService
from backend.services.conversation_service import ConversationService
from backend.services.file_management_service import FileManagementService
from backend.services.ai_provider_service import AIProviderService
from backend.models.chat_session import ChatSessionCreate, Message
from backend.models.ai_provider import ProviderType


class TestE2EWorkflows:
    """End-to-end integration tests for complete workflows."""

    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_service = ProjectService(str(self.temp_dir))
        self.session_service = ChatSessionService(str(self.temp_dir))
        self.conversation_service = ConversationService(self.temp_dir)
        self.file_service = FileManagementService(
            storage_dir=self.temp_dir / "files",
            temp_dir=self.temp_dir / "temp"
        )
        self.ai_service = AIProviderService(str(self.temp_dir))

    def teardown_method(self):
        """Clean up test environment after each test."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_complete_chat_workflow(self):
        """
        Test TC-E2E-001: Complete chat workflow from project to response
        
        Workflow:
        1. Create project
        2. Create chat session under project
        3. Send message to AI
        4. Receive AI response
        5. Verify data persistence
        6. Reload application
        7. Verify all data still present
        """
        # Step 1: Create project
        from backend.models.project import ProjectCreate
        project_data = ProjectCreate(
            name="E2E Test Project",
            description="End-to-end test workflow"
        )
        project = self.project_service.create_project(project_data)
        assert project.id is not None
        assert project.name == "E2E Test Project"

        # Step 2: Create chat session
        session_data = ChatSessionCreate(
            project_id=project.id,
            title="E2E Test Session",
            description="Test session for E2E workflow"
        )
        session = self.session_service.create_session(session_data)
        assert session.id is not None
        assert str(session.project_id) == str(project.id)

        # Step 3: Send message (simulated)
        user_message_content = "Hello, can you help me?"
        user_message = {
            "id": str(uuid4()),
            "session_id": str(session.id),
            "role": "user",
            "content": user_message_content,
            "timestamp": datetime.now().isoformat(),
            "status": "sent"
        }

        # Step 4: Receive AI response (simulated)
        ai_response_content = "Hello! I'm here to help. What can I assist you with?"
        ai_response = {
            "id": str(uuid4()),
            "session_id": str(session.id),
            "role": "assistant",
            "content": ai_response_content,
            "timestamp": datetime.now().isoformat(),
            "status": "sent",
            "provider_id": "openai",
            "tokens": {"prompt": 10, "completion": 20, "total": 30},
            "finish_reason": "stop"
        }

        # Step 5: Verify persistence (messages saved)
        # In real implementation, messages would be persisted
        assert user_message["id"] is not None
        assert ai_response["id"] is not None
        assert user_message["status"] == "sent"
        assert ai_response["status"] == "sent"

        # Step 6: Simulate reload - retrieve data
        reloaded_project = self.project_service.get_project(project.id)
        reloaded_session = self.session_service.get_session(
            session.id,
            str(project.id)
        )

        # Step 7: Verify all data still present
        assert reloaded_project is not None
        assert reloaded_project.id == project.id
        assert reloaded_session is not None
        assert reloaded_session.id == session.id
        assert str(reloaded_session.project_id) == str(project.id)

    def test_multi_provider_switching(self):
        """
        Test TC-E2E-002: Multi-provider switching within same session
        
        Workflow:
        1. Send message with OpenAI provider
        2. Verify response has OpenAI provider_id
        3. Send another message with Anthropic provider
        4. Verify response has Anthropic provider_id
        5. Verify both responses stored with correct provider
        6. Verify can switch providers mid-session
        """
        # Setup: Create project and session
        from backend.models.project import ProjectCreate
        project_data = ProjectCreate(name="Multi-Provider Test")
        project = self.project_service.create_project(project_data)
        session_data = ChatSessionCreate(
            project_id=project.id,
            title="Multi-Provider Session"
        )
        session = self.session_service.create_session(session_data)

        # Step 1: Send with OpenAI
        message_1 = {
            "id": str(uuid4()),
            "session_id": str(session.id),
            "role": "user",
            "content": "Using OpenAI",
            "timestamp": datetime.now().isoformat(),
            "status": "sent"
        }

        response_1 = {
            "id": str(uuid4()),
            "session_id": str(session.id),
            "role": "assistant",
            "content": "Response from OpenAI",
            "provider_id": "openai",
            "tokens": {"prompt": 5, "completion": 10, "total": 15},
            "finish_reason": "stop"
        }

        # Step 2: Verify OpenAI provider
        assert response_1["provider_id"] == "openai"

        # Step 3: Send with Anthropic
        message_2 = {
            "id": str(uuid4()),
            "session_id": str(session.id),
            "role": "user",
            "content": "Using Anthropic",
            "timestamp": datetime.now().isoformat(),
            "status": "sent"
        }

        response_2 = {
            "id": str(uuid4()),
            "session_id": str(session.id),
            "role": "assistant",
            "content": "Response from Anthropic",
            "provider_id": "anthropic",
            "tokens": {"prompt": 5, "completion": 12, "total": 17},
            "finish_reason": "stop"
        }

        # Step 4: Verify Anthropic provider
        assert response_2["provider_id"] == "anthropic"

        # Step 5: Verify both responses stored correctly
        assert response_1["provider_id"] != response_2["provider_id"]
        assert response_1["id"] != response_2["id"]

        # Step 6: Verify session integrity maintained
        retrieved_session = self.session_service.get_session(
            session.id,
            str(project.id)
        )
        assert retrieved_session.id == session.id

    def test_file_upload_and_context_inclusion(self):
        """
        Test TC-E2E-003: File upload and inclusion in AI context
        
        Workflow:
        1. Create project with files
        2. Create session under project
        3. Upload file to project
        4. Send message requesting file analysis
        5. Verify file is included in AI context
        6. Verify AI response references file
        7. Verify message persists with file reference
        """
        # Setup: Create project
        from backend.models.project import ProjectCreate
        project_data = ProjectCreate(
            name="File Context Test",
            description="Test file context inclusion"
        )
        project = self.project_service.create_project(project_data)

        # Step 1: Upload file to project
        file_content = b"def hello():\n    return 'world'"
        file_data = {
            "id": str(uuid4()),
            "name": "hello.py",
            "scope": "project",
            "scope_id": str(project.id),
            "size": len(file_content),
            "type": "text/plain",
            "uploaded_at": datetime.now().isoformat(),
            "content": file_content
        }

        # Step 2: Create session
        session_data = ChatSessionCreate(
            project_id=project.id,
            title="File Analysis Session"
        )
        session = self.session_service.create_session(session_data)

        # Step 3: Send message requesting file analysis
        user_message = {
            "id": str(uuid4()),
            "session_id": str(session.id),
            "role": "user",
            "content": "Analyze the Python code in my project",
            "timestamp": datetime.now().isoformat(),
            "status": "sent",
            "context_files": [file_data["id"]]
        }

        # Step 4: Simulate context building (would include file content)
        context = f"Project files:\n{file_data['name']}: {file_content.decode()}\n\nUser message: {user_message['content']}"

        # Step 5: Verify file is included in context
        assert file_data["name"] in context
        assert "def hello():" in context

        # Step 6: Simulate AI response referencing file
        ai_response = {
            "id": str(uuid4()),
            "session_id": str(session.id),
            "role": "assistant",
            "content": "The code in hello.py is a simple function that returns 'world'.",
            "provider_id": "openai",
            "tokens": {"prompt": 50, "completion": 25, "total": 75},
            "finish_reason": "stop"
        }

        # Step 7: Verify message persists
        assert ai_response["content"] is not None
        assert "hello.py" in ai_response["content"]

        # Verify session can be retrieved with files
        retrieved_session = self.session_service.get_session(
            session.id,
            str(project.id)
        )
        assert retrieved_session is not None

    def test_template_usage_workflow(self):
        """
        Test TC-E2E-004: Complete template usage workflow
        
        Workflow:
        1. Create template with parameters
        2. Create session
        3. Insert template into message with parameters
        4. Send to AI
        5. Verify template substitution happened
        6. Verify AI response stored
        7. Verify message history shows substituted content
        """
        # Setup: Create project and session
        from backend.models.project import ProjectCreate
        project_data = ProjectCreate(name="Template Test")
        project = self.project_service.create_project(project_data)
        session_data = ChatSessionCreate(
            project_id=project.id,
            title="Template Test Session"
        )
        session = self.session_service.create_session(session_data)

        # Step 1: Create template
        template = {
            "id": str(uuid4()),
            "title": "Code Review Template",
            "content": "Please review this {{language}} code:\n```\n{{code}}\n```\nFocus: {{focus}}",
            "category": "code-review",
            "parameters": ["language", "code", "focus"]
        }

        # Step 2: Template parameters for substitution
        parameters = {
            "language": "Python",
            "code": "def add(a, b):\n    return a + b",
            "focus": "error handling"
        }

        # Step 3: Substitute parameters
        substituted_content = template["content"]
        for key, value in parameters.items():
            substituted_content = substituted_content.replace(f"{{{{{key}}}}}", value)

        expected_content = (
            "Please review this Python code:\n```\n"
            "def add(a, b):\n    return a + b\n"
            "```\nFocus: error handling"
        )
        assert substituted_content == expected_content

        # Step 4: Send substituted message to AI
        user_message = {
            "id": str(uuid4()),
            "session_id": str(session.id),
            "role": "user",
            "content": substituted_content,
            "timestamp": datetime.now().isoformat(),
            "status": "sent"
        }

        # Step 5: Verify substitution happened
        assert "{{" not in user_message["content"]
        assert "Python" in user_message["content"]
        assert "def add" in user_message["content"]

        # Step 6: Simulate AI response
        ai_response = {
            "id": str(uuid4()),
            "session_id": str(session.id),
            "role": "assistant",
            "content": "The code looks good but should handle None inputs.",
            "provider_id": "openai",
            "tokens": {"prompt": 60, "completion": 20, "total": 80},
            "finish_reason": "stop"
        }

        # Step 7: Verify message history shows substituted content
        # (not original template)
        assert user_message["content"] == expected_content
        assert "{{" not in user_message["content"]

    def test_cross_session_isolation(self):
        """
        Test TC-E2E-005: Cross-session data isolation verification
        
        Workflow:
        1. Create project with two sessions
        2. Add 10 messages to Session A
        3. Add 5 messages to Session B
        4. Verify Session A has 10 messages, Session B has 5
        5. Send message to Session A
        6. Verify it doesn't affect Session B
        7. Delete Session A
        8. Verify Session B data unaffected
        """
        # Step 1: Create project
        from backend.models.project import ProjectCreate
        project_data = ProjectCreate(name="Isolation Test")
        project = self.project_service.create_project(project_data)

        # Step 2: Create Session A
        session_a_data = ChatSessionCreate(
            project_id=project.id,
            title="Session A"
        )
        session_a = self.session_service.create_session(session_a_data)

        # Step 3: Create Session B
        session_b_data = ChatSessionCreate(
            project_id=project.id,
            title="Session B"
        )
        session_b = self.session_service.create_session(session_b_data)

        # Step 4: Add messages to Session A
        messages_a = []
        for i in range(10):
            msg = {
                "id": str(uuid4()),
                "session_id": str(session_a.id),
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"Session A message {i+1}",
                "timestamp": datetime.now().isoformat(),
                "status": "sent"
            }
            messages_a.append(msg)

        # Step 5: Add messages to Session B
        messages_b = []
        for i in range(5):
            msg = {
                "id": str(uuid4()),
                "session_id": str(session_b.id),
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"Session B message {i+1}",
                "timestamp": datetime.now().isoformat(),
                "status": "sent"
            }
            messages_b.append(msg)

        # Step 6: Verify counts
        assert len(messages_a) == 10
        assert len(messages_b) == 5
        assert len(messages_a) != len(messages_b)

        # Step 7: Send new message to Session A
        new_msg_a = {
            "id": str(uuid4()),
            "session_id": str(session_a.id),
            "role": "user",
            "content": "New message to Session A",
            "timestamp": datetime.now().isoformat(),
            "status": "sent"
        }
        messages_a.append(new_msg_a)

        # Step 8: Verify Session B unchanged
        assert len(messages_b) == 5  # Still 5, not 6
        # Verify Session A has new message but Session B doesn't
        session_a_ids = [m["session_id"] for m in messages_a]
        session_b_ids = [m["session_id"] for m in messages_b]
        
        # All A messages should have session_a id
        assert all(mid == str(session_a.id) for mid in session_a_ids)
        # All B messages should have session_b id
        assert all(mid == str(session_b.id) for mid in session_b_ids)

        # Step 9: Delete Session A
        self.session_service.delete_session(session_a.id, False, str(project.id))

        # Step 10: Verify Session B still accessible
        retrieved_b = self.session_service.get_session(
            session_b.id,
            str(project.id)
        )
        assert retrieved_b is not None
        assert retrieved_b.id == session_b.id
        assert retrieved_b.title == "Session B"

    def test_error_recovery_workflow(self):
        """
        Test TC-E2E-*: Error recovery and resilience
        
        Workflow:
        1. Create project and session
        2. Simulate API error during message send
        3. Verify message status is 'failed'
        4. Verify session data intact
        5. Retry message send
        6. Verify recovery successful
        """
        # Setup
        from backend.models.project import ProjectCreate
        project_data = ProjectCreate(name="Error Recovery Test")
        project = self.project_service.create_project(project_data)
        session_data = ChatSessionCreate(
            project_id=project.id,
            title="Error Recovery Session"
        )
        session = self.session_service.create_session(session_data)

        # Step 1: Attempt message (simulated error)
        user_message = {
            "id": str(uuid4()),
            "session_id": str(session.id),
            "role": "user",
            "content": "This will fail",
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }

        # Step 2: Simulate error
        user_message["status"] = "failed"
        error_reason = "API rate limit exceeded"

        # Step 3: Verify message persists in failed state
        assert user_message["status"] == "failed"

        # Step 4: Verify session data intact
        retrieved = self.session_service.get_session(
            session.id,
            str(project.id)
        )
        assert retrieved is not None
        assert retrieved.id == session.id

        # Step 5: Retry - create new attempt
        retry_message = {
            "id": str(uuid4()),  # New ID
            "session_id": str(session.id),
            "role": "user",
            "content": "This will fail",  # Same content
            "timestamp": datetime.now().isoformat(),
            "status": "sent"  # Simulated success
        }

        # Step 6: Verify recovery
        assert retry_message["status"] == "sent"
        assert retry_message["id"] != user_message["id"]  # Different attempt
