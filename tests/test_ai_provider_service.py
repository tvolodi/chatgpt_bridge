"""
Unit Tests for AI Provider Service

Comprehensive test suite for the AIProviderService class covering
all functionality, API communication, error handling, and edge cases.
"""

import json
import pytest
import asyncio
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4
from unittest.mock import Mock, AsyncMock, patch

from backend.models.ai_provider import (
    AIProvider, AIProviderCreate, AIProviderUpdate, AIModel, AIRequest, AIResponse,
    AIError, AIProviderSummary, AIUsageStats, AIProviderHealth, ProviderType
)
from backend.services.ai_provider_service import AIProviderService


class TestAIProviderService:
    """Test suite for AIProviderService."""

    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.service = AIProviderService(data_dir=str(self.temp_dir))

    def teardown_method(self):
        """Clean up test environment after each test."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_create_provider(self):
        """Test creating a new AI provider."""
        provider_data = AIProviderCreate(
            name="Test OpenAI",
            provider_type=ProviderType.OPENAI,
            api_key="test-key-123",
            base_url="https://api.openai.com",
            rate_limit_requests=100,
            timeout_seconds=60
        )

        provider = self.service.create_provider(provider_data)

        assert isinstance(provider, AIProvider)
        assert provider.name == "Test OpenAI"
        assert provider.provider_type == ProviderType.OPENAI
        assert provider.api_key == "test-key-123"
        assert provider.base_url == "https://api.openai.com"
        assert provider.rate_limit_requests == 100
        assert provider.timeout_seconds == 60
        assert provider.is_active is True
        assert isinstance(provider.id, UUID)
        assert isinstance(provider.created_at, datetime)
        assert isinstance(provider.updated_at, datetime)

        # Verify persistence
        loaded_provider = self.service.get_provider(provider.id)
        assert loaded_provider is not None
        assert loaded_provider.name == provider.name

    def test_get_provider(self):
        """Test retrieving an AI provider by ID."""
        # Create a provider first
        provider_data = AIProviderCreate(
            name="Test Provider",
            provider_type=ProviderType.OPENAI,
            api_key="test-key"
        )
        created_provider = self.service.create_provider(provider_data)

        # Retrieve the provider
        retrieved_provider = self.service.get_provider(created_provider.id)

        assert retrieved_provider is not None
        assert retrieved_provider.id == created_provider.id
        assert retrieved_provider.name == created_provider.name

        # Test retrieving non-existent provider
        non_existent_id = uuid4()
        assert self.service.get_provider(non_existent_id) is None

    def test_list_providers(self):
        """Test listing AI providers."""
        # Create providers
        provider1 = self.service.create_provider(AIProviderCreate(
            name="Provider 1",
            provider_type=ProviderType.OPENAI,
            api_key="key1"
        ))
        provider2 = self.service.create_provider(AIProviderCreate(
            name="Provider 2",
            provider_type=ProviderType.ANTHROPIC,
            api_key="key2"
        ))

        # Test list all active providers
        providers = self.service.list_providers()
        assert len(providers) == 2
        assert all(isinstance(p, AIProviderSummary) for p in providers)
        assert all(p.is_active for p in providers)

        # Test include inactive
        inactive_provider = self.service.create_provider(AIProviderCreate(
            name="Inactive Provider",
            provider_type=ProviderType.OPENAI,
            api_key="key3"
        ))
        self.service.update_provider(inactive_provider.id, AIProviderUpdate(is_active=False))

        all_providers = self.service.list_providers(include_inactive=True)
        assert len(all_providers) == 3

        active_only = self.service.list_providers(include_inactive=False)
        assert len(active_only) == 2

    def test_update_provider(self):
        """Test updating an existing AI provider."""
        # Create a provider
        provider_data = AIProviderCreate(
            name="Original Name",
            provider_type=ProviderType.OPENAI,
            api_key="original-key",
            timeout_seconds=30
        )
        provider = self.service.create_provider(provider_data)
        original_updated_at = provider.updated_at

        # Wait a bit to ensure timestamp difference
        import time
        time.sleep(0.01)

        # Update the provider
        update_data = AIProviderUpdate(
            name="Updated Name",
            api_key="updated-key",
            timeout_seconds=60,
            is_active=False
        )
        updated_provider = self.service.update_provider(provider.id, update_data)

        assert updated_provider is not None
        assert updated_provider.id == provider.id
        assert updated_provider.name == "Updated Name"
        assert updated_provider.api_key == "updated-key"
        assert updated_provider.timeout_seconds == 60
        assert updated_provider.is_active is False
        assert updated_provider.updated_at > original_updated_at

        # Test updating non-existent provider
        non_existent_update = self.service.update_provider(uuid4(), update_data)
        assert non_existent_update is None

    def test_delete_provider(self):
        """Test deleting an AI provider."""
        # Create a provider
        provider = self.service.create_provider(AIProviderCreate(
            name="Test Provider",
            provider_type=ProviderType.OPENAI,
            api_key="test-key"
        ))

        # Delete the provider
        deleted = self.service.delete_provider(provider.id)
        assert deleted is True

        # Verify it's gone
        assert self.service.get_provider(provider.id) is None

        # Test deleting non-existent provider
        assert self.service.delete_provider(uuid4()) is False

    def test_get_available_models(self):
        """Test getting available AI models."""
        # Get all models
        all_models = self.service.get_available_models()
        assert len(all_models) > 0
        assert all(isinstance(m, AIModel) for m in all_models)
        assert all(m.is_active for m in all_models)

        # Test filtering by provider type
        openai_models = self.service.get_available_models(ProviderType.OPENAI)
        assert len(openai_models) > 0
        assert all(m.provider_type == ProviderType.OPENAI for m in openai_models)

        anthropic_models = self.service.get_available_models(ProviderType.ANTHROPIC)
        assert len(anthropic_models) > 0
        assert all(m.provider_type == ProviderType.ANTHROPIC for m in anthropic_models)

        # Test filtering by non-existent provider type
        google_models = self.service.get_available_models(ProviderType.GOOGLE)
        assert len(google_models) == 0

    @pytest.mark.asyncio
    async def test_send_request_invalid_provider(self):
        """Test sending request to invalid provider."""
        request = AIRequest(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}]
        )

        async with self.service:
            with pytest.raises(ValueError, match="Provider.*not found or inactive"):
                await self.service.send_request(uuid4(), request)

    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.post')
    async def test_send_openai_request_success(self, mock_post):
        """Test successful OpenAI API request."""
        # Create a provider
        provider = self.service.create_provider(AIProviderCreate(
            name="Test OpenAI",
            provider_type=ProviderType.OPENAI,
            api_key="test-key"
        ))

        # Mock the HTTP response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "id": "chatcmpl-123",
            "model": "gpt-4",
            "choices": [{
                "message": {"content": "Hello, world!"},
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
        mock_post.return_value.__aenter__.return_value = mock_response

        request = AIRequest(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}]
        )

        async with self.service:
            response = await self.service.send_request(provider.id, request)

        assert isinstance(response, AIResponse)
        assert response.id == "chatcmpl-123"
        assert response.model == "gpt-4"
        assert response.content == "Hello, world!"
        assert response.finish_reason == "stop"
        assert response.usage["prompt_tokens"] == 10

        # Verify the request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "https://api.openai.com/v1/chat/completions" in call_args[0][0]
        request_data = call_args[1]["json"]
        assert request_data["model"] == "gpt-4"
        assert request_data["messages"] == [{"role": "user", "content": "Hello"}]

    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.post')
    async def test_send_openai_request_error(self, mock_post):
        """Test OpenAI API request with error response."""
        # Create a provider
        provider = self.service.create_provider(AIProviderCreate(
            name="Test OpenAI",
            provider_type=ProviderType.OPENAI,
            api_key="test-key"
        ))

        # Mock error response
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.json.return_value = {
            "error": {"message": "Invalid request"}
        }
        mock_post.return_value.__aenter__.return_value = mock_response

        request = AIRequest(
            model="invalid-model",
            messages=[{"role": "user", "content": "Hello"}]
        )

        async with self.service:
            response = await self.service.send_request(provider.id, request)

        assert isinstance(response, AIError)
        assert response.type == "request_failed"
        assert "Invalid request" in response.message

    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.post')
    async def test_send_anthropic_request_success(self, mock_post):
        """Test successful Anthropic API request."""
        # Create a provider
        provider = self.service.create_provider(AIProviderCreate(
            name="Test Anthropic",
            provider_type=ProviderType.ANTHROPIC,
            api_key="test-key"
        ))

        # Mock the HTTP response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "id": "msg_123",
            "model": "claude-3-sonnet",
            "content": [{"text": "Hello from Claude!"}],
            "stop_reason": "end_turn",
            "usage": {
                "input_tokens": 10,
                "output_tokens": 15
            }
        }
        mock_post.return_value.__aenter__.return_value = mock_response

        request = AIRequest(
            model="claude-3-sonnet",
            messages=[
                {"role": "system", "content": "You are helpful"},
                {"role": "user", "content": "Hello"}
            ]
        )

        async with self.service:
            response = await self.service.send_request(provider.id, request)

        assert isinstance(response, AIResponse)
        assert response.id == "msg_123"
        assert response.model == "claude-3-sonnet"
        assert response.content == "Hello from Claude!"
        assert response.finish_reason == "end_turn"

        # Verify the request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "https://api.anthropic.com/v1/messages" in call_args[0][0]
        request_data = call_args[1]["json"]
        assert request_data["model"] == "claude-3-sonnet"
        assert request_data["system"] == "You are helpful"
        assert request_data["messages"] == [{"role": "user", "content": "Hello"}]

    @pytest.mark.asyncio
    async def test_send_request_unsupported_provider(self):
        """Test sending request to unsupported provider type."""
        # Create a provider with unsupported type
        provider = self.service.create_provider(AIProviderCreate(
            name="Test Local",
            provider_type=ProviderType.LOCAL,
            api_key="test-key"
        ))

        request = AIRequest(
            model="local-model",
            messages=[{"role": "user", "content": "Hello"}]
        )

        async with self.service:
            response = await self.service.send_request(provider.id, request)

        assert isinstance(response, AIError)
        assert response.type == "unsupported_provider"
        assert "not supported" in response.message

    def test_usage_stats_tracking(self):
        """Test that usage statistics are properly tracked."""
        # Create a provider
        provider = self.service.create_provider(AIProviderCreate(
            name="Test Provider",
            provider_type=ProviderType.OPENAI,
            api_key="test-key"
        ))

        # Simulate usage update
        response = AIResponse(
            id="test-123",
            model="gpt-4",
            content="Test response",
            finish_reason="stop",
            usage={"prompt_tokens": 100, "completion_tokens": 50}
        )

        self.service._update_usage_stats(provider.id, response, 1.5)

        # Check usage stats
        stats = self.service.get_usage_stats(provider.id)
        assert stats.total_requests == 1
        assert stats.total_tokens_input == 100
        assert stats.total_tokens_output == 50
        assert stats.average_response_time == 1.5
        assert stats.last_used is not None

    def test_health_status_tracking(self):
        """Test that health status is properly tracked."""
        # Create a provider
        provider = self.service.create_provider(AIProviderCreate(
            name="Test Provider",
            provider_type=ProviderType.OPENAI,
            api_key="test-key"
        ))

        # Test successful request
        self.service._update_health_status(provider.id, True, 0.5)
        health = self.service.get_health_status(provider.id)
        assert health.status == "healthy"
        assert health.response_time == 0.5
        assert health.consecutive_failures == 0

        # Test failed request
        self.service._update_health_status(provider.id, False, 2.0, "Connection timeout")
        health = self.service.get_health_status(provider.id)
        assert health.status == "degraded"
        assert health.consecutive_failures == 1
        assert health.error_message == "Connection timeout"

        # Test multiple failures
        for _ in range(2):
            self.service._update_health_status(provider.id, False, 1.0, "Error")
        health = self.service.get_health_status(provider.id)
        assert health.status == "unhealthy"
        assert health.consecutive_failures == 3

    def test_get_usage_stats_all_providers(self):
        """Test getting usage stats for all providers."""
        # Create multiple providers
        provider1 = self.service.create_provider(AIProviderCreate(
            name="Provider 1",
            provider_type=ProviderType.OPENAI,
            api_key="key1"
        ))
        provider2 = self.service.create_provider(AIProviderCreate(
            name="Provider 2",
            provider_type=ProviderType.ANTHROPIC,
            api_key="key2"
        ))

        # Get all usage stats
        all_stats = self.service.get_usage_stats()
        assert len(all_stats) == 2
        assert all(isinstance(s, AIUsageStats) for s in all_stats)
        provider_ids = {s.provider_id for s in all_stats}
        assert provider_ids == {provider1.id, provider2.id}

    def test_get_health_status_all_providers(self):
        """Test getting health status for all providers."""
        # Create multiple providers
        provider1 = self.service.create_provider(AIProviderCreate(
            name="Provider 1",
            provider_type=ProviderType.OPENAI,
            api_key="key1"
        ))
        provider2 = self.service.create_provider(AIProviderCreate(
            name="Provider 2",
            provider_type=ProviderType.ANTHROPIC,
            api_key="key2"
        ))

        # Get all health status
        all_health = self.service.get_health_status()
        assert len(all_health) == 2
        assert all(isinstance(h, AIProviderHealth) for h in all_health)
        provider_ids = {h.provider_id for h in all_health}
        assert provider_ids == {provider1.id, provider2.id}

    def test_provider_validation(self):
        """Test provider creation validation."""
        # Test name validation
        with pytest.raises(ValueError):
            self.service.create_provider(AIProviderCreate(
                name="",  # Empty name should fail
                provider_type=ProviderType.OPENAI,
                api_key="key"
            ))

        # Test API key validation
        with pytest.raises(ValueError):
            self.service.create_provider(AIProviderCreate(
                name="Test",
                provider_type=ProviderType.OPENAI,
                api_key=""  # Empty API key should fail
            ))

        # Test rate limit validation
        with pytest.raises(ValueError):
            self.service.create_provider(AIProviderCreate(
                name="Test",
                provider_type=ProviderType.OPENAI,
                api_key="key",
                rate_limit_requests=0  # Zero should fail
            ))

        with pytest.raises(ValueError):
            self.service.create_provider(AIProviderCreate(
                name="Test",
                provider_type=ProviderType.OPENAI,
                api_key="key",
                timeout_seconds=0  # Zero should fail
            ))

    def test_provider_persistence(self):
        """Test that provider data persists across service restarts."""
        # Create a provider
        provider = self.service.create_provider(AIProviderCreate(
            name="Persistent Provider",
            provider_type=ProviderType.OPENAI,
            api_key="persistent-key",
            metadata={"custom": "data"}
        ))

        # Create a new service instance (simulating restart)
        new_service = AIProviderService(data_dir=str(self.temp_dir))

        # Verify provider persists
        loaded_provider = new_service.get_provider(provider.id)
        assert loaded_provider is not None
        assert loaded_provider.name == "Persistent Provider"
        assert loaded_provider.api_key == "persistent-key"
        assert loaded_provider.metadata == {"custom": "data"}

    def test_request_validation(self):
        """Test AI request validation."""
        # Create a provider
        provider = self.service.create_provider(AIProviderCreate(
            name="Test Provider",
            provider_type=ProviderType.OPENAI,
            api_key="key"
        ))

        # Test valid request
        request = AIRequest(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.5,
            max_tokens=100
        )
        assert request.model == "gpt-4"
        assert request.temperature == 0.5

        # Test default values
        simple_request = AIRequest(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}]
        )
        assert simple_request.temperature == 0.7  # default
        assert simple_request.max_tokens is None

    def test_model_cache_initialization(self):
        """Test that models are properly loaded on initialization."""
        # Check that models are loaded
        assert len(self.service._models_cache) > 0

        # Check specific models exist
        assert "gpt-4" in self.service._models_cache
        assert "claude-3-sonnet" in self.service._models_cache

        # Verify model properties
        gpt4 = self.service._models_cache["gpt-4"]
        assert gpt4.provider_type == ProviderType.OPENAI
        assert gpt4.context_window == 8192
        assert gpt4.is_active is True

    def test_provider_directory_structure(self):
        """Test that provider data is stored in proper directory structure."""
        provider = self.service.create_provider(AIProviderCreate(
            name="Test Provider",
            provider_type=ProviderType.OPENAI,
            api_key="test-key"
        ))

        # Check directory structure
        providers_dir = self.temp_dir / "ai_providers"
        assert providers_dir.exists()
        assert providers_dir.is_dir()

        # Check provider file
        provider_file = providers_dir / f"{provider.id}.json"
        assert provider_file.exists()

        # Verify file content
        with open(provider_file, 'r') as f:
            data = json.load(f)
            assert data['name'] == "Test Provider"
            assert data['provider_type'] == "openai"
            assert UUID(data['id']) == provider.id

    @pytest.mark.asyncio
    async def test_check_provider_health(self):
        """Test provider health checking."""
        # Create a provider
        provider = self.service.create_provider(AIProviderCreate(
            name="Test Provider",
            provider_type=ProviderType.OPENAI,
            api_key="test-key"
        ))

        # Mock the health check
        with patch.object(self.service, '_check_rate_limits', return_value=True):
            async with self.service:
                health = await self.service.check_provider_health(provider.id)

        assert isinstance(health, AIProviderHealth)
        assert health.provider_id == provider.id
        assert health.status in ["healthy", "unknown"]
        assert health.last_check is not None

    def test_rate_limit_check(self):
        """Test rate limit checking (simplified implementation)."""
        # Create a provider
        provider = self.service.create_provider(AIProviderCreate(
            name="Test Provider",
            provider_type=ProviderType.OPENAI,
            api_key="key"
        ))

        # Test rate limit check (currently always returns True)
        result = self.service._check_rate_limits(provider)
        assert result is True

    def test_concurrent_provider_operations(self):
        """Test that multiple provider operations work correctly."""
        # Create multiple providers
        providers = []
        for i in range(3):
            provider = self.service.create_provider(AIProviderCreate(
                name=f"Provider {i+1}",
                provider_type=ProviderType.OPENAI,
                api_key=f"key{i+1}"
            ))
            providers.append(provider)

        # Verify all providers exist
        all_providers = self.service.list_providers()
        assert len(all_providers) == 3

        # Verify each provider has usage stats
        all_stats = self.service.get_usage_stats()
        assert len(all_stats) == 3

        # Verify each provider has health status
        all_health = self.service.get_health_status()
        assert len(all_health) == 3

        # Test deleting one provider
        deleted = self.service.delete_provider(providers[0].id)
        assert deleted is True

        # Verify remaining providers
        remaining_providers = self.service.list_providers()
        assert len(remaining_providers) == 2