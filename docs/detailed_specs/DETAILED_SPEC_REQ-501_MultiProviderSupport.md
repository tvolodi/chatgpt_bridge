# REQ-501: Multi-Provider AI Support

**Registry Entry:** See `docs/01_requirements_registry.md` (Line 108)  
**Functionality Reference:** `specifications/functionality.md` Section 5  
**Document Version:** 1.0  
**Last Updated:** November 15, 2025  
**Status:** implemented  

---

## 1. Overview

### 1.1 Brief Description
Support multiple AI providers (OpenAI, Anthropic, local Ollama, etc.) with seamless switching during conversations, provider health checks, model selection, and provider-specific configuration management.

### 1.2 Business Value
- **No Vendor Lock-in:** Switch providers without losing data
- **Cost Optimization:** Use cheapest provider for task
- **Resilience:** Fall back to different provider if one fails
- **Feature Access:** Different providers have different capabilities

---

## 2. Functional Requirements

### 2.1 Core Requirements

#### REQ-501-A: Multiple Provider Support
- **Description:** System supports OpenAI, Anthropic, Ollama, Cohere
- **Configuration:** Each provider needs API key (stored in .env)
- **Metadata:** Provider ID, name, description, model list, status
- **Storage:** `backend/config/providers_config.json` (metadata only, keys in .env)
- **Acceptance Criteria:**
  - ✓ At least 3 providers supported
  - ✓ New providers can be added via config
  - ✓ Each provider can be enabled/disabled

#### REQ-501-B: Provider Selector in Header
- **Description:** Dropdown in header to view/select providers
- **Display:** Current provider name + icon
- **List:** Shows all available providers with:
  - Name and description
  - Model count
  - Configuration status (✓ or ✗)
  - Health status (online/offline)
- **Selection:** Only configured providers selectable
- **Persistence:** Selection saved to localStorage
- **Acceptance Criteria:**
  - ✓ Dropdown shows all providers
  - ✓ Can switch with one click
  - ✓ Status clearly indicated
  - ✓ Selection persists across sessions

#### REQ-501-C: Provider Health Checks
- **Description:** Periodic checks that provider APIs are working
- **Implementation:**
  - Check each provider at startup
  - Check on button test in settings
  - Cache results for 5 minutes
  - Show status in UI (green = working, red = down, yellow = slow)
- **API Endpoint:** GET `/api/ai-providers/{id}/health`
- **Response:** `{ status: "healthy"|"unhealthy", responseTime: ms, message: string }`
- **Fallback:** If selected provider unhealthy, fall back to first healthy provider
- **Acceptance Criteria:**
  - ✓ Health checks performed
  - ✓ Status displayed in UI
  - ✓ Fallback works automatically
  - ✓ Timeout handled gracefully

#### REQ-501-D: Provider-Specific Configuration
- **Description:** Each provider has unique configuration
- **OpenAI:** model (gpt-4, gpt-3.5), temperature, max_tokens
- **Anthropic:** model (claude-3), temperature, max_tokens
- **Ollama:** host URL, model, temperature
- **Storage:** In .env file for keys, in-memory for config
- **Example .env:**
  ```
  OPENAI_API_KEY=sk-...
  ANTHROPIC_API_KEY=claude-...
  OLLAMA_BASE_URL=http://localhost:11434
  ```
- **Acceptance Criteria:**
  - ✓ Config loaded at startup
  - ✓ Each provider has own settings
  - ✓ Hot-reload on settings update
  - ✓ Validation prevents invalid configs

#### REQ-501-E: Model Selection per Provider
- **Description:** Each provider has multiple models; user can select
- **OpenAI:** gpt-4, gpt-4-turbo, gpt-3.5-turbo
- **Anthropic:** claude-3-opus, claude-3-sonnet, claude-3-haiku
- **Ollama:** Any local model available
- **Storage:** Selected model stored in project settings
- **API:** GET `/api/ai-providers/{provider_id}/models`
- **Acceptance Criteria:**
  - ✓ Models list retrieved from provider
  - ✓ Model selection persists
  - ✓ Invalid models rejected

#### REQ-501-F: Provider Switching Mid-Conversation
- **Description:** Switch providers without losing message history
- **Implementation:**
  - All messages stored with provider_id
  - Can see which provider responded to which message
  - New messages use newly selected provider
  - No message loss or duplication
- **Behavior:**
  1. User in conversation with OpenAI
  2. Switches to Anthropic
  3. Next message sent to Anthropic
  4. Previous OpenAI responses still visible
  5. Can switch back to OpenAI
