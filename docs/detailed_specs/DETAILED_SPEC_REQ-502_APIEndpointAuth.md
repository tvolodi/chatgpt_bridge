# REQ-502: Unique API Endpoint and Authentication

**Registry Entry:** See `docs/01_requirements_registry.md` (Line 112)  
**Functionality Reference:** `specifications/functionality.md` Section 5.1.2  
**Document Version:** 1.0  
**Last Updated:** November 15, 2025  
**Status:** implemented  

---

## 1. Overview

### 1.1 Brief Description
Each AI provider has unique API endpoint configurations and authentication mechanisms. The system must support provider-specific base URLs and API key environment variables, enabling seamless integration with multiple AI services while maintaining security and flexibility.

### 1.2 Business Value
- **Provider Flexibility:** Support any API provider with custom endpoints
- **Security:** Each provider's credentials isolated in environment variables
- **Self-hosting:** Support on-premises and custom endpoint deployments (Ollama, local models)
- **Enterprise Integration:** Connect to enterprise API gateways and proxies
- **Future Extensibility:** Easy to add new providers without code changes

---

## 2. Functional Requirements

### 2.1 Core Requirements

#### REQ-502-A: Provider-Specific Base URL Configuration
- **Description:** Each provider has unique API base URL
- **Providers & Their Base URLs:**
  - **OpenAI:** `https://api.openai.com/v1`
  - **Anthropic:** `https://api.anthropic.com/v1`
  - **Azure OpenAI:** `https://{resource}.openai.azure.com/v1`
  - **Ollama (local):** `http://localhost:11434`
  - **Hugging Face Inference API:** `https://api-inference.huggingface.co`
  - **Custom/Enterprise:** Any HTTPS endpoint
- **Configuration Storage:** 
  - Provider metadata → `backend/config/providers_config.json` (base_url field)
  - Custom overrides → `.env` file (e.g., `OPENAI_BASE_URL=https://custom.endpoint.com/v1`)
- **Priority Order:**
  1. Check `.env` file for override (e.g., `OPENAI_BASE_URL`)
  2. Fall back to default from `providers_config.json`
- **Acceptance Criteria:**
  - ✓ Each provider has base_url field in config
  - ✓ Custom base URLs loadable from `.env`
  - ✓ Override mechanism works correctly
  - ✓ Multiple providers can have different endpoints

#### REQ-502-B: Provider-Specific API Key Authentication
- **Description:** Each provider uses unique authentication mechanism and key environment variable
- **Authentication Methods:**
  - **OpenAI:** Bearer token → Header: `Authorization: Bearer {key}`
  - **Anthropic:** API key → Header: `x-api-key: {key}` or `Authorization: Bearer {key}`
  - **Azure OpenAI:** API key → Header: `api-key: {key}`
  - **Ollama:** No authentication (local)
  - **Hugging Face:** Bearer token → Header: `Authorization: Bearer {key}`
  - **Custom:** Configurable per provider
- **Environment Variables:**
  - `OPENAI_API_KEY` → OpenAI authentication
  - `ANTHROPIC_API_KEY` → Anthropic authentication
  - `AZURE_OPENAI_API_KEY` → Azure OpenAI authentication
  - `OLLAMA_API_KEY` → (Optional, if using secured Ollama)
  - Custom providers → `{PROVIDER_NAME}_API_KEY` format
- **Key Storage:**
  - Never in source code or version control
  - Only in `.env` file (project root)
  - Loaded into environment at startup
  - Validated before first use
- **Key Validation:**
  - Format check (must be non-empty string)
  - Basic pattern validation (e.g., OpenAI keys start with `sk-`)
  - Optional: Test connection on startup
- **Acceptance Criteria:**
  - ✓ Each provider has unique auth mechanism
  - ✓ API keys loaded from environment variables only
  - ✓ No keys hardcoded anywhere
  - ✓ Keys validated at startup
  - ✓ Invalid keys trigger clear error message

