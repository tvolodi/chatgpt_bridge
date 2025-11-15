# REQ-705: API Key Management and Security

**Registry Entry:** See `docs/01_requirements_registry.md` (Line 133)  
**Functionality Reference:** `specifications/functionality.md` Section 7  
**Document Version:** 1.0  
**Last Updated:** November 15, 2025  
**Status:** implemented  

---

## 1. Overview

### 1.1 Brief Description
Securely manage AI provider API keys with environment-based storage, hot-reload capability, validation, and per-provider configuration - enabling users to switch between providers without application restart.

### 1.2 Business Value
- **Security:** Keys never hardcoded or logged
- **Flexibility:** Update providers without restarting
- **Simplicity:** Single configuration point
- **Safety:** Validation prevents invalid configurations

---

## 2. Functional Requirements

### 2.1 Core Requirements

#### REQ-705-A: API Keys in Environment Variables
- **Description:** Store all API keys in environment variables, never hardcoded
- **Implementation:**
  - Keys loaded from system environment or .env file
  - No keys in source code whatsoever
  - No keys in logs or console output
- **Variable Names:**
  - OPENAI_API_KEY
  - ANTHROPIC_API_KEY
  - OLLAMA_BASE_URL (not a key, but endpoint)
  - COHERE_API_KEY
- **Loading Order:**
  1. System environment variables (highest priority)
  2. .env file (override possible)
  3. Default to None (provider not available)
- **Validation:** Non-empty check, format validation per provider
- **Acceptance Criteria:**
  - ✓ Keys loaded from environment
  - ✓ No keys in code
  - ✓ No keys in logs
  - ✓ Secure loading order respected

#### REQ-705-B: .env File for API Key Persistence
- **Description:** Persist keys to .env file for development
- **Location:** Project root `.env` file
- **Format:** Standard env format
  ```
  OPENAI_API_KEY=sk-proj-...
  ANTHROPIC_API_KEY=sk-ant-...
  OLLAMA_BASE_URL=http://localhost:11434
  ```
- **File Permissions:** 600 (readable by owner only)
- **Git:** .env in .gitignore (never committed)
- **Hot-Reload:** Changes to .env reloaded on next restart OR via API call
- **Backup:** Users should backup .env file
- **Example Setup:**
  ```bash
  # On first run, user creates .env:
  cp .env.example .env
  # Then edits with their keys
  # Or uses Settings UI to add keys
  ```
- **Acceptance Criteria:**
  - ✓ Keys persist to .env file
  - ✓ .env loaded on app start
  - ✓ File permissions secure
  - ✓ Not committed to git
  - ✓ Can be updated without restart

#### REQ-705-C: Multiple Provider API Key Support
- **Description:** Support keys for multiple providers simultaneously
- **Configuration:** Each provider has independent key
- **Storage:** All in same .env file, prefixed by provider
- **Example:**
  ```
  OPENAI_API_KEY=sk-...
  ANTHROPIC_API_KEY=claude-...
  OLLAMA_BASE_URL=http://localhost:11434
  COHERE_API_KEY=...
  ```
- **Independence:** Removing one key doesn't affect others
- **Optional:** Providers work independently; missing key just disables provider
- **Acceptance Criteria:**
  - ✓ Multiple keys stored
  - ✓ Each independent
  - ✓ Can add/remove/update individually
  - ✓ Only configured providers available

#### REQ-705-D: Settings Page for API Key Management
- **Description:** User interface for viewing and updating keys
- **Features:**
  - Per-provider section with API key input
  - Visual indicator: "Configured" (✓) or "Not configured" (✗)
  - Keys masked in display (show first/last 4 chars: sk-...7h2a)
  - Test button for each provider
  - Save button for batch updates
- **UI Layout:**
  ```
  API KEYS TAB
  ├─ OpenAI
  │  ├─ API Key: [████████] (configured)
  │  ├─ Test Button → "✓ Connected"
  │  └─ Clear Button
  ├─ Anthropic
  │  ├─ API Key: [████████] (configured)
  │  ├─ Test Button → "✓ Connected"
  │  └─ Clear Button
  └─ Save Changes [Button]
  ```
- **Functionality:**
  - Input accepts full key (not masked during edit)
  - Tab key to move between providers
  - Test validates connectivity
  - Save updates .env and reloads config
- **Acceptance Criteria:**
  - ✓ Keys can be entered and saved
  - ✓ Masked display for privacy
  - ✓ Test button works
  - ✓ Updates persist
  - ✓ No keys in browser console

#### REQ-705-E: API Key Validation
- **Description:** Validate keys before saving
- **Validation Rules:**
  - Non-empty check
  - Format check (provider-specific):
    - OpenAI: Starts with "sk-"
    - Anthropic: Valid format
    - Ollama: Valid URL format
  - Length check (reasonable bounds)
  - Characters check (no spaces or special chars except -_)
