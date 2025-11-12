# API Key Update Fix - Complete Solution ✅

## The Complete Problem

When you tried to update an OpenAI API key through **Settings > Providers > Update**, the new key was **not being saved to the `.env` file**. This was due to **TWO separate issues**:

### Issue #1: Singleton Pattern (First Fix)
**Problem:** Each API request created a new service instance
- Request 1: New instance → saves data → instance discarded
- Request 2: New instance (empty) → can't persist updates

**Solution:** Changed to singleton pattern so all requests use same persistent instance

### Issue #2: Relative Path to .env (Second Fix) 
**Problem:** `.env` path was relative, depending on where server was started
- If you start server from `frontend/` directory → looks for `.env` there ❌
- If you start server from `c:\pf\AI-Chat-Assistant\` → finds `.env` correctly ✅

**Solution:** Store absolute path to `.env` file in `__init__`

---

## Complete Fix

### File: `backend/services/ai_provider_service.py`

#### Fix #1: Added absolute env_file_path in `__init__`
```python
def __init__(self, data_dir: str = "data"):
    """Initialize the AI provider service."""
    self.data_dir = Path(data_dir)
    self.providers_dir = self.data_dir / "ai_providers"
    self.providers_dir.mkdir(parents=True, exist_ok=True)
    
    # ✅ NEW: Set .env file path - always relative to project root
    # Find the project root by going up from the backend directory
    self.project_root = Path(__file__).parent.parent.parent
    self.env_file_path = self.project_root / ".env"
    
    # ... rest of init
```

#### Fix #2: Updated `_save_api_key_to_env()` to use instance path
```python
def _save_api_key_to_env(self, provider_name: str, api_key: str):
    """Save API key to .env file securely."""
    # ✅ Use instance's env_file_path instead of relative Path('.env')
    if not self.env_file_path.exists():
        self.env_file_path.touch()
    
    env_var_name = f"PROVIDER_API_KEY_{provider_name.upper().replace(' ', '_')}"
    
    try:
        set_key(str(self.env_file_path), env_var_name, api_key)
    except Exception as e:
        print(f"Warning: Could not save API key to .env file: {e}")
```

#### Fix #3: Updated `_load_api_key_from_env()` to use instance path
```python
def _load_api_key_from_env(self, provider_name: str) -> Optional[str]:
    """Load API key from .env file."""
    env_var_name = f"PROVIDER_API_KEY_{provider_name.upper().replace(' ', '_')}"
    
    api_key = os.getenv(env_var_name)
    if api_key:
        return api_key
    
    # ✅ Use instance's env_file_path
    if self.env_file_path.exists():
        dotenv_values_dict = dotenv_values(str(self.env_file_path))
        return dotenv_values_dict.get(env_var_name)
    
    return None
```

### File: `backend/api/ai_providers.py` (Already fixed in previous session)
```python
# Singleton pattern - one persistent service instance
_ai_provider_service_instance: Optional[AIProviderService] = None

def get_ai_provider_service() -> AIProviderService:
    """Dependency to get the AI provider service instance (singleton)."""
    global _ai_provider_service_instance
    if _ai_provider_service_instance is None:
        _ai_provider_service_instance = AIProviderService()
    return _ai_provider_service_instance
```

---

## How The Fix Works

### Scenario: Update API Key

```
1. Frontend sends: PUT /api/ai-providers/{id}
   - New key: "sk-your-new-key-xyz"

2. Backend dependency injection:
   - get_ai_provider_service()
   - Gets SINGLETON instance ✓
   - Instance has: self.env_file_path = c:\pf\AI-Chat-Assistant\.env

3. Service updates provider:
   - Updates in-memory cache ✓
   - Calls _save_provider()

4. _save_provider():
   - Saves JSON (without api_key) ✓
   - Calls _save_api_key_to_env()

5. _save_api_key_to_env():
   - Uses: self.env_file_path (absolute path)
   - NOT: Path('.env') (relative, unreliable)
   - Calls: set_key(c:\pf\AI-Chat-Assistant\.env, 'PROVIDER_API_KEY_OPENAI', 'sk-your-new-key-xyz')
   - Updates .env file ✓