#### REQ-502-C: Provider Configuration Metadata
- **Description:** Provider metadata includes endpoint and auth configuration details
- **Configuration Structure (providers_config.json):**
  ```json
  {
    "providers": [
      {
        "id": "openai",
        "name": "OpenAI",
        "description": "OpenAI GPT models",
        "base_url": "https://api.openai.com/v1",
        "api_key_env_var": "OPENAI_API_KEY",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer",
        "default_model": "gpt-4",
        "supported_models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
        "is_available": false,
        "message_format": "openai"
      },
      {
        "id": "anthropic",
        "name": "Anthropic",
        "description": "Anthropic Claude models",
        "base_url": "https://api.anthropic.com/v1",
        "api_key_env_var": "ANTHROPIC_API_KEY",
        "auth_header": "x-api-key",
        "auth_prefix": "",
        "default_model": "claude-3-sonnet",
        "supported_models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
        "is_available": false,
        "message_format": "anthropic"
      },
      {
        "id": "ollama",
        "name": "Ollama (Local)",
        "description": "Local Ollama models",
        "base_url": "http://localhost:11434",
        "api_key_env_var": null,
        "auth_header": null,
        "auth_prefix": null,
        "default_model": "llama2",
        "supported_models": [],
        "is_available": false,
        "message_format": "ollama"
      }
    ]
  }
  ```
- **Configuration Loading:**
  - Load at application startup
  - Validate all required fields present
  - Support dynamic reload on `.env` change
- **Acceptance Criteria:**
  - ✓ Config file exists and is valid JSON
  - ✓ All required fields present
  - ✓ Base URLs are valid URLs
  - ✓ Auth headers match provider specs
  - ✓ Message format is recognized

#### REQ-502-D: Runtime Configuration Resolution
- **Description:** At runtime, system resolves base_url and API key for each provider
- **Resolution Process:**
  1. Load provider metadata from `providers_config.json`
  2. Check for `.env` override for base_url (e.g., `OPENAI_BASE_URL`)
  3. If override found, use it; otherwise use default from metadata
  4. Load API key from environment variable (e.g., `OPENAI_API_KEY`)
  5. If API key exists and is non-empty, mark provider as `is_available=true`
  6. If API key missing or empty, mark as `is_available=false`
  7. Cache resolved configuration in memory