- **Failure Handling:**
  - Show error message immediately
  - Clear which field is invalid
  - Don't save invalid keys
  - Don't try to use invalid keys
- **Example Errors:**
  - "OpenAI key must start with 'sk-'"
  - "API key cannot be empty"
  - "Invalid URL format for Ollama"
- **Acceptance Criteria:**
  - ✓ Invalid keys rejected
  - ✓ Error messages helpful
  - ✓ No partial saves
  - ✓ User can correct

#### REQ-705-F: API Key Testing
- **Description:** Test configuration without making AI calls
- **Implementation:**
  - Test endpoint per provider
  - Simple validation call (not full AI call)
  - Timeout: 5 seconds
  - Shows result: "Connected" or error
- **Test Behavior:**
  - OpenAI: Call models list endpoint
  - Anthropic: Call info endpoint
  - Ollama: Check if server responsive
- **UI:** Test button in settings with spinner and result
- **Error Cases:**
  - Timeout → "Provider not responding"
  - Invalid key → "Authentication failed"
  - Not configured → "No key provided"
- **API Endpoint:** POST `/api/settings/test-api-key`
  - Request: `{ provider: "openai", apiKey: "sk-..." }`
  - Response: `{ valid: bool, message: string }`
- **Acceptance Criteria:**
  - ✓ Test confirms connectivity
  - ✓ Error messages clear
  - ✓ No charges incurred
  - ✓ Helpful feedback

#### REQ-705-G: Hot-Reload API Keys
- **Description:** Update keys without restarting application
- **Implementation:**
  - Settings page saves keys to .env
  - Backend detects file change
  - Reloads environment into memory
  - New keys available immediately
  - Existing connections may complete but new calls use new keys
- **Behavior:**
  - User updates OpenAI key in settings
  - Clicks Save
  - Next message uses new key
  - No app restart needed
  - State preserved (messages, sessions, etc.)
- **Error Handling:**
  - If file write fails, show error
  - Keep old keys active
  - Don't crash the app
- **Acceptance Criteria:**
  - ✓ Keys reload without restart
  - ✓ New calls use new keys
  - ✓ No message loss
  - ✓ Error handled gracefully

#### REQ-705-H: API Key Security Best Practices
- **Description:** Implement security measures
- **Measures:**
  - Never log API keys (sanitize logs)
  - Never send keys to frontend
  - Never store in browser localStorage
  - Never include in error messages
  - Mask in UI (show last 4 chars only)
  - File permissions 600 on .env file
  - Keys only loaded once at startup (unless hot-reload)
- **Code Practices:**
  - Use constant env var names (not hardcoded)
  - Validate input sanitization
  - Use HTTPS for any network (production)
  - Consider key rotation (future)
- **Documentation:**
  - Warn users to keep .env private
  - Document .gitignore requirement
  - Explain why not to commit .env
- **Acceptance Criteria:**
  - ✓ Keys not logged
  - ✓ Keys not sent to frontend
  - ✓ Keys not in localStorage
  - ✓ File permissions secure
  - ✓ Documentation clear

### 2.2 Technical Constraints

- **Key Storage:** Environment variables + .env file only
- **Key Validation:** Format check before save
- **Hot-Reload:** Max 30 seconds between .env update and effect
- **Performance:** Key loading < 100ms
- **Timeout:** API tests < 5 seconds
- **Logging:** All API keys sanitized from logs

---

## 3. Implementation Details

### 3.1 Backend Services

**SettingsService** (backend/services/settings_service.py)

**Key Methods:**
- `load_api_keys()` - Load from environment at startup (lines 20-50)
  ```python
  def load_api_keys(self) -> Dict[str, str]:
      """Load API keys from environment"""
      keys = {
          "openai": os.getenv("OPENAI_API_KEY"),
          "anthropic": os.getenv("ANTHROPIC_API_KEY"),
          "ollama": os.getenv("OLLAMA_BASE_URL"),
      }
      return {k: v for k, v in keys.items() if v}  # Filter out None values
  ```

- `update_api_key(provider, key)` - Update key in .env (lines 52-80)
  - Validates format
  - Writes to .env file
  - Reloads into memory
  - Returns success/error

- `get_configured_providers()` - List available providers (lines 82-95)
  - Checks which keys are set
  - Returns provider objects with config status

- `test_api_key(provider, key)` - Test connectivity (lines 97-130)
  - Makes minimal provider call
  - Timeout: 5 seconds
  - Returns `{ valid: bool, message: str }`

- `sanitize_for_logging(text)` - Remove keys from logs (lines 132-150)
  - Replaces API keys with "***REDACTED***"
  - Used throughout codebase before logging

