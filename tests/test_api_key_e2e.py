"""
End-to-end test verifying that API key updates work correctly
regardless of the working directory when the server starts
"""
import pytest
import json
import os
from pathlib import Path
from uuid import uuid4
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.ai_provider_service import AIProviderService


@pytest.fixture
def client():
    """Create a test client for the API."""
    return TestClient(app)


def test_api_key_saved_to_env_with_absolute_path(client):
    """
    Test that API keys are saved to .env file using absolute path.
    This test verifies the fix works regardless of current working directory.
    """
    # Create a new provider
    provider_data = {
        "name": "TestOpenAI_E2E",
        "provider_type": "openai",
        "api_key": "sk-original-key-e2e",
        "base_url": None,
        "organization_id": None,
        "rate_limit_requests": 60,
        "rate_limit_tokens": 100000,
        "timeout_seconds": 30,
        "retry_attempts": 3,
        "is_active": True
    }
    
    # Create provider
    response = client.post("/api/ai-providers/", json=provider_data)
    assert response.status_code == 201, f"Failed to create provider: {response.text}"
    created_provider = response.json()
    provider_id = created_provider["id"]
    
    # Verify original key is in .env file
    env_file = Path("c:\\pf\\AI-Chat-Assistant\\.env")
    if not env_file.exists():
        env_file = Path(".env")
    
    assert env_file.exists(), f".env file not found at {env_file}"
    env_content = env_file.read_text()
    assert "PROVIDER_API_KEY_TESTOPENAI_E2E=" in env_content, ".env should contain provider key"
    assert "sk-original-key-e2e" in env_content, ".env should contain original key"
    
    # Verify original key is NOT in JSON file
    json_file = Path("data/ai_providers") / f"{provider_id}.json"
    assert json_file.exists(), f"JSON file not found at {json_file}"
    with open(json_file, 'r') as f:
        json_content = json.load(f)
        assert 'api_key' not in json_content, "JSON file should NOT contain api_key"
    
    # Update the provider with a new API key
    update_data = {"api_key": "sk-updated-key-e2e-99999"}
    update_response = client.put(f"/api/ai-providers/{provider_id}", json=update_data)
    assert update_response.status_code == 200, f"Failed to update provider: {update_response.text}"
    
    # Verify the updated key is returned in the response
    updated_provider = update_response.json()
    assert updated_provider["api_key"] == "sk-updated-key-e2e-99999"
    
    # Verify updated key is in .env file
    env_content = env_file.read_text()
    assert "PROVIDER_API_KEY_TESTOPENAI_E2E=" in env_content, ".env should still contain provider key after update"
    assert "sk-updated-key-e2e-99999" in env_content, ".env should contain updated key"
    
    # Verify updated key is NOT in JSON file
    with open(json_file, 'r') as f:
        json_content = json.load(f)
        assert 'api_key' not in json_content, "JSON file should NOT contain api_key after update"
    
    # Clean up
    if json_file.exists():
        json_file.unlink()


def test_service_finds_env_file_correctly(client):
    """
    Test that AIProviderService correctly resolves the .env file path.
    This verifies the absolute path calculation is working.
    """
    # Create a new service instance
    service = AIProviderService()
    
    # Verify the env_file_path is set correctly
    assert service.env_file_path is not None, "env_file_path should be set"
    assert service.env_file_path.exists(), f"env_file_path should exist: {service.env_file_path}"
    assert str(service.env_file_path).endswith(".env"), "env_file_path should end with .env"
    
    # Verify it's an absolute path
    assert service.env_file_path.is_absolute(), f"env_file_path should be absolute: {service.env_file_path}"
    
    # Verify env_file_path points to .env in current working directory
    expected_path = Path.cwd() / ".env"
    assert service.env_file_path == expected_path, \
        f"env_file_path should be in current working directory: {expected_path}"


def test_provider_key_persists_across_requests(client):
    """
    Test that a provider's API key persists correctly across multiple requests.
    This verifies the singleton service instance is working.
    """
    # Create a provider
    provider_data = {
        "name": "PersistenceTest",
        "provider_type": "openai",
        "api_key": "sk-persistence-test-key",
        "is_active": True
    }
    
    response1 = client.post("/api/ai-providers/", json=provider_data)
    assert response1.status_code == 201
    provider_id = response1.json()["id"]
    created_key = response1.json()["api_key"]
    
    # Verify the key is returned
    assert created_key == "sk-persistence-test-key"
    
    # Fetch the provider in a new request
    response2 = client.get(f"/api/ai-providers/{provider_id}")
    assert response2.status_code == 200
    fetched_provider = response2.json()
    
    # Verify the key is still available
    assert fetched_provider["api_key"] == "sk-persistence-test-key", \
        "API key should persist across requests"
    
    # Update the provider
    update_data = {"api_key": "sk-persistence-updated"}
    response3 = client.put(f"/api/ai-providers/{provider_id}", json=update_data)
    assert response3.status_code == 200
    updated_provider = response3.json()
    assert updated_provider["api_key"] == "sk-persistence-updated"
    
    # Fetch again to verify persistence
    response4 = client.get(f"/api/ai-providers/{provider_id}")
    assert response4.status_code == 200
    final_provider = response4.json()
    assert final_provider["api_key"] == "sk-persistence-updated", \
        "Updated API key should persist across requests"
    
    # Clean up
    json_file = Path("data/ai_providers") / f"{provider_id}.json"
    if json_file.exists():
        json_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
