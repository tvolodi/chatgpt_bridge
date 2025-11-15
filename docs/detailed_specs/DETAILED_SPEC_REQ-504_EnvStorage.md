# REQ-504: Provider Configuration in .env

**Registry Entry:** See `docs/01_requirements_registry.md` (Line 114)  
**Functionality Reference:** `specifications/functionality.md` Section 5.1.4  
**Document Version:** 1.0  
**Last Updated:** November 15, 2025  
**Status:** implemented  

---

## 1. Overview

### 1.1 Brief Description
Store all provider configurations, API keys, and sensitive parameters securely in the `.env` file at the project root. The `.env` file is the single source of truth for all environment-specific settings, ensuring no hardcoded values in source code and enabling safe credential management.

### 1.2 Business Value
- **Security:** Credentials never in version control or source code
- **Environment Flexibility:** Different configs for dev/staging/production
- **Credential Isolation:** Each provider's keys separate and protected
- **Ease of Deployment:** Simple configuration for new deployments
- **Compliance:** Meets security best practices for sensitive data

---

## 2. Functional Requirements

### 2.1 Core Requirements

#### REQ-504-A: .env File Structure and Location
- **Description:** Define .env file format and location
- **Location:** Project root directory
  - File path: `<project_root>/.env`
  - Sibling to package.json, src/, backend/, etc.
- **Format:** Standard key=value pairs
- **Not tracked:** Add `.env` to `.gitignore`
- **Backup:** Create `.env.example` for reference
- **Character Encoding:** UTF-8 only
- **Example Structure:**
  ```
  # Environment
  NODE_ENV=development
  DEBUG=false
  
  # OpenAI Configuration
  OPENAI_API_KEY=sk-...
  OPENAI_BASE_URL=https://api.openai.com/v1
  
  # Anthropic Configuration
  ANTHROPIC_API_KEY=claude-...
  ANTHROPIC_BASE_URL=https://api.anthropic.com/v1
  
  # Azure OpenAI Configuration
  AZURE_OPENAI_API_KEY=...
  AZURE_OPENAI_BASE_URL=https://eastus.openai.azure.com/v1
  
  # Ollama Configuration
  OLLAMA_BASE_URL=http://localhost:11434
  
  # Provider Parameters (optional overrides)
  OPENAI_TEMPERATURE=0.7
  OPENAI_MAX_TOKENS=2000
  ANTHROPIC_TEMPERATURE=1.0
  ```
- **Acceptance Criteria:**
  - ✓ .env exists at project root
  - ✓ Contains all required API keys
  - ✓ Format is valid key=value pairs
  - ✓ UTF-8 encoding
  - ✓ .gitignore excludes .env

#### REQ-504-B: API Key Environment Variables
- **Description:** Store API keys securely as environment variables
- **Key Naming Convention:** `<PROVIDER_NAME>_API_KEY`
- **Examples:**
  - `OPENAI_API_KEY` → OpenAI API key
  - `ANTHROPIC_API_KEY` → Anthropic API key
  - `AZURE_OPENAI_API_KEY` → Azure OpenAI API key
  - `COHERE_API_KEY` → Cohere API key
  - `HUGGINGFACE_API_KEY` → Hugging Face API key
- **Key Format:**
  - Length: 20-500 characters (varies by provider)
  - Characters: Alphanumeric, hyphens, underscores
  - No spaces or special shell characters
- **Key Value Examples:**
  - OpenAI: `sk-proj-...` or `sk-...` (typically starts with `sk-`)
  - Anthropic: `sk-ant-...` (typically starts with `sk-ant-`)
  - Azure: Long hex string (64+ characters)
  - Generic: Any alphanumeric string
- **Sensitive Data Handling:**
  - Never log full API keys (mask in output)
  - Never display in UI (except masked version)
  - Load into memory at startup only
  - Keep in memory only as long as needed
