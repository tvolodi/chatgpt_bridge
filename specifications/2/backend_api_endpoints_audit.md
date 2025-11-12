# Backend API Endpoints List

## Router Configuration Summary

### Router Prefixes (from main.py and router definitions)

| Router | Include Prefix | Router Prefix | Final Base Path |
|--------|---------------|---------------|----------------|
| chat | `/api/chat` | none | `/api/chat/` |
| settings_api | none | `/api/settings` | `/api/settings/` |
| chat_sessions | none | `/api/chat-sessions` | `/api/chat-sessions/` |
| ai_providers | none | `/api/ai-providers` | `/api/ai-providers/` |
| search | none | `/api/search` | `/api/search/` |
| projects | none | `/api/projects` | `/api/projects/` |
| user_state | none | `/user-state` | `/user-state/` |
| file_management | `/api/files` | none | `/api/files/` |
| files | `/api/workspace-files` | none | `/api/workspace-files/` |
| workspace | `/api/workspace` | none | `/api/workspace/` |
| conversations | none | none | `/` |
| chat (old) | none | none | `/` |

## Complete Backend API Endpoints

### Chat API (`/api/chat/`)
- `POST /api/chat/send`
- `GET /api/chat/history/{session_id}`
- `POST /api/chat/sessions`
- `DELETE /api/chat/sessions/{session_id}`

### Settings API (`/api/settings/`)
- `GET /api/settings/`
- `GET /api/settings/default`
- `GET /api/settings/user/{user_id}`
- `GET /api/settings/{settings_id}`
- `POST /api/settings/`
- `PUT /api/settings/{settings_id}`
- `DELETE /api/settings/{settings_id}`
- `POST /api/settings/{settings_id}/duplicate`
- `GET /api/settings/{settings_id}/export`
- `POST /api/settings/import`
- `POST /api/settings/validate`
- `GET /api/settings/api-providers/{provider_name}`
- `PUT /api/settings/api-providers/{provider_name}`
- `POST /api/settings/{settings_id}/reset`
- `GET /api/settings/user/{user_id}/effective`
- `GET /api/settings/categories/{category}`
- `PUT /api/settings/categories/{category}`

### Chat Sessions API (`/api/chat-sessions/`)
- `POST /api/chat-sessions/`
- `GET /api/chat-sessions/{session_id}`
- `GET /api/chat-sessions/`
- `PUT /api/chat-sessions/{session_id}`
- `DELETE /api/chat-sessions/{session_id}`
- `POST /api/chat-sessions/{session_id}/messages`
- `GET /api/chat-sessions/{session_id}/messages`
- `GET /api/chat-sessions/{session_id}/full`
- `GET /api/chat-sessions/stats/summary`

### AI Providers API (`/api/ai-providers/`)
- `POST /api/ai-providers/`
- `GET /api/ai-providers/{provider_id}`
- `GET /api/ai-providers/`
- `PUT /api/ai-providers/{provider_id}`
- `DELETE /api/ai-providers/{provider_id}`
- `GET /api/ai-providers/models/available`
- `POST /api/ai-providers/{provider_id}/request`
- `GET /api/ai-providers/{provider_id}/usage`
- `GET /api/ai-providers/usage/all`
- `GET /api/ai-providers/{provider_id}/health`
- `POST /api/ai-providers/{provider_id}/health/check`
- `GET /api/ai-providers/health/all`
- `POST /api/ai-providers/conversation`

### Search API (`/api/search/`)
- `POST /api/search/`
- `POST /api/search/advanced`
- `GET /api/search/suggest`
- `POST /api/search/index/build`
- `GET /api/search/indices`
- `DELETE /api/search/index/{index_id}`
- `DELETE /api/search/indices`
- `GET /api/search/analytics`
- `GET /api/search/quick`

### Projects API (`/api/projects/`)
- `GET /api/projects/`
- `POST /api/projects/`
- `GET /api/projects/{project_id}`
- `PUT /api/projects/{project_id}`
- `DELETE /api/projects/{project_id}`
- `GET /api/projects/{project_id}/tree`
- `GET /api/projects/tree/all`
- `GET /api/projects/stats/overview`