- `_load_env_file()` - Parse .env file (lines 152-170)
  - Reads .env from project root
  - Parses KEY=VALUE format
  - Loads into memory

- `_write_env_file(keys)` - Persist keys to .env (lines 172-190)
  - Writes all keys
  - Sets file permissions to 600
  - Atomic write (temp file + rename)

### 3.2 Frontend Components

**SettingsPage.tsx** - Settings with API key tab (lines 1-50)
- Displays settings tabs
- API Keys tab shows per-provider sections

**APIKeySettings.tsx** - API key input section (lines 50-200)
```typescript
export const APIKeySettings: React.FC = () => {
  const [keys, setKeys] = useState({})
  const [testing, setTesting] = useState<string | null>(null)
  const [testResults, setTestResults] = useState({})

  const handleTest = async (provider: string) => {
    setTesting(provider)
    const response = await fetch(`/api/settings/test-api-key`, {
      method: "POST",
      body: JSON.stringify({ provider, apiKey: keys[provider] })
    })
    const result = await response.json()
    setTestResults(prev => ({ ...prev, [provider]: result }))
    setTesting(null)
  }

  const handleSave = async () => {
    const response = await fetch(`/api/settings`, {
      method: "PUT",
      body: JSON.stringify({ api_providers: keys })
    })
    // Handle response
  }

  return (
    <div>
      {PROVIDERS.map(provider => (
        <div key={provider.id} className="mb-6">
          <label>{provider.name}</label>
          <input
            type="password"
            placeholder="Paste your API key here"
            value={keys[provider.id] || ""}
            onChange={(e) => setKeys({...keys, [provider.id]: e.target.value})}
          />
          <button onClick={() => handleTest(provider.id)}>
            {testing === provider.id ? "Testing..." : "Test Connection"}
          </button>
          {testResults[provider.id] && (
            <div className={testResults[provider.id].valid ? "text-green-600" : "text-red-600"}>
              {testResults[provider.id].message}
            </div>
          )}
        </div>
      ))}
      <button onClick={handleSave}>Save API Keys</button>
    </div>
  )
}
```

### 3.3 API Endpoints

- **GET** `/api/settings` - Get current configuration
  - Returns: Configured providers list (no keys)
  - Used by: Frontend to know which providers available

- **PUT** `/api/settings` - Update API keys
  - Request: `{ api_providers: { openai: "sk-...", ... } }`
  - Validates all keys
  - Writes to .env
  - Reloads
  - Returns: Success/validation errors

- **POST** `/api/settings/test-api-key` - Test key
  - Request: `{ provider: "openai", apiKey: "sk-..." }`
  - Response: `{ valid: bool, message: string }`

---

## 4. Testing Strategy

**Test File:** `tests/unit/test_api_key_management.py`

- `test_load_api_keys_from_env`: Load keys correctly
- `test_validate_api_key_format`: Reject invalid formats
- `test_write_keys_to_env_file`: Persist to .env
- `test_hot_reload_keys`: Keys reload without restart
- `test_sanitize_keys_in_logs`: Keys removed from logs
- `test_keys_not_in_frontend`: Backend doesn't send keys
- `test_test_api_key`: Test connectivity

---

## 5. Dependencies & Relationships

### 5.1 Depends On

| REQ-ID | Title | Reason |
|--------|-------|--------|
| REQ-108 | Settings page | UI provided by settings page |
| REQ-501 | Multi-provider | Keys configure multiple providers |

### 5.2 Enables / Unblocks

| REQ-ID | Title | How |
|--------|-------|-----|
| REQ-105-109 | All API key reqs | Implemented here |
| REQ-501 | Multi-provider | Keys enable providers |
| REQ-514 | Send to provider | Providers use these keys |

---

## 6. Security Considerations

### Critical Security Points

1. **Environment Loading:**
   - Load once at startup (efficient, secure)
   - System env vars > .env file > defaults
   - No file watching for constant reload

2. **Key Masking:**
   - Frontend: Show last 4 chars only
   - Logs: Sanitize all keys
   - Console: No keys printed
   - Network: No keys in URLs or bodies

3. **File Security:**
   - .env file permissions 600
   - Owner read/write only
   - .gitignore prevents accidental commit
   - Document best practices

4. **Error Handling:**
   - Don't expose key in error messages
   - Test failures don't leak format info
   - Validation errors generic

---

## 7. Acceptance Checklist

- [x] Keys loaded from environment
- [x] Keys persisted to .env
- [x] Multiple providers supported
- [x] Settings UI functional
- [x] Keys validated
- [x] Testing works
- [x] Hot-reload works
- [x] Security best practices followed
- [x] No keys exposed
- [x] Tests passing

---

## Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-15 | Development Team | Initial specification |

---

**Status:** Ready for team use