- **Validation:**
  - Base URL must be valid (starts with http:// or https://)
  - Base URL must be reachable (optional health check)
  - API key must be non-empty string (if required)
- **Error Handling:**
  - Invalid base URL → Log warning, use default
  - Missing required API key → Mark provider unavailable
  - Unreachable endpoint → Mark provider unhealthy (not unavailable)
- **Caching:**
  - Cache resolved config for 5 minutes
  - Invalidate on `.env` change or manual refresh
  - Provider availability re-checked on cache invalidation
- **Acceptance Criteria:**
  - ✓ Base URLs resolved correctly
  - ✓ API keys loaded from environment
  - ✓ Provider availability determined accurately
  - ✓ Configuration cached efficiently
  - ✓ Overrides respected

#### REQ-502-E: Multi-Endpoint Support for Single Provider
- **Description:** Support multiple instances of same provider (e.g., different Azure endpoints)
- **Use Cases:**
  - Multiple Azure OpenAI instances in different regions
  - Load balancing across multiple endpoints
  - Development, staging, production environments
- **Implementation:**
  - Provider ID can include region or instance identifier
  - Example: `openai-azure-eastus`, `openai-azure-westeu`
  - Each has own base_url and api_key_env_var
- **Configuration Example:**
  ```json
  {
    "id": "openai-azure-eastus",
    "name": "Azure OpenAI (East US)",
    "base_url": "https://eastus.openai.azure.com/v1",
    "api_key_env_var": "AZURE_OPENAI_API_KEY_EASTUS"
  }
  ```
- **Acceptance Criteria:**
  - ✓ Multiple instances of same provider supported
  - ✓ Each instance independent
  - ✓ Selector shows all instances with region info

#### REQ-502-F: Custom HTTP Headers and Authentication
- **Description:** Support various HTTP authentication schemes
- **Supported Schemes:**
  - Bearer tokens (most common)
  - API keys in custom headers
  - Basic authentication (username:password in Base64)
  - Custom headers (client-id, api-version, etc.)
- **Configuration Fields:**
  - `auth_header`: HTTP header name (e.g., "Authorization", "x-api-key")
  - `auth_prefix`: Prefix before key (e.g., "Bearer", "ApiKey")
  - `extra_headers`: Object with additional headers
  - Example:
    ```json
    {
      "auth_header": "Authorization",
      "auth_prefix": "Bearer",
      "extra_headers": {
        "User-Agent": "AIAssistant/1.0",
        "Accept": "application/json"
      }
    }
    ```
- **Acceptance Criteria:**
  - ✓ Bearer token authentication works
  - ✓ API key header authentication works
  - ✓ Custom headers included in requests
  - ✓ No authentication needed for local endpoints

#### REQ-502-G: Provider Configuration Validation
- **Description:** Validate provider configurations to catch errors early
- **Validation Checks:**
  - Base URL is valid format (http/https, valid domain)
  - Required fields present (id, name, base_url, api_key_env_var, message_format)
  - API key environment variable name is valid format
  - Auth header matches known patterns
  - Message format is recognized type
- **Validation Timing:**
  - On application startup
  - When settings updated
  - Before using provider (runtime validation)
- **Error Handling:**
  - Log detailed validation errors
  - Mark invalid provider as unavailable
  - Show user-friendly message in UI
  - Allow retry after fix
- **Acceptance Criteria:**
  - ✓ All configurations validated at startup
  - ✓ Invalid configs don't crash app
  - ✓ User notified of configuration problems
  - ✓ Can fix and retry

#### REQ-502-H: Environment Variable Refresh
- **Description:** Support updating API keys without restarting application
- **Implementation:**
  - Detect `.env` file changes
  - Reload environment variables
  - Re-validate provider availability
  - Update provider list in UI
- **Methods to Trigger Reload:**
  1. Automatic on `.env` file modification (watch mode)
  2. Manual via settings page "Refresh providers" button
  3. Scheduled checks every 30 seconds (optional)
- **Behavior:**
  - New API keys take effect immediately
  - Provider availability re-evaluated
  - Existing connections maintained
  - No message loss during reload
- **Acceptance Criteria:**
  - ✓ .env changes detected
  - ✓ New keys active without restart
  - ✓ UI updated to reflect availability
  - ✓ No interruption to conversations

### 2.2 Technical Constraints

- **Base URL:** Must be HTTPS for production (HTTP only for localhost)
- **API Key Length:** Support keys up to 500 characters
- **Auth Header:** Support custom headers up to 255 characters
- **Timeout:** Connection timeout 10s, request timeout 30s per provider
- **Retry Logic:** Up to 3 attempts with exponential backoff
- **Concurrent Requests:** Max 5 requests per provider simultaneously
- **Rate Limiting:** Respect provider-specific rate limits (429 responses)

---

## 3. Implementation Details

### 3.1 Backend Services

**ProviderConfigService** (`backend/services/provider_config_service.py`)

**Key Methods:**
- `load_provider_config()` - Load from providers_config.json
- `resolve_provider_endpoint(provider_id)` - Get base_url with override support
- `get_api_key(provider_id)` - Get key from environment variables
- `validate_provider_config(config)` - Validate configuration
- `refresh_provider_availability()` - Re-check which providers available
- `get_available_providers()` - Return list of configured providers with API keys
- `watch_env_file()` - Monitor .env for changes (optional)

**Provider Endpoint Resolver** (`backend/services/provider_endpoint_resolver.py`)

**Key Methods:**
- `resolve_endpoint(provider_id, override_url)` - Resolve final endpoint
- `build_auth_header(provider_id)` - Build Authorization header
- `apply_extra_headers(request, provider_id)` - Add custom headers
- `validate_endpoint_url(url)` - Validate URL format and reachability

### 3.2 Configuration Files

**File: `backend/config/providers_config.json`**
- Default provider configurations
- Base URLs for each provider
- Message format specifications
- Supported models list
- Example:
  ```json
  {
    "providers": [
      {
        "id": "openai",
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "api_key_env_var": "OPENAI_API_KEY",
        ...
      }
    ]
  }
  ```

**File: `.env` (user's project root)**
- Contains API keys and endpoint overrides
- Format: `PROVIDER_API_KEY=value` and `PROVIDER_BASE_URL=value`
- Example:
  ```
  OPENAI_API_KEY=sk-...
  OPENAI_BASE_URL=https://custom.openai.proxy.com/v1
  ANTHROPIC_API_KEY=claude-...
  ```

### 3.3 API Endpoints

- **GET** `/api/ai-providers` - List all providers with resolved endpoints and availability
- **GET** `/api/ai-providers/{id}/config` - Get specific provider configuration
- **POST** `/api/ai-providers/validate` - Validate endpoint URL
- **POST** `/api/ai-providers/refresh` - Reload .env and refresh availability

### 3.4 Example Request Flow

```
1. User configures OPENAI_API_KEY=sk-xyz in .env
2. Application starts → ProviderConfigService.load_provider_config()
3. Load providers_config.json with OPENAI base_url
4. Check for OPENAI_BASE_URL override in .env (not found)
5. Use default: https://api.openai.com/v1
6. Get API key: os.getenv("OPENAI_API_KEY") → "sk-xyz"
7. OpenAI marked as is_available=true
8. User composes message with OpenAI selected
9. Build request:
   - URL: https://api.openai.com/v1/chat/completions
   - Header: Authorization: Bearer sk-xyz
   - Body: messages, model, etc.
10. Send to OpenAI
11. Receive response → Extract content and save
```

---

## 4. Testing Strategy

**Test File:** `tests/unit/test_provider_config_service.py`

### Unit Tests:
- `test_load_provider_config_success`: Config loads correctly
- `test_resolve_base_url_no_override`: Uses default from config
- `test_resolve_base_url_with_override`: Uses .env override
- `test_get_api_key_found`: Returns key from environment
- `test_get_api_key_not_found`: Returns None when missing
- `test_validate_endpoint_url_valid`: Accepts valid URLs
- `test_validate_endpoint_url_invalid`: Rejects invalid URLs
- `test_build_auth_header_bearer`: Bearer token format correct
- `test_build_auth_header_custom`: Custom header format correct
- `test_provider_availability_with_key`: Marked available when key present
- `test_provider_availability_without_key`: Marked unavailable when key missing
- `test_refresh_on_env_change`: Detects .env changes and refreshes

**Test File:** `tests/integration/test_provider_endpoints.py`

- `test_openai_endpoint_configuration`: OpenAI endpoint correct
- `test_anthropic_endpoint_configuration`: Anthropic endpoint correct
- `test_azure_openai_endpoint_override`: Azure override works
- `test_ollama_local_endpoint`: Ollama localhost endpoint works
- `test_multiple_instances_same_provider`: Multiple Azure instances work
- `test_invalid_endpoint_handling`: Invalid endpoints handled gracefully

---

## 5. Dependencies & Relationships

### 5.1 Depends On

| REQ-ID | Title | Reason |
|--------|-------|--------|
| REQ-105-109 | API key management | API keys loaded here |
| REQ-501 | Multiple provider support | Each provider has unique endpoint |
| REQ-601 | File management | Config files managed on disk |

### 5.2 Enables / Unblocks

| REQ-ID | Title | How |
|--------|-------|-----|
| REQ-503 | Provider-specific parameters | Uses resolved endpoint config |
| REQ-504 | Provider configuration in .env | Documented here |
| REQ-514 | Send message to provider API | Uses resolved endpoint |

---

## 6. Acceptance Checklist

- [x] Each provider has unique base_url
- [x] Each provider has unique API key environment variable
- [x] Base URLs can be overridden in .env
- [x] API keys loaded from environment variables only
- [x] Provider availability determined by API key presence
- [x] Configuration validated at startup
- [x] Support multiple instances of same provider
- [x] Custom authentication headers supported
- [x] Environment variable refresh works
- [x] Tests passing

---

## Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-15 | Development Team | Initial specification |

---

**Status:** Ready for team use