6. Success:
   - .env now contains: PROVIDER_API_KEY_OPENAI='sk-your-new-key-xyz' ✓
   - JSON file has no key (secure) ✓
   - Key in memory for API calls ✓
```

---

## Verification

### Tests Created & Passing ✅
```
✅ test_api_key_saved_to_env_on_update
   - Creates provider
   - Updates API key
   - Verifies saved to .env
   - Verifies NOT in JSON
   - Verifies multiple updates work

✅ test_multiple_providers_keys_independent
   - Creates two providers
   - Updates one
   - Verifies both .env entries correct
   - Verifies independence

✅ test_update_requirements_api (10 tests)
   - All API endpoints work

✅ test_update_requirements_backend (14 tests)
   - All backend services work

─────────────────────────────────
TOTAL: 26/26 tests passing ✅
```

---

## Why This Works Now

| Component | Before | After |
|-----------|--------|-------|
| **Service Instance** | New per request ❌ | Singleton ✅ |
| **.env Path** | Relative (unreliable) ❌ | Absolute (reliable) ✅ |
| **Cache Persistence** | Lost after request ❌ | Persists ✅ |
| **Update Flow** | Broken ❌ | Works ✅ |
| **Working Directory Independent** | NO (depends on cwd) ❌ | YES (absolute path) ✅ |

---

## To Test The Fix

### 1. Restart your backend server
The singleton needs to be recreated to get the new absolute path logic:

```bash
# Stop the running backend (Ctrl+C)
# Then restart it:
cd c:\pf\AI-Chat-Assistant
python -m uvicorn backend.main:app --reload
```

### 2. Update a provider's API key via UI
- Go to **Settings > Providers**
- Select a provider to edit
- Update the API key field
- Click **Save**

### 3. Check the `.env` file
```bash
# Should contain:
PROVIDER_API_KEY_OPENAI='sk-your-new-key-here'
```

### 4. Or test via API
```bash
# Create provider
curl -X POST http://localhost:8000/api/ai-providers/ \
  -H "Content-Type: application/json" \
  -d '{"name":"OpenAI","provider_type":"openai","api_key":"sk-test-123"}'

# Update it (replace {ID} with response id)
curl -X PUT http://localhost:8000/api/ai-providers/{ID} \
  -H "Content-Type: application/json" \
  -d '{"api_key":"sk-updated-456"}'

# Verify .env
grep PROVIDER_API_KEY .env
# Should show: PROVIDER_API_KEY_OPENAI='sk-updated-456'
```

---

## Path Resolution Logic

```python
# In __init__:
self.project_root = Path(__file__).parent.parent.parent
self.env_file_path = self.project_root / ".env"

# Path resolution:
# __file__ = c:\pf\AI-Chat-Assistant\backend\services\ai_provider_service.py
# .parent = c:\pf\AI-Chat-Assistant\backend\services\
# .parent = c:\pf\AI-Chat-Assistant\backend\
# .parent = c:\pf\AI-Chat-Assistant\  ← project_root
# .env = c:\pf\AI-Chat-Assistant\.env ✓
```

This works **regardless of where you start the server from**!

---

## Files Modified

1. **backend/services/ai_provider_service.py**
   - Added `self.project_root` and `self.env_file_path` in `__init__`
   - Updated `_save_api_key_to_env()` to use `self.env_file_path`
   - Updated `_load_api_key_from_env()` to use `self.env_file_path`

2. **backend/api/ai_providers.py** (from previous fix)
   - Implemented singleton pattern

3. **tests/test_api_key_update_fix.py** (created)
   - 2 comprehensive tests

---

## Security Status

✅ **All security measures intact:**
- API keys NOT stored in JSON files
- API keys stored securely in .env file
- Keys excluded from API responses
- Keys in environment variables only

✅ **No breaking changes**
✅ **Backward compatible**
✅ **Works from any working directory**

---

## Summary

**The fix addresses TWO issues:**
1. ✅ Singleton pattern for persistent service instance
2. ✅ Absolute path to .env file regardless of working directory

**Result:** API key updates now reliably save to .env file from any location.

**Status:** ✅ **COMPLETE AND TESTED**
