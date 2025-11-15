# Quick Reference: Detailed Specifications (REQ-501 through REQ-504)

**Version:** 1.0  
**Date:** November 15, 2025  
**Updated Requirements:** 4  

---

## New Detailed Specifications

### REQ-502: Unique API Endpoint and Authentication
**File:** `docs/detailed_specs/DETAILED_SPEC_REQ-502_APIEndpointAuth.md`  
**Registry Link:** `docs/01_requirements_registry.md` Line 112

**What's Documented:**
- How each AI provider gets its unique API endpoint URL
- How to handle authentication for different providers
- Configuration override system (.env takes precedence)
- Multi-region/multi-instance support (e.g., Azure)
- Hot-reload without application restart

**Key Components:**
- ProviderConfigService (backend)
- ProviderEndpointResolver (backend)
- Configuration API endpoints
- 8 sub-requirements with test strategy

**Implementation Services:**
```python
backend/services/provider_config_service.py
backend/services/provider_endpoint_resolver.py
```

---

### REQ-503: Provider-Specific Parameters
**File:** `docs/detailed_specs/DETAILED_SPEC_REQ-503_ProviderParameters.md`  
**Registry Link:** `docs/01_requirements_registry.md` Line 113

**What's Documented:**
- Which parameters each provider supports (temperature, max_tokens, etc.)
- How to configure parameters at different levels (global, project, session)
- Parameter validation and constraints
- UI for parameter configuration in Settings
- Parameter presets for quick setup
- Hierarchical override system

**Key Components:**
- ProviderParametersService (backend)
- ProviderParametersSettings component (frontend)
- ParameterInput component (frontend, reusable)
- 8 sub-requirements with test strategy

**Implementation Services:**
```python
backend/services/provider_parameters_service.py
```

**Implementation Components:**
```typescript
src/components/Settings/ProviderParametersSettings.tsx
src/components/Settings/ParameterInput.tsx
```

---

### REQ-504: Provider Configuration in .env
**File:** `docs/detailed_specs/DETAILED_SPEC_REQ-504_EnvStorage.md`  
**Registry Link:** `docs/01_requirements_registry.md` Line 114

**What's Documented:**
- How to set up the `.env` file at project root
- Where to put API keys (never in code!)
- How to override default endpoints
- How to configure parameters via .env
- Hot-reload and file watching
- Security: masking, validation, error handling
- Multi-environment support (dev/staging/prod)

**Key Components:**
- EnvConfigService (backend)
- .env file structure and format
- .env.example template
- 10 sub-requirements with test strategy

**Implementation Services:**
```python
backend/services/env_config_service.py
```

**Files to Create:**
```
.env                  (project root - DO NOT COMMIT)
.env.example          (project root - commit to git)
```

---

## Quick Navigation

### By File
| File | Location | Lines | Focus |
|------|----------|-------|-------|
| REQ-502 | detailed_specs/ | 434 | Endpoints & Auth |
| REQ-503 | detailed_specs/ | 404 | Parameters |
| REQ-504 | detailed_specs/ | 533 | .env Storage |

### By Implementation Layer
| Service | Requirements | Location |
|---------|--------------|----------|
| Backend Config | 502, 504 | backend/services/ |
| Backend Parameters | 503 | backend/services/ |
| Frontend Settings | 503 | src/components/Settings/ |

### By Function
| Function | Requirement | Key Section |
|----------|-------------|-------------|
| Load provider config | 502 | REQ-502-A |
| Override endpoints | 502 | REQ-502-D |
| Configure parameters | 503 | REQ-503-B |
| Store in .env | 504 | REQ-504-A |
| Validate at startup | 504 | REQ-504-I |
| Hot-reload | 504 | REQ-504-F |

---

## Key Concepts

### Configuration Hierarchy (REQ-503, REQ-504)
```
Global Defaults (provider default)
  ↓ Override
Project Settings (all sessions in project)
  ↓ Override
Session Settings (specific chat)
  ↓ Override
Request Override (this message only)
```

### API Key Environment Variables (REQ-502, REQ-504)
```
OPENAI_API_KEY           → OpenAI authentication
ANTHROPIC_API_KEY        → Anthropic authentication
AZURE_OPENAI_API_KEY     → Azure OpenAI authentication
OLLAMA_API_KEY           → (optional for local Ollama)
```

### Endpoint Override Pattern (REQ-502, REQ-504)
```
Default: providers_config.json
Override: {PROVIDER}_BASE_URL in .env
Example: OPENAI_BASE_URL=https://custom.endpoint.com/v1
```