- **Acceptance Criteria:**
  - ✓ API keys stored in .env only
  - ✓ Keys loaded at application startup
  - ✓ Never appear in source code
  - ✓ Never logged in plaintext
  - ✓ Correctly formatted per provider

#### REQ-504-C: Endpoint URL Configuration
- **Description:** Allow override of default API endpoint URLs via .env
- **Naming Convention:** `<PROVIDER_NAME>_BASE_URL`
- **Examples:**
  - `OPENAI_BASE_URL=https://api.openai.com/v1`
  - `ANTHROPIC_BASE_URL=https://api.anthropic.com/v1`
  - `OLLAMA_BASE_URL=http://localhost:11434`
  - `CUSTOM_PROVIDER_BASE_URL=https://custom.ai.provider.com/v1`
- **Use Cases:**
  - Proxy endpoints (corporate firewall)
  - Alternative providers with same API format
  - Development vs production endpoints
  - Local instances (Ollama, local models)
  - Azure regions (multiple deployments)
- **Default Behavior:**
  - If `<PROVIDER>_BASE_URL` not in .env, use default from config
  - If present, override default completely
- **Format Validation:**
  - Must start with `http://` or `https://`
  - Must be valid URL format
  - May include port number
  - May include path prefix
- **Examples:**
  ```
  OPENAI_BASE_URL=https://custom-proxy.company.com/openai
  OLLAMA_BASE_URL=http://ai-server.local:11434
  AZURE_OPENAI_BASE_URL=https://eastus.openai.azure.com
  ```
- **Acceptance Criteria:**
  - ✓ Base URL overrides supported
  - ✓ URLs validated on load
  - ✓ Defaults used when override absent
  - ✓ Multiple endpoints can be configured

#### REQ-504-D: Provider-Specific Parameter Configuration
- **Description:** Configure provider parameters via .env (optional, can also be in settings)
- **Naming Convention:** `<PROVIDER_NAME>_<PARAMETER_NAME>`
- **Common Parameters:**
  - `OPENAI_TEMPERATURE=0.7`
  - `OPENAI_MAX_TOKENS=2000`
  - `ANTHROPIC_TEMPERATURE=1.0`
  - `ANTHROPIC_MAX_TOKENS=1024`
- **Parameter Types in .env:**
  - String values: `MODEL=gpt-4`
  - Numeric values: `TEMPERATURE=0.7`
  - Boolean values: `DEBUG=true`
  - CSV lists: `STOP_SEQUENCES=stop1,stop2,stop3`
- **Priority:**
  - .env values are baseline defaults
  - Settings page can override (higher priority)
  - Session/project settings can override further
- **Examples:**
  ```
  # Default parameters for all requests
  OPENAI_TEMPERATURE=0.7
  OPENAI_MAX_TOKENS=2000
  OPENAI_TOP_P=1.0
  
  ANTHROPIC_TEMPERATURE=1.0
  ANTHROPIC_MAX_TOKENS=1024
  
  # Model selection
  OPENAI_MODEL=gpt-4
  ANTHROPIC_MODEL=claude-3-sonnet
  ```
- **Acceptance Criteria:**
  - ✓ Parameters loaded from .env
  - ✓ Types parsed correctly (string, number, boolean)
  - ✓ Can override settings defaults
  - ✓ Invalid parameters logged with warning

