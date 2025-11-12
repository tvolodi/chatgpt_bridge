"""
Test to verify that API keys are correctly stripped of quotes when loaded from .env
"""
import pytest
from pathlib import Path
from dotenv import dotenv_values, set_key
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.ai_provider_service import AIProviderService


@pytest.fixture
def client():
    """Create a test client for the API."""
    return TestClient(app)


def test_api_key_quotes_stripped_on_load(client):
    """
    Test that API keys have quotes stripped when loaded from .env file.
    This verifies the fix for the issue where keys were loaded WITH quotes.
    """
    # Create a new provider
    provider_data = {
        "name": "QuoteTestProvider",
        "provider_type": "openai",
        "api_key": "sk-quote-test-12345",
        "is_active": True
    }
    
    # Create provider
    response = client.post("/api/ai-providers/", json=provider_data)
    assert response.status_code == 201
    created_provider = response.json()
    provider_id = created_provider["id"]
    
    # Verify the key is returned without quotes
    assert created_provider["api_key"] == "sk-quote-test-12345", \
        "Created provider key should not have quotes"
    
    # Check what's actually in the .env file
    env_file = Path(".env")
    env_content = env_file.read_text()
    assert "PROVIDER_API_KEY_QUOTETESTPROVIDER=" in env_content
    
    # Extract the line
    for line in env_content.split('\n'):
        if 'PROVIDER_API_KEY_QUOTETESTPROVIDER=' in line:
            print(f"Raw .env line: {repr(line)}")
            # Should contain quotes (set_key adds them)
            assert "'" in line or '"' in line, "set_key() should add quotes in .env file"
    
    # Now verify loading the provider gets the key WITHOUT quotes
    get_response = client.get(f"/api/ai-providers/{provider_id}")
    assert get_response.status_code == 200
    retrieved_provider = get_response.json()
    
    # The key should NOT have quotes
    assert retrieved_provider["api_key"] == "sk-quote-test-12345", \
        "Retrieved provider key should have quotes stripped"
    assert not retrieved_provider["api_key"].startswith("'"), \
        "Retrieved key should not start with quote"
    assert not retrieved_provider["api_key"].endswith("'"), \
        "Retrieved key should not end with quote"
    assert not retrieved_provider["api_key"].startswith('"'), \
        "Retrieved key should not start with double quote"
    assert not retrieved_provider["api_key"].endswith('"'), \
        "Retrieved key should not end with double quote"
    
    # Clean up
    json_file = Path("data/ai_providers") / f"{provider_id}.json"
    if json_file.exists():
        json_file.unlink()


def test_page_refresh_preserves_key(client):
    """
    Test that after creating a provider and refreshing the page,
    the key is still loaded correctly (addresses the original issue).
    This simulates a page refresh by getting the provider again via API.
    """
    # Create a new provider
    provider_data = {
        "name": "RefreshTestProvider",
        "provider_type": "openai",
        "api_key": "sk-refresh-test-key-999",
        "is_active": True
    }
    
    # Create provider
    response = client.post("/api/ai-providers/", json=provider_data)
    assert response.status_code == 201
    created_provider = response.json()
    provider_id = created_provider["id"]
    original_key = created_provider["api_key"]
    
    # Verify key is correct
    assert original_key == "sk-refresh-test-key-999"
    
    # Simulate page refresh by fetching the provider again via API
    # This tests that the key is correctly persisted and reloaded
    refresh_response = client.get(f"/api/ai-providers/{provider_id}")
    assert refresh_response.status_code == 200
    
    refreshed_provider = refresh_response.json()
    # Verify the key is still correct (not lost, not with quotes)
    assert refreshed_provider["api_key"] == "sk-refresh-test-key-999", \
        "Key should persist after page refresh"
    assert refreshed_provider["api_key"] == original_key, \
        "Key should not change after refresh"
    
    # Clean up
    json_file = Path("data/ai_providers") / f"{provider_id}.json"
    if json_file.exists():
        json_file.unlink()


def test_key_survives_update_cycle(client):
    """
    Test that a key survives the complete update cycle:
    1. Create provider with key A
    2. Update to key B
    3. Page refresh via API
    4. Verify key is still B (not lost, not with quotes)
    """
    # Create provider with initial key
    provider_data = {
        "name": "UpdateCycleTestProvider",
        "provider_type": "openai",
        "api_key": "sk-initial-key-111",
        "is_active": True
    }
    
    response = client.post("/api/ai-providers/", json=provider_data)
    assert response.status_code == 201
    provider_id = response.json()["id"]
    
    # Verify initial key
    get_response = client.get(f"/api/ai-providers/{provider_id}")
    assert get_response.json()["api_key"] == "sk-initial-key-111"
    
    # Update the key
    update_response = client.put(
        f"/api/ai-providers/{provider_id}",
        json={"api_key": "sk-updated-key-222"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["api_key"] == "sk-updated-key-222"
    
    # Simulate page refresh by fetching via API again
    refresh_response = client.get(f"/api/ai-providers/{provider_id}")
    refreshed_provider = refresh_response.json()
    
    # Verify key is correct after refresh
    assert refreshed_provider["api_key"] == "sk-updated-key-222", \
        "Updated key should persist after page refresh"
    
    # Do another update
    update_response2 = client.put(
        f"/api/ai-providers/{provider_id}",
        json={"api_key": "sk-third-key-333"}
    )
    assert update_response2.status_code == 200
    
    # Another refresh
    refresh_response2 = client.get(f"/api/ai-providers/{provider_id}")
    final_provider = refresh_response2.json()
    assert final_provider["api_key"] == "sk-third-key-333", \
        "Third key should persist after second refresh"
    
    # Clean up
    json_file = Path("data/ai_providers") / f"{provider_id}.json"
    if json_file.exists():
        json_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