- **Acceptance Criteria:**
  - ✓ No context loss on switch
  - ✓ Messages clearly attributed
  - ✓ Can switch any time
  - ✓ No duplicate messages

#### REQ-501-G: Provider Error Handling
- **Description:** Gracefully handle provider-specific errors
- **Common Errors:**
  - API key invalid → Show "Configure provider in settings"
  - Rate limit → Show "Provider rate limited, retry in X seconds"
  - Timeout → Show "Provider not responding, try different provider"
  - Model not found → Show "Model not available"
  - Content filter → Show "Provider blocked this content"
- **Retry Logic:**
  - Automatic retry for timeouts (up to 3 times)
  - User manual retry for other errors
  - Exponential backoff between retries
- **Acceptance Criteria:**
  - ✓ All errors handled gracefully
  - ✓ User-friendly error messages
  - ✓ Retry logic works
  - ✓ No crashes or hangs

#### REQ-501-H: Provider Performance Tracking
- **Description:** Track response times and costs per provider
- **Metrics:**
  - Response time (ms)
  - Tokens used (for cost calculation)
  - Success rate (%)
  - Average cost per message
- **Display:** Optional stats in settings
- **Storage:** Aggregated in-memory (not persisted)
- **Acceptance Criteria:**
  - ✓ Metrics tracked
  - ✓ Can view statistics
  - ✓ Costs calculated
  - ✓ Data helps with provider selection

### 2.2 Technical Constraints

- **Timeout:** 30s max per provider call
- **Retry Limit:** 3 maximum attempts
- **Model Context:** Up to 128,000 tokens (claude-3) or 8,000 (gpt-3.5)
- **Rate Limits:** Respected per provider
- **Concurrent:** Max 5 concurrent requests to providers

---

## 3. Implementation Details

### 3.1 Backend Services

**AIProviderService** (backend/services/ai_provider_service.py)

**Key Methods:**
- `get_available_providers()` - List all configured providers
- `get_provider_health()` - Check if provider is working
- `call_provider(provider_id, message, context)` - Send request to provider
- `_handle_provider_error(error)` - Convert provider errors to user messages
- `_select_fallback_provider()` - Choose backup if primary fails

**Provider Implementations:**
- `OpenAIProvider` - Calls OpenAI API
- `AnthropicProvider` - Calls Anthropic API
- `OllamaProvider` - Calls local Ollama instance
- `CohereProvider` - Calls Cohere API

### 3.2 Frontend Components

**ProviderSelector.tsx** - Dropdown in header with:
- Current provider display
- List of all providers
- Health status indicators
- Click to switch

**ProviderSettings.tsx** - Settings page section with:
- API key input per provider
- Test button
- Model selection dropdown
- Health status display

### 3.3 API Endpoints

- **GET** `/api/ai-providers` - List all providers
- **GET** `/api/ai-providers/{id}/health` - Health check
- **GET** `/api/ai-providers/{id}/models` - Available models
- **POST** `/api/ai-providers/{id}/test` - Test configuration
- **PUT** `/api/ai-providers/{id}/config` - Update provider config

---

## 4. Testing Strategy

**Test File:** `tests/unit/test_ai_provider_service.py`

- `test_list_available_providers`: All configured providers listed
- `test_provider_health_check`: Health endpoint works
- `test_switch_provider_mid_conversation`: No message loss on switch
- `test_error_handling`: Provider errors handled gracefully
- `test_fallback_on_unhealthy`: Falls back when primary unavailable
- `test_model_selection`: Can select different models

---

## 5. Dependencies & Relationships

### 5.1 Depends On

| REQ-ID | Title | Reason |
|--------|-------|--------|
| REQ-105-109 | API key management | Provider keys configured here |
| REQ-308 | Settings button | Provider config in settings |
| REQ-401 | Message history | Messages track provider_id |

### 5.2 Enables / Unblocks

| REQ-ID | Title | How |
|--------|-------|-----|
| REQ-502 | Provider status display | Shown in dropdown |
| REQ-507 | Provider selector | Implemented here |
| REQ-514 | Send to provider | Uses this service |

---

## 6. Acceptance Checklist

- [x] Multiple providers supported
- [x] Header selector works
- [x] Health checks functional
- [x] Model selection works
- [x] Mid-conversation switching works
- [x] Error handling complete
- [x] Tests passing

---

## Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-15 | Development Team | Initial specification |

---

**Status:** Ready for team use
