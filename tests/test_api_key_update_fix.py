"""
Test to verify that API keys are correctly saved to .env file when updated via API
"""
import pytest
import json
import os
from pathlib import Path
from uuid import uuid4
from datetime import datetime
from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.main import app
from backend.models.ai_provider import AIProviderCreate, ProviderType, AIProviderUpdate
from backend.services.ai_provider_service import AIProviderService


@pytest.fixture
def client():
    """Create a test client for the API."""
    return TestClient(app)


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory for tests."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return str(data_dir)


@pytest.fixture
def temp_env_file(tmp_path):
    """Create a temporary .env file for tests."""
    env_file = tmp_path / ".env"
    env_file.write_text("# Test .env file\n")
    return str(env_file)


def test_api_key_saved_to_env_on_update(client):
    """
    Test that API keys are saved to .env file when a provider is updated.
    This test verifies the fix for the singleton pattern issue.
    """
    # Create a new provider
    provider_data = {
        "name": "TestOpenAI",
        "provider_type": "openai",
        "api_key": "sk-original-key-12345",
        "base_url": None,
        "organization_id": None,
        "rate_limit_requests": 60,
        "rate_limit_tokens": 100000,
        "timeout_seconds": 30,
        "retry_attempts": 3,
        "is_active": True
    }
    
    # Create provider
    create_response = client.post("/api/ai-providers/", json=provider_data)
    assert create_response.status_code == 201
    created_provider = create_response.json()
    provider_id = created_provider["id"]
    
    # Verify original key is NOT in JSON file (only in .env)
    json_file = Path("data/ai_providers") / f"{provider_id}.json"
    assert json_file.exists()
    
    with open(json_file, 'r') as f:
        json_content = json.load(f)
        assert 'api_key' not in json_content, "API key should not be in JSON file"
    
    # Verify original key IS in .env file
    env_file = Path(".env")
    assert env_file.exists()
    env_content = env_file.read_text()
    assert "PROVIDER_API_KEY_TESTOPENAI=" in env_content
    assert "sk-original-key-12345" in env_content
    
    # Now update the provider with a new API key
    update_data = {
        "api_key": "sk-updated-key-99999"
    }
    
    update_response = client.put(f"/api/ai-providers/{provider_id}", json=update_data)
    assert update_response.status_code == 200
    updated_provider = update_response.json()
    
    # Verify the updated key is returned in the response
    assert updated_provider["api_key"] == "sk-updated-key-99999"
    
    # Verify updated key is NOT in JSON file
    with open(json_file, 'r') as f:
        json_content = json.load(f)
        assert 'api_key' not in json_content, "Updated API key should not be in JSON file"
    
    # Verify updated key IS in .env file
    env_content = env_file.read_text()
    assert "PROVIDER_API_KEY_TESTOPENAI=" in env_content
    assert "sk-updated-key-99999" in env_content
    
    # Verify the old key is replaced (not just appended)
    lines = env_content.strip().split('\n')
    provider_key_lines = [line for line in lines if 'PROVIDER_API_KEY_TESTOPENAI=' in line]
    assert len(provider_key_lines) == 1, "Should only have one entry for PROVIDER_API_KEY_TESTOPENAI"
    assert "sk-updated-key-99999" in provider_key_lines[0]
    
    # Verify singleton: Create another update to same provider - should still work
    update_data2 = {
        "api_key": "sk-third-update-77777"
    }
    
    update_response2 = client.put(f"/api/ai-providers/{provider_id}", json=update_data2)
    assert update_response2.status_code == 200
    final_provider = update_response2.json()
    assert final_provider["api_key"] == "sk-third-update-77777"
    
    # Verify final key is in .env
    env_content = env_file.read_text()
    assert "sk-third-update-77777" in env_content
    
    # Clean up
    if json_file.exists():
        json_file.unlink()


def test_multiple_providers_keys_independent(client):
    """
    Test that multiple providers maintain independent API keys in .env file.
    """
    provider_data_1 = {
        "name": "TestOpenAI",
        "provider_type": "openai",
        "api_key": "sk-openai-key-111",
        "base_url": None,
        "organization_id": None,
        "rate_limit_requests": 60,
        "rate_limit_tokens": 100000,
        "timeout_seconds": 30,
        "retry_attempts": 3,
        "is_active": True
    }
    
    provider_data_2 = {
        "name": "TestAnthropic",
        "provider_type": "anthropic",
        "api_key": "sk-anthropic-key-222",
        "base_url": None,
        "organization_id": None,
        "rate_limit_requests": 60,
        "rate_limit_tokens": 100000,
        "timeout_seconds": 30,
        "retry_attempts": 3,
        "is_active": True
    }
    
    # Create first provider
    response1 = client.post("/api/ai-providers/", json=provider_data_1)
    assert response1.status_code == 201
    provider_id_1 = response1.json()["id"]
    
    # Create second provider
    response2 = client.post("/api/ai-providers/", json=provider_data_2)
    assert response2.status_code == 201
    provider_id_2 = response2.json()["id"]
    
    # Verify both keys are in .env file
    env_file = Path(".env")
    env_content = env_file.read_text()
    assert "PROVIDER_API_KEY_TESTOPENAI=" in env_content
    assert "PROVIDER_API_KEY_TESTANTHROPIC=" in env_content
    assert "sk-openai-key-111" in env_content
    assert "sk-anthropic-key-222" in env_content
    
    # Update first provider
    update_data_1 = {"api_key": "sk-openai-updated-333"}
    update_response_1 = client.put(f"/api/ai-providers/{provider_id_1}", json=update_data_1)
    assert update_response_1.status_code == 200
    
    # Verify both keys are still there and correct
    env_content = env_file.read_text()
    assert "PROVIDER_API_KEY_TESTOPENAI=" in env_content
    assert "PROVIDER_API_KEY_TESTANTHROPIC=" in env_content
    assert "sk-openai-updated-333" in env_content
    assert "sk-anthropic-key-222" in env_content
    
    # Clean up
    json_file_1 = Path("data/ai_providers") / f"{provider_id_1}.json"
    json_file_2 = Path("data/ai_providers") / f"{provider_id_2}.json"
    if json_file_1.exists():
        json_file_1.unlink()
    if json_file_2.exists():
        json_file_2.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
