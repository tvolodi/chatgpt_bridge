"""
Backend Integration Tests

Tests for API endpoint integrations and service interactions:
- Chat session API endpoints
- Provider management endpoints
- Project management endpoints
- File management endpoints
- End-to-end user workflows
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import shutil
from uuid import uuid4

from backend.main import app
from backend.models.chat_session import ChatSessionCreate, MessageCreate
from backend.models.ai_provider import AIProviderCreate


@pytest.fixture
def test_client():
    """Create a test client for the API."""
    return TestClient(app)


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


class TestChatSessionsAPI:
    """Integration tests for chat sessions endpoints."""

    def test_create_session_endpoint(self, test_client):
        """Test POST /api/chat-sessions."""
        project_id = str(uuid4())
        payload = {
            "project_id": project_id,
            "title": "Test Session",
            "description": "Integration test session"
        }

        response = test_client.post("/api/chat-sessions", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Session"
        assert data["project_id"] == project_id

    def test_get_sessions_endpoint(self, test_client):
        """Test GET /api/chat-sessions."""
        project_id = str(uuid4())
        
        # Create a session first
        create_payload = {
            "project_id": project_id,
            "title": "Test Session"
        }
        create_response = test_client.post("/api/chat-sessions", json=create_payload)
        assert create_response.status_code == 201

        # List sessions
        response = test_client.get(f"/api/chat-sessions?project_id={project_id}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_session_detail(self, test_client):
        """Test GET /api/chat-sessions/{session_id}."""
        project_id = str(uuid4())
        
        # Create session
        create_response = test_client.post(
            "/api/chat-sessions",
            json={"project_id": project_id, "title": "Test"}
        )
        session_id = create_response.json()["id"]

        # Get session
        response = test_client.get(f"/api/chat-sessions/{session_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id

    def test_update_session_endpoint(self, test_client):
        """Test PUT /api/chat-sessions/{session_id}."""
        project_id = str(uuid4())
        
        # Create session
        create_response = test_client.post(
            "/api/chat-sessions",
            json={"project_id": project_id, "title": "Original"}
        )
        session_id = create_response.json()["id"]

        # Update session
        update_payload = {
            "title": "Updated Title",
            "description": "New description"
        }
        response = test_client.put(
            f"/api/chat-sessions/{session_id}",
            json=update_payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"

    def test_delete_session_endpoint(self, test_client):
        """Test DELETE /api/chat-sessions/{session_id}."""
        project_id = str(uuid4())
        
        # Create session
        create_response = test_client.post(
            "/api/chat-sessions",
            json={"project_id": project_id, "title": "Delete Me"}
        )
        session_id = create_response.json()["id"]

        # Delete session
        response = test_client.delete(f"/api/chat-sessions/{session_id}")

        assert response.status_code == 204

        # Verify deletion
        get_response = test_client.get(f"/api/chat-sessions/{session_id}")
        assert get_response.status_code == 404


class TestConversationAPI:
    """Integration tests for conversation endpoints."""

    def setup_method(self):
        """Set up test data."""
        self.project_id = str(uuid4())
        # Create a session for testing
        create_response = TestClient(app).post(
            "/api/chat-sessions",
            json={"project_id": self.project_id, "title": "Test Session"}
        )
        self.session_id = create_response.json()["id"]

    def test_send_message_endpoint(self, test_client):
        """Test POST /api/conversations/send."""
        payload = {
            "session_id": self.session_id,
            "message": "Hello, how are you?",
            "model": "gpt-4"
        }

        response = test_client.post("/api/conversations/send", json=payload)

        assert response.status_code in [200, 201]
        data = response.json()
        assert "message_id" in data or "id" in data

    def test_get_history_endpoint(self, test_client):
        """Test GET /api/conversations/{session_id}/history."""
        response = test_client.get(f"/api/conversations/{self.session_id}/history")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_history_with_pagination(self, test_client):
        """Test pagination on history endpoint."""
        response = test_client.get(
            f"/api/conversations/{self.session_id}/history?limit=10&offset=0"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestProvidersAPI:
    """Integration tests for provider endpoints."""

    def test_get_providers_endpoint(self, test_client):
        """Test GET /api/providers."""
        response = test_client.get("/api/providers")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_active_providers(self, test_client):
        """Test GET /api/providers/active."""
        response = test_client.get("/api/providers/active")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_provider_models(self, test_client):
        """Test GET /api/providers/{provider_id}/models."""
        # First get providers
        providers_response = test_client.get("/api/providers")
        providers = providers_response.json()
        
        if providers:
            provider_id = providers[0]["id"]
            response = test_client.get(f"/api/providers/{provider_id}/models")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    def test_add_provider_config(self, test_client):
        """Test POST /api/providers/{provider_id}/config."""
        # Get first provider
        providers_response = test_client.get("/api/providers")
        providers = providers_response.json()
        
        if providers:
            provider_id = providers[0]["id"]
            payload = {
                "api_key": "test-key-123",
                "custom_headers": {}
            }
            
            response = test_client.post(
                f"/api/providers/{provider_id}/config",
                json=payload
            )
            
            assert response.status_code in [200, 201]


class TestProjectsAPI:
    """Integration tests for project endpoints."""

    def test_create_project_endpoint(self, test_client):
        """Test POST /api/projects."""
        payload = {
            "name": "Test Project",
            "description": "A test project"
        }

        response = test_client.post("/api/projects", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Project"

    def test_get_projects_endpoint(self, test_client):
        """Test GET /api/projects."""
        response = test_client.get("/api/projects")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_project_detail(self, test_client):
        """Test GET /api/projects/{project_id}."""
        # Create a project first
        create_response = test_client.post(
            "/api/projects",
            json={"name": "Test Project"}
        )
        project_id = create_response.json()["id"]

        # Get project
        response = test_client.get(f"/api/projects/{project_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id

    def test_update_project_endpoint(self, test_client):
        """Test PUT /api/projects/{project_id}."""
        # Create project
        create_response = test_client.post(
            "/api/projects",
            json={"name": "Original"}
        )
        project_id = create_response.json()["id"]

        # Update
        response = test_client.put(
            f"/api/projects/{project_id}",
            json={"name": "Updated"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"

    def test_delete_project_endpoint(self, test_client):
        """Test DELETE /api/projects/{project_id}."""
        # Create project
        create_response = test_client.post(
            "/api/projects",
            json={"name": "Delete Me"}
        )
        project_id = create_response.json()["id"]

        # Delete
        response = test_client.delete(f"/api/projects/{project_id}")

        assert response.status_code == 204


class TestFilesAPI:
    """Integration tests for file management endpoints."""

    def test_list_files_endpoint(self, test_client):
        """Test GET /api/files."""
        response = test_client.get("/api/files")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_upload_file_endpoint(self, test_client):
        """Test POST /api/files/upload."""
        # Create test file content
        file_content = b"Test file content"
        files = {"file": ("test.txt", file_content, "text/plain")}
        
        response = test_client.post("/api/files/upload", files=files)

        assert response.status_code in [200, 201]
        data = response.json()
        assert "file_id" in data or "id" in data

    def test_download_file_endpoint(self, test_client):
        """Test GET /api/files/{file_id}."""
        # This would require first uploading a file
        # For now, test the endpoint structure
        test_file_id = str(uuid4())
        response = test_client.get(f"/api/files/{test_file_id}")
        
        # Should return 404 for non-existent file
        assert response.status_code in [404, 200]


class TestSettingsAPI:
    """Integration tests for settings endpoints."""

    def test_get_settings_endpoint(self, test_client):
        """Test GET /api/settings."""
        response = test_client.get("/api/settings")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_update_settings_endpoint(self, test_client):
        """Test PUT /api/settings."""
        payload = {
            "theme": "dark",
            "language": "en"
        }

        response = test_client.put("/api/settings", json=payload)

        assert response.status_code in [200, 201]
        data = response.json()
        assert isinstance(data, dict)


class TestErrorHandling:
    """Tests for error handling across endpoints."""

    def test_invalid_json_payload(self, test_client):
        """Test handling of invalid JSON."""
        response = test_client.post(
            "/api/chat-sessions",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422  # Unprocessable Entity

    def test_missing_required_fields(self, test_client):
        """Test handling of missing required fields."""
        response = test_client.post(
            "/api/chat-sessions",
            json={"title": "Missing project_id"}
        )

        assert response.status_code == 422

    def test_not_found_endpoint(self, test_client):
        """Test 404 response for non-existent endpoints."""
        response = test_client.get("/api/nonexistent")

        assert response.status_code == 404

    def test_invalid_uuid_parameter(self, test_client):
        """Test handling of invalid UUID in path."""
        response = test_client.get("/api/chat-sessions/invalid-uuid")

        assert response.status_code in [400, 422, 404]


class TestWorkflows:
    """Integration tests for complete user workflows."""

    def test_complete_chat_workflow(self, test_client):
        """Test complete workflow: create project -> session -> send message."""
        # Step 1: Create project
        project_response = test_client.post(
            "/api/projects",
            json={"name": "Workflow Test Project"}
        )
        assert project_response.status_code == 201
        project_id = project_response.json()["id"]

        # Step 2: Create session
        session_response = test_client.post(
            "/api/chat-sessions",
            json={"project_id": project_id, "title": "Workflow Test Session"}
        )
        assert session_response.status_code == 201
        session_id = session_response.json()["id"]

        # Step 3: Send message
        message_response = test_client.post(
            "/api/conversations/send",
            json={
                "session_id": session_id,
                "message": "Hello"
            }
        )
        assert message_response.status_code in [200, 201]

        # Step 4: Get history
        history_response = test_client.get(
            f"/api/conversations/{session_id}/history"
        )
        assert history_response.status_code == 200
        history = history_response.json()
        assert isinstance(history, list)

    def test_multi_session_workflow(self, test_client):
        """Test workflow with multiple sessions."""
        project_id = str(uuid4())

        # Create multiple sessions
        session_ids = []
        for i in range(3):
            response = test_client.post(
                "/api/chat-sessions",
                json={"project_id": project_id, "title": f"Session {i}"}
            )
            assert response.status_code == 201
            session_ids.append(response.json()["id"])

        # List sessions for project
        list_response = test_client.get(f"/api/chat-sessions?project_id={project_id}")
        assert list_response.status_code == 200
        sessions = list_response.json()
        
        assert len(sessions) >= 3
        listed_ids = [s["id"] for s in sessions]
        for session_id in session_ids:
            assert session_id in listed_ids

    def test_provider_switching_workflow(self, test_client):
        """Test workflow of switching between providers."""
        # Get available providers
        providers_response = test_client.get("/api/providers")
        assert providers_response.status_code == 200
        providers = providers_response.json()
        
        if len(providers) >= 2:
            # Use first provider
            provider1_id = providers[0]["id"]
            provider1_models = test_client.get(
                f"/api/providers/{provider1_id}/models"
            )
            assert provider1_models.status_code == 200

            # Switch to second provider
            provider2_id = providers[1]["id"]
            provider2_models = test_client.get(
                f"/api/providers/{provider2_id}/models"
            )
            assert provider2_models.status_code == 200
