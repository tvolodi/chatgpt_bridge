"""
Conversation Service

This module provides the business logic for managing conversations between
users and AI providers within chat sessions.
"""

import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from uuid import UUID

from ..models.conversation import (
    ConversationMessage,
    ConversationContext,
    ConversationRequest,
    ConversationResponse,
    ConversationHistory,
    ConversationStats,
    ConversationSettings,
    ConversationError
)
from ..models.chat_session import Message, MessageCreate
from ..models.ai_provider import AIRequest, AIResponse, AIError
from ..services.chat_session_service import ChatSessionService
from ..services.ai_provider_service import AIProviderService


class ConversationService:
    """
    Service for managing conversations between users and AI providers.

    This service bridges chat sessions with AI providers to enable actual
    conversation flow, including message history, context management, and
    AI communication.
    """

    def __init__(self, data_dir: Path = Path("data")):
        """
        Initialize the conversation service.

        Args:
            data_dir: Directory for storing conversation data
        """
        self.data_dir = data_dir
        self.conversations_dir = data_dir / "conversations"
        self.conversations_dir.mkdir(parents=True, exist_ok=True)

        # Initialize dependent services
        self.chat_session_service = ChatSessionService(data_dir)
        self.ai_provider_service = AIProviderService(data_dir)

        # In-memory caches
        self._context_cache: Dict[UUID, ConversationContext] = {}
        self._settings = ConversationSettings()

        # Load existing conversation contexts
        self._load_conversation_contexts()

    def _get_conversation_file(self, session_id: UUID) -> Path:
        """Get the file path for a conversation's context."""
        return self.conversations_dir / f"{session_id}.json"

    def _load_conversation_contexts(self):
        """Load all conversation contexts from disk."""
        if self.conversations_dir.exists():
            for context_file in self.conversations_dir.glob("*.json"):
                try:
                    import json
                    with open(context_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Convert string UUIDs and timestamps
                        data['session_id'] = UUID(data['session_id'])
                        if data.get('last_message_at'):
                            data['last_message_at'] = datetime.fromisoformat(data['last_message_at'])
                        context = ConversationContext(**data)
                        self._context_cache[context.session_id] = context
                except (json.JSONDecodeError, OSError, ValueError):
                    continue

    def _save_conversation_context(self, context: ConversationContext):
        """Save a conversation context to disk."""
        context_file = self._get_conversation_file(context.session_id)
        data = context.model_dump()
        # Convert UUID and datetime objects to serializable formats
        data['session_id'] = str(data['session_id'])
        if data.get('last_message_at'):
            data['last_message_at'] = data['last_message_at'].isoformat()

        import json
        with open(context_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _get_or_create_context(self, session_id: UUID) -> ConversationContext:
        """Get existing context or create new one for a session."""
        if session_id not in self._context_cache:
            # Get message count from chat session service
            session = self.chat_session_service.get_session(session_id)
            if not session:
                raise ValueError(f"Chat session {session_id} not found")

            context = ConversationContext(
                session_id=session_id,
                message_count=session.message_count
            )
            self._context_cache[session_id] = context
            self._save_conversation_context(context)

        return self._context_cache[session_id]

    def _prepare_conversation_messages(
        self,
        session_id: UUID,
        user_message: str,
        include_history: bool = True,
        max_history_messages: Optional[int] = None,
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Prepare messages for AI request including history and system prompt.

        Args:
            session_id: Chat session ID
            user_message: The user's message
            include_history: Whether to include conversation history
            max_history_messages: Maximum number of history messages to include
            system_prompt: System prompt to use

        Returns:
            List of messages in AI API format
        """
        messages = []

        # Add system prompt if provided
        effective_system_prompt = system_prompt or self._settings.default_system_prompt
        if effective_system_prompt:
            messages.append({"role": "system", "content": effective_system_prompt})

        # Add conversation history if requested
        if include_history:
            history_messages = self.chat_session_service.get_session_messages(
                session_id,
                limit=max_history_messages or self._settings.max_history_messages
            )

            for msg in history_messages:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        # Add the current user message
        messages.append({"role": "user", "content": user_message})

        return messages

    def _select_provider_and_model(
        self,
        context: ConversationContext,
        requested_model: Optional[str] = None,
        requested_provider_id: Optional[UUID] = None
    ) -> tuple[UUID, str]:
        """
        Select the best AI provider and model for a conversation.

        Args:
            context: Conversation context
            requested_model: Specific model requested
            requested_provider_id: Specific provider requested

        Returns:
            Tuple of (provider_id, model)
        """
        # Use requested provider if specified
        if requested_provider_id:
            provider = self.ai_provider_service.get_provider(requested_provider_id)
            if not provider or not provider.is_active:
                raise ValueError(f"Requested provider {requested_provider_id} not found or inactive")
            provider_id = requested_provider_id
        else:
            # Use preferred provider from context or default
            provider_id = context.preferred_provider_id or self._settings.default_provider_id
            if not provider_id:
                # Find the first active provider
                providers = self.ai_provider_service.list_providers(include_inactive=False)
                if not providers:
                    raise ValueError("No active AI providers available")
                provider_id = providers[0].id

        # Determine model to use
        if requested_model:
            model = requested_model
        elif context.preferred_model:
            model = context.preferred_model
        else:
            model = self._settings.default_model or "gpt-3.5-turbo"  # fallback

        return provider_id, model

    async def send_message(self, request: ConversationRequest) -> Union[ConversationResponse, ConversationError]:
        """
        Send a message in a conversation and get AI response.

        Args:
            request: Conversation request with message and settings

        Returns:
            Conversation response or error
        """
        try:
            # Validate session exists
            session = self.chat_session_service.get_session(request.session_id)
            if not session:
                return ConversationError(
                    type="session_not_found",
                    message=f"Chat session {request.session_id} not found",
                    session_id=request.session_id
                )

            # Get or create conversation context
            context = self._get_or_create_context(request.session_id)

            # Select provider and model
            provider_id, model = self._select_provider_and_model(
                context,
                request.model,
                request.provider_id
            )

            # Prepare messages for AI request
            messages = self._prepare_conversation_messages(
                request.session_id,
                request.message,
                request.include_history,
                request.max_history_messages,
                request.system_prompt
            )

            # Create AI request
            ai_request = AIRequest(
                model=model,
                messages=messages,
                max_tokens=request.max_tokens or self._settings.default_max_tokens,
                temperature=request.temperature or self._settings.default_temperature
            )

            # Send request to AI provider
            start_time = time.time()
            ai_response = await self.ai_provider_service.send_request(provider_id, ai_request)

            if isinstance(ai_response, AIError):
                # Update context with error
                context.last_message_at = datetime.now()
                self._save_conversation_context(context)

                return ConversationError(
                    type=ai_response.type,
                    message=ai_response.message,
                    session_id=request.session_id,
                    provider_id=provider_id,
                    retry_after=ai_response.retry_after,
                    metadata=ai_response.metadata
                )

            # Create user message in chat session
            user_message_data = MessageCreate(
                role="user",
                content=request.message,
                metadata={"conversation": True}
            )
            user_message = self.chat_session_service.add_message(request.session_id, user_message_data)

            # Create AI response message in chat session
            ai_message_data = MessageCreate(
                role="assistant",
                content=ai_response.content,
                metadata={
                    "conversation": True,
                    "model": ai_response.model,
                    "provider_id": str(provider_id),
                    "usage": ai_response.usage,
                    "finish_reason": ai_response.finish_reason
                }
            )
            ai_message = self.chat_session_service.add_message(request.session_id, ai_message_data)

            # Update conversation context
            response_time = time.time() - start_time
            context.message_count += 2  # user + assistant
            context.last_message_at = datetime.now()
            context.total_tokens_input += ai_response.usage.get("prompt_tokens", 0)
            context.total_tokens_output += ai_response.usage.get("completion_tokens", 0)

            # Calculate cost (simplified)
            if self._settings.enable_cost_tracking:
                model_info = None
                for m in self.ai_provider_service.get_available_models():
                    if m.id == ai_response.model:
                        model_info = m
                        break

                if model_info:
                    input_cost = (ai_response.usage.get("prompt_tokens", 0) / 1000) * model_info.input_pricing
                    output_cost = (ai_response.usage.get("completion_tokens", 0) / 1000) * model_info.output_pricing
                    context.total_cost += input_cost + output_cost

            self._save_conversation_context(context)

            # Create conversation response
            conversation_response = ConversationResponse(
                session_id=request.session_id,
                user_message_id=user_message.id,
                ai_message_id=ai_message.id,
                content=ai_response.content,
                model=ai_response.model,
                provider_id=provider_id,
                usage=ai_response.usage,
                finish_reason=ai_response.finish_reason,
                created_at=ai_response.created_at,
                conversation_context=context
            )

            return conversation_response

        except Exception as e:
            return ConversationError(
                type="internal_error",
                message=f"Internal error: {str(e)}",
                session_id=request.session_id
            )

    def get_conversation_history(
        self,
        session_id: UUID,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> ConversationHistory:
        """
        Get the conversation history for a session.

        Args:
            session_id: Chat session ID
            limit: Maximum number of messages to return
            offset: Number of messages to skip

        Returns:
            Conversation history
        """
        # Get conversation context
        context = self._get_or_create_context(session_id)

        # Get messages from chat session service
        messages = self.chat_session_service.get_session_messages(
            session_id,
            limit=limit,
            offset=offset
        )

        # Convert to conversation messages
        conversation_messages = []
        for msg in messages:
            conv_msg = ConversationMessage(
                id=msg.id,
                session_id=session_id,
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp,
                metadata=msg.metadata
            )

            # Extract AI-specific metadata
            if msg.role == "assistant" and msg.metadata:
                conv_msg.model = msg.metadata.get("model")
                if msg.metadata.get("provider_id"):
                    conv_msg.provider_id = UUID(msg.metadata["provider_id"])
                conv_msg.usage = msg.metadata.get("usage")
                conv_msg.finish_reason = msg.metadata.get("finish_reason")

            conversation_messages.append(conv_msg)

        # Check if there are more messages
        total_messages = self.chat_session_service.get_session(session_id).message_count
        has_more = (offset or 0) + len(messages) < total_messages

        return ConversationHistory(
            session_id=session_id,
            context=context,
            messages=conversation_messages,
            total_messages=total_messages,
            has_more=has_more
        )

    def update_conversation_settings(self, settings: ConversationSettings):
        """
        Update conversation settings.

        Args:
            settings: New conversation settings
        """
        self._settings = settings

    def get_conversation_settings(self) -> ConversationSettings:
        """
        Get current conversation settings.

        Returns:
            Current conversation settings
        """
        return self._settings

    def get_conversation_stats(self) -> ConversationStats:
        """
        Get statistics for all conversations.

        Returns:
            Conversation statistics
        """
        total_conversations = len(self._context_cache)
        active_conversations = sum(1 for ctx in self._context_cache.values()
                                 if ctx.last_message_at and
                                 (datetime.now() - ctx.last_message_at).days < 30)  # Active in last 30 days

        total_messages = sum(ctx.message_count for ctx in self._context_cache.values())
        total_tokens_input = sum(ctx.total_tokens_input for ctx in self._context_cache.values())
        total_tokens_output = sum(ctx.total_tokens_output for ctx in self._context_cache.values())
        total_cost = sum(ctx.total_cost for ctx in self._context_cache.values())

        # Calculate average response time (simplified - would need to track individual response times)
        average_response_time = 2.0  # placeholder

        conversations_by_provider = {}
        messages_by_model = {}

        for ctx in self._context_cache.values():
            if ctx.preferred_provider_id:
                provider_key = str(ctx.preferred_provider_id)
                conversations_by_provider[provider_key] = conversations_by_provider.get(provider_key, 0) + 1

            if ctx.preferred_model:
                messages_by_model[ctx.preferred_model] = messages_by_model.get(ctx.preferred_model, 0) + ctx.message_count

        return ConversationStats(
            total_conversations=total_conversations,
            active_conversations=active_conversations,
            total_messages=total_messages,
            total_tokens_input=total_tokens_input,
            total_tokens_output=total_tokens_output,
            total_cost=total_cost,
            average_response_time=average_response_time,
            conversations_by_provider=conversations_by_provider,
            messages_by_model=messages_by_model
        )

    def clear_conversation_context(self, session_id: UUID) -> bool:
        """
        Clear the conversation context for a session.

        Args:
            session_id: Chat session ID

        Returns:
            True if cleared, False if not found
        """
        if session_id in self._context_cache:
            del self._context_cache[session_id]

            # Remove from disk
            context_file = self._get_conversation_file(session_id)
            if context_file.exists():
                context_file.unlink()

            return True
        return False