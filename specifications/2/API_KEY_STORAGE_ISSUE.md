# API Key Storage Issue - Analysis & Security Concern

## Current Implementation Status

### ❌ **ISSUE: API keys are being stored in JSON files, NOT in .env file**

**Location:** `backend/services/ai_provider_service.py`

```python
# Lines 34-42: Initialization
def __init__(self, data_dir: str = "data"):
    self.data_dir = Path(data_dir)
    self.providers_dir = self.data_dir / "ai_providers"  # <-- Creates data/ai_providers directory

# Lines 80-81: Provider file location
def _get_provider_file(self, provider_id: UUID) -> Path:
    return self.providers_dir / f"{provider_id}.json"  # <-- Stores as JSON file

# Lines 100-113: Saves entire provider object including API key
def _save_provider(self, provider: AIProvider):
    """Save a provider configuration to disk."""
    provider_file = self._get_provider_file(provider.id)
    data = provider.model_dump()  # <-- Includes api_key field
    # ... JSON save with api_key in plaintext
```

### 📂 **Current Storage Structure**

```
data/
├── ai_providers/
│   ├── {provider-uuid-1}.json  <-- Contains API key in plaintext
│   ├── {provider-uuid-2}.json  <-- Contains API key in plaintext
│   └── ...
└── other_data/
```

### 📝 **Example JSON File Content**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "openai",
  "provider_type": "openai",
  "is_active": true,
  "api_key": "sk-1234567890abcdefghijklmnop",  <-- ❌ PLAINTEXT API KEY!
  "base_url": "https://api.openai.com/v1",
  "created_at": "2025-11-12T07:30:00",
  "updated_at": "2025-11-12T07:30:00"
}
```

## Security Issues

### 1. ❌ **API Keys in JSON Files**
- API keys stored as plaintext in `data/ai_providers/*.json`
- Not using .env file as documented
- If someone accesses the `data/` directory, they get all API keys

### 2. ❌ **Requirement 1.3.2 Violation**
The tests claim API keys are stored securely, but they're actually in JSON:
- ✅ Frontend correctly doesn't store API keys in localStorage
- ❌ Backend stores them in plaintext JSON files
- ❌ Not using .env file as intended

### 3. ❌ **No Encryption**
- API keys are not encrypted on disk
- JSON files are world-readable by default
- No key derivation or hashing

### 4. ⚠️ **Version Control Risk**
- If `data/` directory is accidentally committed to git
- All API keys become exposed in git history

## How It Should Work

### Correct Implementation:
```
Backend Setup:
1. User inputs API key in Provider Management UI
2. Frontend sends to backend via POST /api/providers/{id}/config
3. Backend receives API key
4. Backend saves ONLY to .env file (not JSON):
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=claude-...
5. Backend uses os.getenv() to load at runtime
6. API key never persists in data files
```

### Current (Broken) Implementation:
```
What's Happening Now:
1. Frontend sends API key to backend
2. Backend saves to: data/ai_providers/{uuid}.json
3. API key stored as plaintext in JSON
4. Backend can read from JSON file
5. Anyone with file system access gets API keys
```

## Related Code

### Backend Settings (Correct approach that's not being used):
File: `backend/config/settings.py`
```python
OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
```

### Backend API Endpoints:
File: `backend/api/ai_providers.py` (Lines 30-45)
```python
@router.post("/providers")
async def create_provider(provider_data: AIProviderCreate) -> AIProvider:
    """
    Create a new AI provider.
    - **api_key**: API key for authentication
    """
    # Receives API key but then saves it to JSON via AIProviderService
```

### Frontend Test Claims (That are false):
File: `tests/test_update_requirements_backend.py`
```python
def test_env_file_storage_not_frontend(self):
    """Test that API keys are stored in .env file, not accessible to frontend."""
    env_file = self.temp_dir / ".env"
    env_content = "OPENAI_API_KEY=sk-test-12345abcde\n..."
    env_file.write_text(env_content)
    # This test PASSES but doesn't verify the actual backend implementation!
```

## Recommendations

### Immediate Fix (Priority 1)
**Modify `AIProviderService._save_provider()` to exclude API keys:**

```python
def _save_provider(self, provider: AIProvider):
    """Save a provider configuration to disk (without API key)."""
    provider_file = self._get_provider_file(provider.id)
    data = provider.model_dump(exclude={'api_key'})  # <-- Exclude API key
    data['id'] = str(data['id'])
    data['created_at'] = data['created_at'].isoformat()
    data['updated_at'] = data['updated_at'].isoformat()
    
    with open(provider_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```

### Better Fix (Priority 1)
**Save API key to .env file instead:**

```python
def _save_provider_config(self, provider_id: str, api_key: str):
    """Save API key to .env file."""
    env_file = Path(".env")
    
    # Read existing .env
    env_vars = {}
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    
    # Add new API key
    env_key = f"{provider_id.upper()}_API_KEY"
    env_vars[env_key] = api_key
    
    # Write back
    with open(env_file, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
```

### Best Fix (Priority 2)
**Use environment variables at startup:**

```python
def load_provider_from_env(provider_name: str) -> Optional[str]:
    """Load API key from environment variables only."""
    api_key = os.getenv(f"{provider_name.upper()}_API_KEY")
    if not api_key:
        logger.warning(f"No API key found for {provider_name}")
    return api_key
```

## Files That Need Changes

1. **`backend/services/ai_provider_service.py`**
   - Modify `_save_provider()` to exclude api_key
   - Add new method `_save_provider_config()` to save to .env

2. **`backend/api/ai_providers.py`**
   - Update provider config endpoint to save to .env

3. **`backend/config/settings.py`**
   - Keep using os.getenv() for loading (already correct)

4. **Tests**
   - Update `test_env_file_storage_not_frontend` to verify actual implementation
   - Add test for `.env` file storage

## Summary

| Aspect | Current | Should Be | Status |
|--------|---------|-----------|--------|
| **Storage Location** | `data/ai_providers/*.json` | `.env` file | ❌ Wrong |
| **Encryption** | None (plaintext) | Encrypted or env vars only | ❌ Wrong |
| **Security Risk** | HIGH - exposed in JSON | LOW - env var only | ❌ Vulnerable |
| **Requirement 1.3.2** | Claims compliance | Actually not compliant | ❌ Failing |
| **Frontend** | Correctly doesn't store | Correct ✓ | ✅ OK |

**Action Required:** Implement one of the recommended fixes above to properly secure API keys.