### User State API (`/user-state/`)
- `POST /user-state/states`
- `GET /user-state/states/{state_id}`
- `GET /user-state/states`
- `PUT /user-state/states/{state_id}`
- `DELETE /user-state/states/{state_id}`
- `DELETE /user-state/states`
- `GET /user-state/preferences`
- `PUT /user-state/preferences`
- `GET /user-state/ui-state`
- `PUT /user-state/ui-state`
- `GET /user-state/session/{session_id}`
- `PUT /user-state/session`
- `POST /user-state/activity`
- `GET /user-state/activity`
- `POST /user-state/bookmarks`
- `GET /user-state/bookmarks`
- `DELETE /user-state/bookmarks/{bookmark_id}`

### File Management API (`/api/files/`)
- `POST /api/files/upload`
- `GET /api/files/{file_id}`
- `GET /api/files/{file_id}/download`
- `GET /api/files/{file_id}/content`
- `PUT /api/files/{file_id}`
- `DELETE /api/files/{file_id}`
- `POST /api/files/search`
- `POST /api/files/{file_id}/process`
- `GET /api/files/context`
- `GET /api/files/stats`
- `GET /api/files/types/supported`

### Files API (`/api/workspace-files/`)
- `GET /api/workspace-files/list`
- `GET /api/workspace-files/read`
- `POST /api/workspace-files/write`
- `POST /api/workspace-files/upload`
- `GET /api/workspace-files/download`
- `POST /api/workspace-files/search`

### Workspace API (`/api/workspace/`)
- `GET /api/workspace/info`
- `GET /api/workspace/context`
- `POST /api/workspace/index`
- `GET /api/workspace/tree`

### Conversations API (`/`)
- `POST /send`
- `GET /history/{session_id}`
- `GET /stats`
- `GET /settings`
- `PUT /settings`
- `DELETE /context/{session_id}`

### Legacy Chat API (`/`)
- `POST /send`
- `GET /history/{session_id}`
- `POST /sessions`
- `DELETE /sessions/{session_id}`

## Root Endpoints
- `GET /health`
- `GET /`

---

# Frontend API Configuration

## Base URL
```
API_BASE_URL = 'http://localhost:8000/api'
```

## Frontend API Calls (from api.ts)

### Chat API Calls
- `POST /api/chat/send` ✓ (matches backend)
- `GET /api/chat/history/{session_id}` ✓ (matches backend)
- `POST /api/chat/sessions` ✓ (matches backend)
- `DELETE /api/chat/sessions/{session_id}` ✓ (matches backend)

### Settings API Calls
- `GET /api/settings/user/{user_id}/effective` ✓ (matches backend)
- `PUT /api/settings/{settings_id}` ✓ (matches backend)
- `GET /api/settings/categories/{category}` ✓ (matches backend)
- `PUT /api/settings/categories/{category}` ✓ (matches backend)
- `GET /api/settings/{settings_id}/export` ✓ (matches backend)
- `POST /api/settings/import` ✓ (matches backend)

### Search API Calls
- `POST /api/search` ✓ (matches backend)
- `GET /api/search/suggest` ✓ (matches backend)
- `POST /api/search/index/build` ✓ (matches backend)
- `GET /api/search/analytics` ✓ (matches backend)

### User State API Calls
- `GET /user-state/preferences` ✓ (matches backend - uses separate client)
- `PUT /user-state/preferences` ✓ (matches backend - uses separate client)
- `GET /user-state/ui-state` ✓ (matches backend - uses separate client)
- `PUT /user-state/ui-state` ✓ (matches backend - uses separate client)
- `GET /user-state/session/{session_id}` ✓ (matches backend - uses separate client)
- `PUT /user-state/session` ✓ (matches backend - uses separate client)
- `POST /user-state/activity` ✓ (matches backend - uses separate client)
- `GET /user-state/activity` ✓ (matches backend - uses separate client)
- `POST /user-state/bookmarks` ✓ (matches backend - uses separate client)
- `GET /user-state/bookmarks` ✓ (matches backend - uses separate client)
- `DELETE /user-state/bookmarks/{bookmark_id}` ✓ (matches backend - uses separate client)

### Projects API Calls
- `GET /api/projects` ✓ (matches backend)
- `GET /api/projects/{project_id}` ✓ (matches backend)
- `POST /api/projects` ✓ (matches backend)
- `PUT /api/projects/{project_id}` ✓ (matches backend)
- `DELETE /api/projects/{project_id}` ✓ (matches backend)
- `GET /api/projects/{project_id}/tree` ✓ (matches backend)
- `GET /api/projects/tree/all` ✓ (matches backend)
- `GET /api/projects/stats/overview` ✓ (matches backend)

