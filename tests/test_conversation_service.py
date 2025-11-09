"""
Unit Tests for Conversation Service

Comprehensive test suite for the conversation service functionality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
from uuid import UUID, uuid4
from datetime import datetime

from backend.models.conversation import (
    ConversationMessage,
    ConversationContext,
    ConversationRequest,
    ConversationResponse,
    ConversationHistory,
    ConversationStats,
    ConversationSettings,
    ConversationError
)
from backend.models.chat_session import ChatSession, Message
from backend.models.ai_provider import AIProvider, AIResponse, AIError, ProviderType
from backend.services.conversation_service import ConversationService


class TestConversationService:
    """Test suite for ConversationService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = Path("test_data")
        self.service = ConversationService(self.test_dir)

        # Mock dependent services
        self.service.chat_session_service = MagicMock()
        self.service.ai_provider_service = MagicMock()

        # Clear caches
        self.service._context_cache.clear()

    def teardown_method(self):
        """Clean up test fixtures."""
        # Clean up test directory
        if self.test_dir.exists():
            for file in self.test_dir.rglob("*.json"):
                file.unlink()
            for dir_path in reversed(list(self.test_dir.rglob("*"))):
                if dir_path.is_dir():
                    dir_path.rmdir()
            self.test_dir.rmdir()

    def test_initialization(self):
        """Test service initialization."""
        assert self.service.data_dir == self.test_dir
        assert self.service.conversations_dir == self.test_dir / "conversations"
        assert self.service.conversations_dir.exists()
        assert isinstance(self.service._settings, ConversationSettings)

    def test_get_or_create_context_new(self):
        """Test getting context for new session."""
        session_id = uuid4()

        # Mock chat session service
        mock_session = MagicMock()
        mock_session.message_count = 5
        self.service.chat_session_service.get_session.return_value = mock_session

        context = self.service._get_or_create_context(session_id)

        assert context.session_id == session_id
        assert context.message_count == 5
        assert session_id in self.service._context_cache

    def test_get_or_create_context_existing(self):
        """Test getting existing context."""
        session_id = uuid4()
        existing_context = ConversationContext(session_id=session_id, message_count=10)
        self.service._context_cache[session_id] = existing_context

        context = self.service._get_or_create_context(session_id)

        assert context == existing_context
        # Should not call chat session service for existing context
        self.service.chat_session_service.get_session.assert_not_called()

    def test_get_or_create_context_session_not_found(self):
        """Test getting context for non-existent session."""
        session_id = uuid4()
        self.service.chat_session_service.get_session.return_value = None

        with pytest.raises(ValueError, match=f"Chat session {session_id} not found"):
            self.service._get_or_create_context(session_id)

    def test_prepare_conversation_messages_with_history(self):
        """Test preparing messages with conversation history."""
        session_id = uuid4()

        # Mock history messages
        history_messages = [
            MagicMock(role="user", content="Hello"),
            MagicMock(role="assistant", content="Hi there!")
        ]
        self.service.chat_session_service.get_session_messages.return_value = history_messages

        messages = self.service._prepare_conversation_messages(
            session_id, "How are you?", include_history=True
        )

        assert len(messages) == 3  # history + user (no system prompt by default)
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello"
        assert messages[1]["role"] == "assistant"
        assert messages[1]["content"] == "Hi there!"
        assert messages[2]["role"] == "user"
        assert messages[2]["content"] == "How are you?"

    def test_prepare_conversation_messages_no_history(self):
        """Test preparing messages without history."""
        session_id = uuid4()

        messages = self.service._prepare_conversation_messages(
            session_id, "Hello", include_history=False
        )

        assert len(messages) == 1  # just user (no system prompt by default)
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello"

    def test_prepare_conversation_messages_with_system_prompt(self):
        """Test preparing messages with custom system prompt."""
        session_id = uuid4()
        system_prompt = "You are a helpful assistant."

        messages = self.service._prepare_conversation_messages(
            session_id, "Hello", system_prompt=system_prompt
        )

        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == system_prompt

    def test_select_provider_and_model_requested(self):
        """Test selecting requested provider and model."""
        context = ConversationContext(session_id=uuid4())
        requested_provider_id = uuid4()
        requested_model = "gpt-4"

        # Mock provider
        mock_provider = MagicMock()
        mock_provider.is_active = True
        self.service.ai_provider_service.get_provider.return_value = mock_provider

        provider_id, model = self.service._select_provider_and_model(
            context, requested_model, requested_provider_id
        )

        assert provider_id == requested_provider_id
        assert model == requested_model

    def test_select_provider_and_model_from_context(self):
        """Test selecting provider and model from context."""
        context = ConversationContext(
            session_id=uuid4(),
            preferred_provider_id=uuid4(),
            preferred_model="claude-3-sonnet"
        )

        provider_id, model = self.service._select_provider_and_model(context)

        assert provider_id == context.preferred_provider_id
        assert model == context.preferred_model

    def test_select_provider_and_model_defaults(self):
        """Test selecting default provider and model."""
        context = ConversationContext(session_id=uuid4())

        # Mock providers list
        mock_provider = MagicMock()
        mock_provider.id = uuid4()
        self.service.ai_provider_service.list_providers.return_value = [mock_provider]

        provider_id, model = self.service._select_provider_and_model(context)

        assert provider_id == mock_provider.id
        assert model == "gpt-3.5-turbo"  # default fallback

    def test_select_provider_and_model_no_providers(self):
        """Test selecting provider when no providers available."""
        context = ConversationContext(session_id=uuid4())
        self.service.ai_provider_service.list_providers.return_value = []

        with pytest.raises(ValueError, match="No active AI providers available"):
            self.service._select_provider_and_model(context)

    @pytest.mark.asyncio
    async def test_send_message_success(self):
        """Test successful message sending."""
        session_id = uuid4()
        provider_id = uuid4()

        # Mock session
        mock_session = MagicMock()
        mock_session.message_count = 0
        self.service.chat_session_service.get_session.return_value = mock_session

        # Mock context
        context = ConversationContext(session_id=session_id)
        self.service._context_cache[session_id] = context

        # Mock AI response
        ai_response = AIResponse(
            id="test-response",
            model="gpt-4",
            content="Hello! How can I help you?",
            finish_reason="stop",
            usage={"prompt_tokens": 10, "completion_tokens": 20}
        )
        self.service.ai_provider_service.send_request = AsyncMock(return_value=ai_response)

        # Mock message creation
        user_message = MagicMock()
        user_message.id = uuid4()
        ai_message = MagicMock()
        ai_message.id = uuid4()
        self.service.chat_session_service.add_message.side_effect = [user_message, ai_message]

        # Mock model info for cost calculation
        mock_model = MagicMock()
        mock_model.input_pricing = 0.01
        mock_model.output_pricing = 0.03
        self.service.ai_provider_service.get_available_models.return_value = [mock_model]

        request = ConversationRequest(session_id=session_id, message="Hello")

        with patch.object(self.service, '_select_provider_and_model', return_value=(provider_id, "gpt-4")):
            result = await self.service.send_message(request)

        assert isinstance(result, ConversationResponse)
        assert result.session_id == session_id
        assert result.content == ai_response.content
        assert result.model == "gpt-4"
        assert result.provider_id == provider_id

        # Verify context was updated
        assert context.message_count == 2
        assert context.total_tokens_input == 10
        assert context.total_tokens_output == 20

    @pytest.mark.asyncio
    async def test_send_message_session_not_found(self):
        """Test sending message to non-existent session."""
        session_id = uuid4()
        self.service.chat_session_service.get_session.return_value = None

        request = ConversationRequest(session_id=session_id, message="Hello")

        result = await self.service.send_message(request)

        assert isinstance(result, ConversationError)
        assert result.type == "session_not_found"
        assert result.session_id == session_id

    @pytest.mark.asyncio
    async def test_send_message_ai_error(self):
        """Test handling AI provider error."""
        session_id = uuid4()

        # Mock session
        mock_session = MagicMock()
        self.service.chat_session_service.get_session.return_value = mock_session

        # Mock AI error
        ai_error = AIError(
            type="rate_limit_exceeded",
            message="Rate limit exceeded",
            retry_after=60
        )
        self.service.ai_provider_service.send_request = AsyncMock(return_value=ai_error)

        request = ConversationRequest(session_id=session_id, message="Hello")

        with patch.object(self.service, '_select_provider_and_model', return_value=(uuid4(), "gpt-4")):
            result = await self.service.send_message(request)

        assert isinstance(result, ConversationError)
        assert result.type == "rate_limit_exceeded"
        assert result.retry_after == 60

    def test_get_conversation_history(self):
        """Test getting conversation history."""
        session_id = uuid4()

        # Mock context
        context = ConversationContext(session_id=session_id, message_count=5)
        self.service._context_cache[session_id] = context

        # Mock messages - return all 5 messages since no limit
        mock_messages = [
            MagicMock(id=uuid4(), role="user", content="Hello", timestamp=datetime.now(), metadata={}),
            MagicMock(id=uuid4(), role="assistant", content="Hi!", timestamp=datetime.now(),
                     metadata={"model": "gpt-4", "provider_id": str(uuid4()), "usage": {"tokens": 10}}),
            MagicMock(id=uuid4(), role="user", content="How are you?", timestamp=datetime.now(), metadata={}),
            MagicMock(id=uuid4(), role="assistant", content="I'm fine!", timestamp=datetime.now(),
                     metadata={"model": "gpt-4", "provider_id": str(uuid4()), "usage": {"tokens": 15}}),
            MagicMock(id=uuid4(), role="user", content="Good!", timestamp=datetime.now(), metadata={})
        ]
        self.service.chat_session_service.get_session_messages.return_value = mock_messages

        # Mock session for total count
        mock_session = MagicMock()
        mock_session.message_count = 5
        self.service.chat_session_service.get_session.return_value = mock_session

        history = self.service.get_conversation_history(session_id)

        assert isinstance(history, ConversationHistory)
        assert history.session_id == session_id
        assert history.context == context
        assert len(history.messages) == 5
        assert history.total_messages == 5
        assert not history.has_more

    def test_get_conversation_stats(self):
        """Test getting conversation statistics."""
        # Create mock contexts
        context1 = ConversationContext(
            session_id=uuid4(),
            message_count=10,
            total_tokens_input=100,
            total_tokens_output=200,
            total_cost=1.5,
            preferred_provider_id=uuid4(),
            preferred_model="gpt-4",
            last_message_at=datetime.now()
        )
        context2 = ConversationContext(
            session_id=uuid4(),
            message_count=5,
            total_tokens_input=50,
            total_tokens_output=100,
            total_cost=0.75,
            last_message_at=datetime.now()
        )

        self.service._context_cache = {
            context1.session_id: context1,
            context2.session_id: context2
        }

        stats = self.service.get_conversation_stats()

        assert isinstance(stats, ConversationStats)
        assert stats.total_conversations == 2
        assert stats.total_messages == 15
        assert stats.total_tokens_input == 150
        assert stats.total_tokens_output == 300
        assert stats.total_cost == 2.25

    def test_update_conversation_settings(self):
        """Test updating conversation settings."""
        new_settings = ConversationSettings(
            default_model="claude-3-sonnet",
            default_max_tokens=2000,
            enable_cost_tracking=False
        )

        self.service.update_conversation_settings(new_settings)

        current_settings = self.service.get_conversation_settings()
        assert current_settings.default_model == "claude-3-sonnet"
        assert current_settings.default_max_tokens == 2000
        assert not current_settings.enable_cost_tracking

    def test_clear_conversation_context(self):
        """Test clearing conversation context."""
        session_id = uuid4()
        context = ConversationContext(session_id=session_id)
        self.service._context_cache[session_id] = context

        # Create context file
        context_file = self.service._get_conversation_file(session_id)
        context_file.parent.mkdir(parents=True, exist_ok=True)
        context_file.write_text('{"test": "data"}')

        result = self.service.clear_conversation_context(session_id)

        assert result is True
        assert session_id not in self.service._context_cache
        assert not context_file.exists()

    def test_clear_conversation_context_not_found(self):
        """Test clearing non-existent conversation context."""
        session_id = uuid4()

        result = self.service.clear_conversation_context(session_id)

        assert result is False