### Parameter Override Pattern (REQ-503, REQ-504)
```
.env: OPENAI_TEMPERATURE=0.7
Settings: Can override to 0.5
Session: Can override to 0.3
Request: Applied at message time
```

---

## Implementation Checklist

### Backend Services to Create

- [ ] `ProviderConfigService`
  - [ ] `load_provider_config()` - Load from JSON
  - [ ] `resolve_provider_endpoint()` - Get URL with override
  - [ ] `validate_provider_config()` - Validate config
  - [ ] `get_api_key()` - Get from environment
  - [ ] `refresh_provider_availability()` - Update status

- [ ] `ProviderParametersService`
  - [ ] `get_parameter_schema()` - Get constraints
  - [ ] `validate_parameters()` - Validate values
  - [ ] `apply_parameters()` - Apply hierarchy
  - [ ] `save_preset()` - Save as preset
  - [ ] `apply_preset()` - Apply saved preset

- [ ] `EnvConfigService`
  - [ ] `load_env_file()` - Parse .env
  - [ ] `parse_env_line()` - Parse single line
  - [ ] `validate_env_variables()` - Validate all
  - [ ] `get_env_variable()` - Get with fallback
  - [ ] `watch_env_file()` - Monitor changes
  - [ ] `reload_env_variables()` - Reload from file

### Frontend Components to Create

- [ ] `ProviderParametersSettings`
  - [ ] Tabbed UI per provider
  - [ ] Dynamic control generation
  - [ ] Save/Reset buttons

- [ ] `ParameterInput` (reusable)
  - [ ] Slider for floats
  - [ ] Input for integers
  - [ ] Dropdown for enums
  - [ ] Validation feedback

### API Endpoints to Create

- [ ] `GET /api/ai-providers` - List all
- [ ] `GET /api/ai-providers/{id}/config` - Get config
- [ ] `POST /api/ai-providers/{id}/validate` - Validate
- [ ] `PUT /api/ai-providers/{id}/parameters` - Save params
- [ ] `POST /api/ai-providers/refresh` - Reload .env

### Configuration Files

- [ ] `backend/config/providers_config.json` - Provider metadata
- [ ] `.env` - User's API keys (not committed)
- [ ] `.env.example` - Template (committed)

### Tests to Create

- [ ] Unit tests for ProviderConfigService (12+ tests)
- [ ] Unit tests for ProviderParametersService (13+ tests)
- [ ] Unit tests for EnvConfigService (12+ tests)
- [ ] Integration tests for configuration loading
- [ ] Integration tests for hot-reload

---

## Important Security Notes

### Never Store Secrets in Code
- ❌ Do NOT hardcode API keys
- ❌ Do NOT commit .env file
- ✅ DO store in .env file
- ✅ DO load from environment variables

### Masking in Logs and UI
- Show only first 4 and last 4 characters
- Example: `sk-proj-****...****bcd1`
- Use masked versions in error messages

### Validation at Startup
- Check that required API keys are present
- Validate endpoint URLs are reachable
- Mark unavailable providers disabled

---

## Testing Strategy

### Unit Tests: 37+ Test Cases
- Parameter validation tests
- Configuration loading tests
- Environment variable tests
- Endpoint resolution tests
- API key handling tests

### Integration Tests
- End-to-end configuration loading
- Hot-reload on .env change
- Parameter hierarchy enforcement
- Provider availability checking

### Manual Testing
- Test each provider's endpoint
- Verify parameter effects
- Check UI displays correctly
- Validate error messages

---

## Cross-Reference Matrix

| REQ | Depends On | Enables |
|-----|-----------|---------|
| 502 | 105-109, 501 | 503, 504, 514 |
| 503 | 501, 502, 308 | 504, 518 |
| 504 | 105-109, 502 | 501, 503, 505 |

---

## Version History

| Date | Change | Author |
|------|--------|--------|
| 2025-11-15 | Initial creation | Doc Team |

---

## Questions or Issues?

Refer to the detailed specification files for comprehensive information:
- `docs/detailed_specs/DETAILED_SPEC_REQ-502_APIEndpointAuth.md`
- `docs/detailed_specs/DETAILED_SPEC_REQ-503_ProviderParameters.md`
- `docs/detailed_specs/DETAILED_SPEC_REQ-504_EnvStorage.md`

Check the registry for dependencies and relationships:
- `docs/01_requirements_registry.md`
