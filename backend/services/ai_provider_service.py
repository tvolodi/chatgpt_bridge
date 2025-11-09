"""
AI Provider Service

This module provides the business logic for managing AI providers and
handling communication with external AI APIs.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from uuid import UUID

import aiohttp
from aiohttp import ClientTimeout

from ..models.ai_provider import (
    AIProvider, AIProviderCreate, AIProviderUpdate, AIModel, AIRequest, AIResponse,
    AIError, AIProviderSummary, AIUsageStats, AIProviderHealth, AIConversationRequest,
    AIConversationResponse, ProviderType
)


class AIProviderService:
    """
    Service for managing AI providers and handling API communication.

    Provides CRUD operations for AI providers, standardized API communication
    with different AI providers, usage tracking, and health monitoring.
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the AI provider service.

        Args:
            data_dir: Base directory for storing provider data
        """
        self.data_dir = Path(data_dir)
        self.providers_dir = self.data_dir / "ai_providers"
        self.providers_dir.mkdir(parents=True, exist_ok=True)

        # In-memory cache for providers and models
        self._providers_cache: Dict[UUID, AIProvider] = {}
        self._models_cache: Dict[str, AIModel] = {}
        self._usage_stats: Dict[UUID, AIUsageStats] = {}
        self._health_status: Dict[UUID, AIProviderHealth] = {}

        # HTTP client session
        self._session: Optional[aiohttp.ClientSession] = None

        # Load initial data
        self._load_providers()
        self._load_models()
        self._load_usage_stats()

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close_session()

    async def _ensure_session(self):
        """Ensure HTTP session is available."""
        if self._session is None or self._session.closed:
            timeout = ClientTimeout(total=30)
            self._session = aiohttp.ClientSession(timeout=timeout)

    async def _close_session(self):
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    def _get_provider_file(self, provider_id: UUID) -> Path:
        """Get the file path for a provider configuration."""
        return self.providers_dir / f"{provider_id}.json"

    def _load_providers(self):
        """Load all provider configurations from disk."""
        if self.providers_dir.exists():
            for provider_file in self.providers_dir.glob("*.json"):
                try:
                    with open(provider_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Convert string UUIDs and timestamps
                        data['id'] = UUID(data['id'])
                        data['created_at'] = datetime.fromisoformat(data['created_at'])
                        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
                        provider = AIProvider(**data)
                        self._providers_cache[provider.id] = provider
                except (json.JSONDecodeError, OSError, ValueError):
                    continue

    def _save_provider(self, provider: AIProvider):
        """Save a provider configuration to disk."""
        provider_file = self._get_provider_file(provider.id)
        data = provider.model_dump()
        # Convert UUID and datetime objects to serializable formats
        data['id'] = str(data['id'])
        data['created_at'] = data['created_at'].isoformat()
        data['updated_at'] = data['updated_at'].isoformat()

        with open(provider_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load_models(self):
        """Load available AI models for all providers."""
        # This would typically load from a configuration file or API
        # For now, we'll define some common models
        self._models_cache = {
            # OpenAI models
            "gpt-4": AIModel(
                id="gpt-4",
                name="GPT-4",
                provider_type=ProviderType.OPENAI,
                context_window=8192,
                max_tokens=4096,
                supports_functions=True,
                input_pricing=0.03,
                output_pricing=0.06
            ),
            "gpt-4-turbo": AIModel(
                id="gpt-4-turbo",
                name="GPT-4 Turbo",
                provider_type=ProviderType.OPENAI,
                context_window=128000,
                max_tokens=4096,
                supports_functions=True,
                input_pricing=0.01,
                output_pricing=0.03
            ),
            "gpt-3.5-turbo": AIModel(
                id="gpt-3.5-turbo",
                name="GPT-3.5 Turbo",
                provider_type=ProviderType.OPENAI,
                context_window=16385,
                max_tokens=4096,
                supports_functions=True,
                input_pricing=0.0015,
                output_pricing=0.002
            ),

            # Anthropic models
            "claude-3-opus": AIModel(
                id="claude-3-opus",
                name="Claude 3 Opus",
                provider_type=ProviderType.ANTHROPIC,
                context_window=200000,
                max_tokens=4096,
                supports_functions=False,
                input_pricing=0.015,
                output_pricing=0.075
            ),
            "claude-3-sonnet": AIModel(
                id="claude-3-sonnet",
                name="Claude 3 Sonnet",
                provider_type=ProviderType.ANTHROPIC,
                context_window=200000,
                max_tokens=4096,
                supports_functions=False,
                input_pricing=0.003,
                output_pricing=0.015
            ),
            "claude-3-haiku": AIModel(
                id="claude-3-haiku",
                name="Claude 3 Haiku",
                provider_type=ProviderType.ANTHROPIC,
                context_window=200000,
                max_tokens=4096,
                supports_functions=False,
                input_pricing=0.00025,
                output_pricing=0.00125
            ),
        }

    def _load_usage_stats(self):
        """Load usage statistics from disk."""
        # This would load from persistent storage
        # For now, initialize empty stats for each provider
        for provider in self._providers_cache.values():
            if provider.id not in self._usage_stats:
                self._usage_stats[provider.id] = AIUsageStats(provider_id=provider.id)

    def create_provider(self, provider_data: AIProviderCreate) -> AIProvider:
        """
        Create a new AI provider.

        Args:
            provider_data: Data for the new provider

        Returns:
            The created AI provider

        Raises:
            ValueError: If validation fails
        """
        provider = AIProvider(**provider_data.model_dump())
        self._providers_cache[provider.id] = provider
        self._usage_stats[provider.id] = AIUsageStats(provider_id=provider.id)
        self._health_status[provider.id] = AIProviderHealth(
            provider_id=provider.id,
            status="unknown",
            last_check=datetime.now()
        )
        self._save_provider(provider)
        return provider

    def get_provider(self, provider_id: UUID) -> Optional[AIProvider]:
        """
        Get an AI provider by ID.

        Args:
            provider_id: The provider ID to retrieve

        Returns:
            The AI provider if found, None otherwise
        """
        return self._providers_cache.get(provider_id)

    def list_providers(self, include_inactive: bool = False) -> List[AIProviderSummary]:
        """
        List all AI providers.

        Args:
            include_inactive: Whether to include inactive providers

        Returns:
            List of provider summaries
        """
        summaries = []
        for provider in self._providers_cache.values():
            if not include_inactive and not provider.is_active:
                continue

            models_count = len([m for m in self._models_cache.values()
                              if m.provider_type == provider.provider_type and m.is_active])

            summary = AIProviderSummary(
                id=provider.id,
                name=provider.name,
                provider_type=provider.provider_type,
                is_active=provider.is_active,
                models_count=models_count,
                created_at=provider.created_at
            )
            summaries.append(summary)

        # Sort by creation date, newest first
        summaries.sort(key=lambda s: s.created_at, reverse=True)
        return summaries

    def update_provider(self, provider_id: UUID, update_data: AIProviderUpdate) -> Optional[AIProvider]:
        """
        Update an existing AI provider.

        Args:
            provider_id: The provider ID to update
            update_data: The data to update

        Returns:
            The updated provider if found, None otherwise

        Raises:
            ValueError: If validation fails
        """
        provider = self._providers_cache.get(provider_id)
        if not provider:
            return None

        # Update fields if provided
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(provider, field, value)

        provider.updated_at = datetime.now()
        self._save_provider(provider)
        return provider

    def delete_provider(self, provider_id: UUID) -> bool:
        """
        Delete an AI provider.

        Args:
            provider_id: The provider ID to delete

        Returns:
            True if deleted, False if not found
        """
        provider = self._providers_cache.pop(provider_id, None)
        if provider:
            # Remove associated data
            self._usage_stats.pop(provider_id, None)
            self._health_status.pop(provider_id, None)

            # Remove from disk
            provider_file = self._get_provider_file(provider_id)
            if provider_file.exists():
                provider_file.unlink()

            return True
        return False

    def get_available_models(self, provider_type: Optional[ProviderType] = None) -> List[AIModel]:
        """
        Get available AI models.

        Args:
            provider_type: Optional filter by provider type

        Returns:
            List of available models
        """
        models = [m for m in self._models_cache.values() if m.is_active]
        if provider_type:
            models = [m for m in models if m.provider_type == provider_type]
        return models

    async def send_request(self, provider_id: UUID, request: AIRequest) -> Union[AIResponse, AIError]:
        """
        Send a request to an AI provider.

        Args:
            provider_id: The provider to use
            request: The AI request to send

        Returns:
            AI response or error

        Raises:
            ValueError: If provider not found or invalid
        """
        provider = self._providers_cache.get(provider_id)
        if not provider or not provider.is_active:
            raise ValueError(f"Provider {provider_id} not found or inactive")

        await self._ensure_session()

        # Check rate limits (simplified implementation)
        if not self._check_rate_limits(provider):
            return AIError(
                type="rate_limit_exceeded",
                message="Rate limit exceeded",
                retry_after=60
            )

        # Prepare the request based on provider type
        start_time = time.time()

        try:
            if provider.provider_type == ProviderType.OPENAI:
                response = await self._send_openai_request(provider, request)
            elif provider.provider_type == ProviderType.ANTHROPIC:
                response = await self._send_anthropic_request(provider, request)
            else:
                return AIError(
                    type="unsupported_provider",
                    message=f"Provider type {provider.provider_type} not supported"
                )

            # Update usage statistics
            self._update_usage_stats(provider_id, response, time.time() - start_time)

            # Update health status
            self._update_health_status(provider_id, True, time.time() - start_time)

            return response

        except Exception as e:
            response_time = time.time() - start_time
            error = AIError(
                type="request_failed",
                message=str(e),
                metadata={"response_time": response_time}
            )

            # Update health status
            self._update_health_status(provider_id, False, response_time, str(e))

            return error

    async def _send_openai_request(self, provider: AIProvider, request: AIRequest) -> AIResponse:
        """Send request to OpenAI API."""
        url = f"{provider.base_url or 'https://api.openai.com'}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": request.model,
            "messages": request.messages,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "frequency_penalty": request.frequency_penalty,
            "presence_penalty": request.presence_penalty,
            "stop": request.stop,
        }

        if request.functions:
            payload["functions"] = request.functions
            payload["function_call"] = request.function_call

        async with self._session.post(url, headers=headers, json=payload) as resp:
            if resp.status != 200:
                error_data = await resp.json()
                raise Exception(f"OpenAI API error: {error_data.get('error', {}).get('message', 'Unknown error')}")

            data = await resp.json()
            choice = data["choices"][0]

            return AIResponse(
                id=data["id"],
                model=data["model"],
                content=choice["message"]["content"],
                finish_reason=choice["finish_reason"],
                usage=data["usage"],
                metadata={"provider": "openai"}
            )

    async def _send_anthropic_request(self, provider: AIProvider, request: AIRequest) -> AIResponse:
        """Send request to Anthropic API."""
        url = f"{provider.base_url or 'https://api.anthropic.com'}/v1/messages"
        headers = {
            "x-api-key": provider.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

        # Convert OpenAI format to Anthropic format
        system_message = ""
        anthropic_messages = []

        for msg in request.messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                anthropic_messages.append(msg)

        payload = {
            "model": request.model,
            "max_tokens": request.max_tokens or 4096,
            "temperature": request.temperature,
            "system": system_message,
            "messages": anthropic_messages
        }

        async with self._session.post(url, headers=headers, json=payload) as resp:
            if resp.status != 200:
                error_data = await resp.json()
                raise Exception(f"Anthropic API error: {error_data.get('error', {}).get('message', 'Unknown error')}")

            data = await resp.json()

            return AIResponse(
                id=data["id"],
                model=data["model"],
                content=data["content"][0]["text"],
                finish_reason=data["stop_reason"],
                usage=data["usage"],
                metadata={"provider": "anthropic"}
            )

    def _check_rate_limits(self, provider: AIProvider) -> bool:
        """Check if provider is within rate limits (simplified implementation)."""
        # In a real implementation, this would track actual usage
        # For now, just return True
        return True

    def _update_usage_stats(self, provider_id: UUID, response: AIResponse, response_time: float):
        """Update usage statistics."""
        stats = self._usage_stats.get(provider_id)
        if stats:
            stats.total_requests += 1
            stats.total_tokens_input += response.usage.get("prompt_tokens", 0)
            stats.total_tokens_output += response.usage.get("completion_tokens", 0)

            # Calculate cost (simplified)
            model = self._models_cache.get(response.model)
            if model:
                input_cost = (stats.total_tokens_input / 1000) * model.input_pricing
                output_cost = (stats.total_tokens_output / 1000) * model.output_pricing
                stats.total_cost = input_cost + output_cost

            stats.average_response_time = (
                (stats.average_response_time * (stats.total_requests - 1)) + response_time
            ) / stats.total_requests
            stats.last_used = datetime.now()

    def _update_health_status(self, provider_id: UUID, success: bool, response_time: float,
                            error_message: Optional[str] = None):
        """Update provider health status."""
        health = self._health_status.get(provider_id)
        if health:
            health.last_check = datetime.now()
            health.response_time = response_time

            if success:
                health.status = "healthy"
                health.consecutive_failures = 0
                health.error_message = None
            else:
                health.consecutive_failures += 1
                health.error_message = error_message
                if health.consecutive_failures >= 3:
                    health.status = "unhealthy"
                elif health.consecutive_failures >= 1:
                    health.status = "degraded"

    def get_usage_stats(self, provider_id: Optional[UUID] = None) -> Union[AIUsageStats, List[AIUsageStats]]:
        """
        Get usage statistics.

        Args:
            provider_id: Optional specific provider ID

        Returns:
            Usage stats for the provider or all providers
        """
        if provider_id:
            return self._usage_stats.get(provider_id, AIUsageStats(provider_id=provider_id))
        else:
            return list(self._usage_stats.values())

    def get_health_status(self, provider_id: Optional[UUID] = None) -> Union[AIProviderHealth, List[AIProviderHealth]]:
        """
        Get health status.

        Args:
            provider_id: Optional specific provider ID

        Returns:
            Health status for the provider or all providers
        """
        if provider_id:
            return self._health_status.get(provider_id, AIProviderHealth(
                provider_id=provider_id,
                status="unknown",
                last_check=datetime.now()
            ))
        else:
            return list(self._health_status.values())

    async def check_provider_health(self, provider_id: UUID) -> AIProviderHealth:
        """
        Check the health of a specific provider.

        Args:
            provider_id: The provider ID to check

        Returns:
            Updated health status
        """
        provider = self._providers_cache.get(provider_id)
        if not provider:
            raise ValueError(f"Provider {provider_id} not found")

        # Simple health check - try a basic request
        start_time = time.time()
        try:
            # This would be a minimal test request
            # For now, just simulate a successful check
            success = True
            error_msg = None
            response_time = 0.1
        except Exception as e:
            success = False
            error_msg = str(e)
            response_time = time.time() - start_time

        self._update_health_status(provider_id, success, response_time, error_msg)
        return self._health_status[provider_id]