#### REQ-504-E: Configuration Loading and Parsing
- **Description:** Load and parse .env file on application startup
- **Loading Process:**
  1. Check for `.env` file at project root
  2. Read file content (UTF-8 encoding)
  3. Parse key=value lines
  4. Skip comments (lines starting with #)
  5. Skip blank lines
  6. Trim whitespace from keys and values
  7. Load into environment variables
  8. Validate required keys present
- **Parsing Rules:**
  - Line format: `KEY=VALUE` or `KEY="VALUE"` or `KEY='VALUE'`
  - Comments: `# This is a comment`
  - Empty lines: ignored
  - Multiline values: Not supported (single line only)
  - Escapes: `\n`, `\t` converted appropriately
  - Inline comments: Not supported
- **Parser Implementation:**
  ```python
  def parse_env_file(filepath):
      env_vars = {}
      with open(filepath, 'r', encoding='utf-8') as f:
          for line in f:
              line = line.strip()
              # Skip comments and empty lines
              if not line or line.startswith('#'):
                  continue
              # Parse key=value
              if '=' in line:
                  key, value = line.split('=', 1)
                  key = key.strip()
                  value = value.strip()
                  # Remove quotes if present
                  if (value.startswith('"') and value.endswith('"')) or \
                     (value.startswith("'") and value.endswith("'")):
                      value = value[1:-1]
                  env_vars[key] = value
      return env_vars
  ```
- **Error Handling:**
  - Invalid format line → Log warning, skip line
  - Missing .env file → Use only defaults (OK if no API keys set)
  - Malformed key=value → Skip line with warning
  - Encoding issues → Use UTF-8, log if fails
- **Acceptance Criteria:**
  - ✓ .env file parsed correctly
  - ✓ Key=value pairs extracted
  - ✓ Comments ignored
  - ✓ Invalid lines skipped safely
  - ✓ UTF-8 encoding handled

#### REQ-504-F: Environment Variable Hot-Reload
- **Description:** Detect .env changes and reload without restart
- **Detection Method:**
  - Watch `.env` file for changes
  - Use file system watcher (debounced)
  - Check every 10 seconds (if watcher unavailable)
- **Reload Process:**
  1. Detect .env file change
  2. Re-read and re-parse .env file
  3. Update in-memory environment variables
  4. Validate all required keys still present
  5. Re-check provider availability
  6. Update UI to reflect new provider status
  7. Log reload event
- **User-Triggered Reload:**
  - Button in Settings page: "Refresh Provider Configuration"
  - Instantly reloads .env
  - Shows confirmation message
- **Error Handling:**
  - Invalid .env after changes → Keep previous valid config, log error
  - Missing required keys after reload → Mark provider unavailable
  - Syntax error → Log and continue with previous config
- **Acceptance Criteria:**
  - ✓ File changes detected
  - ✓ Configuration reloaded
  - ✓ Providers updated in UI
  - ✓ No restart required
  - ✓ Errors handled gracefully

#### REQ-504-G: .env.example Reference File
- **Description:** Create template .env.example for users
- **Content:** Sample of all possible configuration keys
- **Purpose:**
  - Reference for what can be configured
  - Template for new deployments
  - Documentation of configuration options
- **File Location:** Project root, committed to version control
- **Example Content:**
  ```
  # .env.example - Configuration template
  # Copy this file to .env and fill in your API keys
  # Never commit .env to version control
  
  # Environment
  NODE_ENV=development
  DEBUG=false
  
  # OpenAI Configuration
  # Get API key from: https://platform.openai.com/api-keys
  OPENAI_API_KEY=sk-your-api-key-here
  # Optional: Override default endpoint
  # OPENAI_BASE_URL=https://api.openai.com/v1
  # Optional: Override default parameters
  # OPENAI_TEMPERATURE=0.7
  # OPENAI_MAX_TOKENS=2000
  
  # Anthropic Configuration
  # Get API key from: https://console.anthropic.com/
  ANTHROPIC_API_KEY=sk-ant-your-api-key-here
  # ANTHROPIC_BASE_URL=https://api.anthropic.com/v1
  
  # Azure OpenAI Configuration
  # Get API key from: https://portal.azure.com/
  # AZURE_OPENAI_API_KEY=your-key-here
  # AZURE_OPENAI_BASE_URL=https://resource.openai.azure.com
  
  # Ollama Configuration (for local models)
  # OLLAMA_BASE_URL=http://localhost:11434
  
  # Additional providers can be added following the pattern:
  # <PROVIDER_NAME>_API_KEY=your-key
  # <PROVIDER_NAME>_BASE_URL=https://api.provider.com
  ```
- **Maintenance:**
  - Keep updated when adding new providers
  - Document all possible keys
  - Include helpful comments and links
  - Remove any actual keys or secrets
- **Acceptance Criteria:**
  - ✓ .env.example exists
  - ✓ Contains all configurable keys
  - ✓ Includes helpful comments
  - ✓ No real API keys included
  - ✓ Updated with new providers

#### REQ-504-H: Environment Variable Masking
- **Description:** Mask API keys in logs and UI
- **Masking Rules:**
  - Show only first 4 and last 4 characters
  - Replace middle with `****`
  - Example: `sk-proj-****...****bcd1` (for key `sk-proj-abcdefghij...abcd1`)
- **Logging:**
  - Never log full API key
  - Use masked version only
  - Include in error messages if needed for troubleshooting
- **UI Display:**
  - Settings page shows masked version
  - Copy button copies unmasked version (to clipboard only)
  - Hide button to show/hide (defaults to hidden)
- **Implementation:**
  ```python
  def mask_api_key(key):
      if len(key) <= 8:
          return key  # Too short to mask safely
      return f"{key[:4]}****...****{key[-4:]}"
  ```
- **Acceptance Criteria:**
  - ✓ API keys masked in all logs
  - ✓ UI shows masked versions
  - ✓ Can still verify if configured
  - ✓ No unmasked keys in output

#### REQ-504-I: Provider Configuration Validation at Startup
- **Description:** Validate all environment variables at application startup
- **Validation Checks:**
  1. .env file exists (if API keys needed)
  2. All required API key variables present
  3. API keys are non-empty strings
  4. Base URL variables have valid format
  5. Parameter values have correct types
- **Validation Results:**
  - Provider marked `is_available=true` if API key present
  - Provider marked `is_available=false` if API key missing
  - Invalid config logged as error
  - Warning if recommended provider not configured
- **Error Messages:**
  - Missing key: "OpenAI API key not found. Set OPENAI_API_KEY in .env"
  - Invalid format: "OPENAI_BASE_URL must be valid HTTPS URL"
  - Suggestion: "Tip: Use .env.example as template"
- **Startup Behavior:**
  - Validation errors don't prevent startup (graceful degradation)
  - Unavailable providers disabled in UI
  - User can fix and refresh
- **Acceptance Criteria:**
  - ✓ Validation runs at startup
  - ✓ Invalid configs detected
  - ✓ Clear error messages provided
  - ✓ User can fix and retry

#### REQ-504-J: Multi-Environment Support
- **Description:** Support different .env files for different environments
- **Approach 1: Single .env (Recommended)**
  - One .env file per deployment
  - Different values for dev/staging/prod
- **Approach 2: Environment-Specific Files (Optional)**
  - `.env.development` for local dev
  - `.env.staging` for staging
  - `.env.production` for production
  - Loaded based on `NODE_ENV` variable
- **Priority Order (if using multiple files):**
  1. Check `.env.{NODE_ENV}.local` (local overrides, not committed)
  2. Check `.env.{NODE_ENV}` (environment-specific, committed)
  3. Check `.env.local` (local overrides, not committed)
  4. Check `.env` (shared defaults, committed)
- **Git Ignore:**
  ```gitignore
  .env
  .env.local
  .env.*.local
  ```
- **Acceptance Criteria:**
  - ✓ Support single .env per deployment
  - ✓ Environment detection works
  - ✓ Correct file loaded per environment
  - ✓ Local overrides possible

### 2.2 Technical Constraints

- **File Size:** .env must be under 100KB
- **Max Variables:** Support up to 100 environment variables
- **Line Length:** Individual lines must be under 1,000 characters
- **Parsing Time:** <100ms to parse and load .env
- **Encoding:** UTF-8 only
- **Availability:** .env file optional (graceful fallback)
- **Reload Delay:** File changes detected within 2 seconds
- **Memory:** Configuration cached in memory, updated on reload

---

## 3. Implementation Details

### 3.1 Backend Services

**EnvConfigService** (`backend/services/env_config_service.py`)

**Key Methods:**
- `load_env_file(filepath)` - Read and parse .env
- `parse_env_line(line)` - Parse single key=value
- `validate_env_variables()` - Validate configuration
- `get_env_variable(key, default=None)` - Get with fallback
- `watch_env_file()` - Monitor for changes (optional)
- `reload_env_variables()` - Reload from file
- `mask_sensitive_value(key, value)` - Mask for display

**Implementation Pattern:**
```python
class EnvConfigService:
    def __init__(self):
        self.config = {}
        self.watchers = []
        self.load_env_file()
    
    def load_env_file(self):
        # Load .env file
        # Parse key=value pairs
        # Set os.environ
        pass
    
    def watch_env_file(self):
        # Use watchdog or polling
        # Call reload_env_variables on change
        pass
```

### 3.2 API Endpoints

- **POST** `/api/config/validate-env` - Validate current .env setup
- **POST** `/api/config/reload-env` - Trigger manual reload
- **GET** `/api/config/environment` - Get current environment variables (masked)

### 3.3 Configuration Flow

```
Application Start:
1. EnvConfigService.__init__()
2. load_env_file('.env')
3. Parse key=value pairs
4. Set os.environ
5. ProviderConfigService.load_providers()
6. Validate each provider's API key
7. Update provider availability
8. Start .env file watcher
9. UI loads available providers
```

---

## 4. Testing Strategy

**Test File:** `tests/unit/test_env_config_service.py`

- `test_load_env_file_success`: File loads correctly
- `test_parse_env_line_simple`: Parses `KEY=VALUE`
- `test_parse_env_line_quoted`: Parses `KEY="VALUE"`
- `test_parse_env_line_with_spaces`: Handles whitespace
- `test_skip_comments`: Ignores comment lines
- `test_skip_empty_lines`: Handles blank lines
- `test_parse_env_file_complete`: Full file parsing works
- `test_validate_api_keys_present`: Detects missing keys
- `test_validate_base_url_format`: URL validation works
- `test_mask_api_key`: Masking works correctly
- `test_reload_on_file_change`: Hot-reload functional
- `test_invalid_env_graceful`: Errors handled gracefully

**Test File:** `tests/integration/test_env_file.py`

- `test_env_file_loading`: Real .env file loads
- `test_provider_availability_from_env`: Providers available based on keys
- `test_env_override_default_endpoints`: Overrides work
- `test_multiline_values_not_supported`: Rejects multiline
- `test_special_characters_in_values`: Handles special chars
- `test_env_reload_preserves_connection`: No interruption on reload

---

## 5. Dependencies & Relationships

### 5.1 Depends On

| REQ-ID | Title | Reason |
|--------|-------|--------|
| REQ-105-109 | API key management | Keys stored and managed here |
| REQ-502 | Endpoint authentication | Endpoints and auth loaded from .env |

### 5.2 Enables / Unblocks

| REQ-ID | Title | How |
|--------|-------|-----|
| REQ-501 | Multiple provider support | Provider config sourced from .env |
| REQ-503 | Provider parameters | Parameter defaults in .env |
| REQ-505 | Dynamic provider loading | Based on keys in .env |

---

## 6. Acceptance Checklist

- [x] .env file at project root
- [x] Proper key=value format
- [x] API keys stored in .env only
- [x] No hardcoded values in code
- [x] Endpoint URLs configurable
- [x] Provider parameters configurable
- [x] Hot-reload working
- [x] Configuration validated at startup
- [x] .env.example template provided
- [x] Masking in UI and logs
- [x] Tests passing

---

## Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-15 | Development Team | Initial specification |

---

**Status:** Ready for team use