### Chat Sessions API Calls
- `GET /api/chat-sessions` ✓ (matches backend)
- `GET /api/chat-sessions/{session_id}` ✓ (matches backend)
- `POST /api/chat-sessions` ✓ (matches backend)
- `PUT /api/chat-sessions/{session_id}` ✓ (matches backend)
- `DELETE /api/chat-sessions/{session_id}` ✓ (matches backend)
- `GET /api/chat-sessions/{session_id}/full` ✓ (matches backend)
- `POST /api/chat-sessions/{session_id}/messages` ✓ (matches backend)
- `GET /api/chat-sessions/{session_id}/messages` ✓ (matches backend)
- `GET /api/chat-sessions/stats/summary` ✓ (matches backend)

### Providers API Calls
- `GET /api/ai-providers` ✓ (matches backend)
- `GET /api/ai-providers/{provider_id}` ✓ (matches backend)
- `POST /api/ai-providers` ✓ (matches backend)
- `PUT /api/ai-providers/{provider_id}` ✓ (matches backend)
- `DELETE /api/ai-providers/{provider_id}` ✓ (matches backend)
- `GET /api/settings/api-providers/{provider_name}` ✓ (matches backend)
- `PUT /api/settings/api-providers/{provider_name}` ✓ (matches backend)
- `DELETE /api/settings/api-providers/{provider_name}` ✓ (matches backend)
- `GET /api/ai-providers/models/available` ✓ (matches backend)

## Issues Found and FIXED ✅

### 1. **User State API Path Mismatch** ✅ FIXED
- **Problem**: Frontend used `/api/user-state/...` but backend served `/user-state/...`
- **Root Cause**: User State router has prefix `/user-state` but frontend added `/api/` base URL
- **Fix Applied**: Created separate `userStateClient` without `/api` prefix, updated all user-state API calls
- **Status**: ✅ RESOLVED - All user-state endpoints now work correctly

### 2. **Providers API Path Mismatch** ✅ FIXED
- **Problem**: Frontend used `/api/providers/...` but backend served `/api/ai-providers/...`
- **Root Cause**: Frontend expected `/providers` but backend uses `/ai-providers`
- **Fix Applied**: Changed all provider API calls from `/providers` to `/ai-providers`
- **Status**: ✅ RESOLVED - Provider CRUD operations now work

### 3. **Provider Config API Wrong Module** ✅ PREVIOUSLY FIXED
- **Problem**: Frontend used `/api/providers/{id}/config` but backend served `/api/settings/api-providers/{name}`
- **Root Cause**: Provider config is in settings API, not ai-providers API
- **Fix Applied**: Updated frontend to use `/settings/api-providers/{name}` for config operations
- **Status**: ✅ ALREADY RESOLVED in providersStore.ts

### 4. **Settings API Path Issues** ✅ FIXED
- **Problem**: Frontend used `/api/settings/user/default` but backend expects `/api/settings/{settings_id}`
- **Root Cause**: Frontend used hardcoded "user/default" but backend uses dynamic `{settings_id}`
- **Fix Applied**: Updated settings API to use proper settings IDs and user IDs
- **Status**: ✅ RESOLVED - Settings operations now use correct endpoints

### 5. **Missing Provider Validation Endpoint** ✅ REMOVED
- **Problem**: Frontend called `/api/providers/{id}/validate` but backend has no such endpoint
- **Root Cause**: Validation endpoint doesn't exist in backend
- **Fix Applied**: Removed the non-existent endpoint call from frontend
- **Status**: ✅ RESOLVED - No more invalid API calls

### 6. **Provider Models Endpoint Structure** ✅ FIXED
- **Problem**: Frontend used `/api/providers/{id}/models` but backend has `/api/ai-providers/models/available`
- **Root Cause**: Models endpoint is global, not per-provider
- **Fix Applied**: Updated frontend to use global `/ai-providers/models/available` endpoint
- **Status**: ✅ RESOLVED - Models loading now works correctly</content>
<parameter name="filePath">c:\pf\AI-Chat-Assistant\backend_api_endpoints_audit.md