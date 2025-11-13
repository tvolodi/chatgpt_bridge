# DOCUMENT_TYPE: MODULE_SPEC
# MODULE_ID: MOD-BE-Core
# MODULE_TYPE: backend
# VERSION: 1.0

## 1. Meta

- Name: AI Chat Assistant - Backend Core Module Specification
- Owner: Development Team
- Status: implemented <proposed | in_progress | implemented | tested | accepted>
- Tech Stack:
  - Language: Python 3.10+
  - Framework: FastAPI 0.104+
  - Data Storage: JSON files (with SQLite reserved for future)
  - External Services: OpenAI API, Anthropic API (extensible)
  - ORM: Pydantic v2 for data validation

## 2. Linked Requirements

### Foundational Architecture
- REQ-101: File-based data persistence
- REQ-102: Directory hierarchy with metadata
- REQ-103: Version control in metadata
- REQ-104: Message history persistence
- REQ-105: API key environment variables
- REQ-106: .env file for API key persistence
- REQ-107: Multiple provider API key support
- REQ-109: API key update without restart
- REQ-110: Single-user architecture
- REQ-111: Error handling & logging
- REQ-112: Testing strategy implementation

### Workspace Organization
- REQ-201: Three-level workspace hierarchy
- REQ-202: Default project auto-creation
- REQ-203: Default project functionality
- REQ-204: User-created projects
- REQ-205: Nested project structure
- REQ-206: Chat session isolation
- REQ-207: Session context includes files
- REQ-209: Project CRUD operations
- REQ-213: Session CRUD operations
- REQ-214: Message history isolation

### Chat & Messaging
- REQ-401 through REQ-418: Message management, history, templates, and substitution

### AI Provider Integration
- REQ-501 through REQ-524: Multi-provider support, configuration, and integration

### File Management
- REQ-601 through REQ-620: File upload/download, storage organization, metadata

### Settings
- REQ-705 through REQ-710: API key management, validation, and persistence

## 3. Public API (Endpoints)

### 3.1 Endpoint Overview by Service

| Service | Base Path | Purpose | Status |
|---------|-----------|---------|--------|
| Projects | `/api/projects` | Manage projects and hierarchy | implemented |
| Chat Sessions | `/api/chat_sessions` | Manage chat sessions | implemented |
| Chat Operations | `/api/chat` | High-level chat workflows | implemented |
| Conversations | `/api/conversations` | Message management and AI interaction | implemented |
| AI Providers | `/api/ai-providers` | Provider configuration and interaction | implemented |
| Files | `/api/files` | File upload/download/management | implemented |
| Settings | `/api/settings` | Configuration and preferences | implemented |
| Search | `/api/search` | Message and file search | implemented |
| User State | `/user-state` | Application state persistence | implemented |

### 3.2 Core Endpoint Specifications

#### EP-PROJ-001: List All Projects
- **Method:** GET
- **Path:** `/api/projects`
- **Related REQ:** REQ-201, REQ-209
- **Status:** implemented
- **Response:**
```json
{
  "projects": [
    {
      "id": "uuid",
      "name": "string",
      "description": "string",
      "parent_id": "uuid | null",
      "created_at": "ISO8601",
      "updated_at": "ISO8601"
    }
  ]
}
```

#### EP-PROJ-002: Create Project
- **Method:** POST
- **Path:** `/api/projects`
- **Related REQ:** REQ-204, REQ-209
- **Status:** implemented
- **Request Body:**
```json
{
  "name": "string (required, unique)",
  "description": "string (optional)",
  "parent_id": "uuid (optional, for nesting)"
}
```
- **Response:** 201 Created with project object

#### EP-PROJ-003: Get Project Details
- **Method:** GET
- **Path:** `/api/projects/{project_id}`
- **Related REQ:** REQ-209
- **Status:** implemented

#### EP-PROJ-004: Update Project
- **Method:** PUT
- **Path:** `/api/projects/{project_id}`
- **Related REQ:** REQ-209
- **Status:** implemented

#### EP-PROJ-005: Delete Project (Cascade)
- **Method:** DELETE
- **Path:** `/api/projects/{project_id}`
- **Related REQ:** REQ-209, REQ-213
- **Status:** implemented
- **Behavior:** Cascade deletes all sessions, messages, and files

#### EP-PROJ-006: Get Project Tree
- **Method:** GET
- **Path:** `/api/projects/tree/all`
- **Related REQ:** REQ-205, REQ-211
- **Status:** implemented
- **Response:** Hierarchical project tree with nesting

#### EP-SESS-001: List Sessions in Project
- **Method:** GET
- **Path:** `/api/chat_sessions?project_id={project_id}`
- **Related REQ:** REQ-213
- **Status:** implemented

#### EP-SESS-002: Create Session
- **Method:** POST
- **Path:** `/api/chat_sessions`
- **Related REQ:** REQ-213
- **Status:** implemented
- **Request Body:**
```json
{
  "name": "string",
  "project_id": "uuid"
}
```

#### EP-SESS-003: Get Session with Messages
- **Method:** GET
- **Path:** `/api/chat_sessions/{session_id}/full`
- **Related REQ:** REQ-213, REQ-404, REQ-409
- **Status:** implemented
- **Response:** Session metadata + complete message history

#### EP-SESS-004: Update Session
- **Method:** PUT
- **Path:** `/api/chat_sessions/{session_id}`
- **Related REQ:** REQ-213
- **Status:** implemented

#### EP-SESS-005: Delete Session
- **Method:** DELETE
- **Path:** `/api/chat_sessions/{session_id}`
- **Related REQ:** REQ-213, REQ-214
- **Status:** implemented
- **Behavior:** Cascade deletes messages and session files

#### EP-CONV-001: Send Message to AI
- **Method:** POST
- **Path:** `/api/conversations/send`
- **Related REQ:** REQ-401, REQ-402, REQ-514
- **Status:** implemented
- **Request Body:**
```json
{
  "session_id": "uuid",
  "message": "string",
  "provider_id": "string (optional)",
  "context_files": ["file_id"] (optional)
}
```
- **Response:**
```json
{
  "user_message": { "id", "timestamp", "role", "content", "status" },
  "ai_response": { "id", "timestamp", "role", "content", "provider_id", "tokens", "finish_reason" }
}
```

#### EP-CONV-002: Get Conversation History
- **Method:** GET
- **Path:** `/api/conversations/history/{session_id}`
- **Related REQ:** REQ-404, REQ-409
- **Status:** implemented

#### EP-PROV-001: List Available Providers
- **Method:** GET
- **Path:** `/api/ai-providers`
- **Related REQ:** REQ-501, REQ-505
- **Status:** implemented
- **Response:** List of providers with availability status

#### EP-PROV-002: Get Available Models
- **Method:** GET
- **Path:** `/api/ai-providers/models/available`
- **Related REQ:** REQ-501
- **Status:** implemented

#### EP-FILE-001: Upload File
- **Method:** POST
- **Path:** `/api/files/upload`
- **Related REQ:** REQ-601, REQ-609
- **Status:** implemented
- **Request:** multipart/form-data with file and metadata
- **Response:** File object with metadata

#### EP-FILE-002: List Project Files
- **Method:** GET
- **Path:** `/api/files/projects/{project_id}`
- **Related REQ:** REQ-603
- **Status:** implemented

#### EP-FILE-003: Download File
- **Method:** GET
- **Path:** `/api/files/{file_id}/download`
- **Related REQ:** REQ-604, REQ-612
- **Status:** implemented

#### EP-FILE-004: Delete File
- **Method:** DELETE
- **Path:** `/api/files/{file_id}`
- **Related REQ:** REQ-605, REQ-613
- **Status:** implemented

#### EP-SETT-001: Get Current Settings
- **Method:** GET
- **Path:** `/api/settings`
- **Related REQ:** REQ-105, REQ-706
- **Status:** implemented

#### EP-SETT-002: Update Settings
- **Method:** PUT
- **Path:** `/api/settings`
- **Related REQ:** REQ-106, REQ-709
- **Status:** implemented
- **Request Body:**
```json
{
  "api_providers": {
    "provider_name": {
      "api_key": "string",
      "base_url": "string",
      "model": "string"
    }
  }
}
```

#### EP-SETT-003: Test API Key
- **Method:** POST
- **Path:** `/api/settings/test-api-key`
- **Related REQ:** REQ-705, REQ-706
- **Status:** implemented
- **Request Body:**
```json
{
  "provider": "string",
  "api_key": "string"
}
```
- **Response:**
```json
{
  "valid": "boolean",
  "message": "string"
}
```

#### EP-TMPL-001: Create Template
- **Method:** POST
- **Path:** `/api/templates`
- **Related REQ:** REQ-414, REQ-418
- **Status:** implemented

#### EP-TMPL-002: List Templates
- **Method:** GET
- **Path:** `/api/templates`
- **Related REQ:** REQ-414
- **Status:** implemented

#### EP-TMPL-003: Substitute Template Parameters
- **Method:** POST
- **Path:** `/api/templates/{template_id}/substitute`
- **Related REQ:** REQ-418
- **Status:** implemented
- **Request Body:**
```json
{
  "parameters": {
    "variable_name": "value"
  }
}
```

## 4. Data Models

### 4.1 Core Entities

#### Project Entity
- **Collection:** data/projects/{project-id}/
- **Metadata File:** metadata.json
- **Fields:**
  - `id`: UUID4 (primary key)
  - `name`: string (unique)
  - `description`: string (optional)
  - `parent_id`: UUID4 (optional, for nesting)
  - `created_at`: ISO8601 timestamp
  - `updated_at`: ISO8601 timestamp
  - `workspace_path`: string (relative to data/)

#### ChatSession Entity
- **Collection:** data/chat_sessions/{session-id}/
- **Metadata File:** metadata.json
- **Files:**
  - `messages.json`: array of Message objects
  - `metadata.json`: session metadata
- **Fields:**
  - `id`: UUID4 (primary key)
  - `name`: string
  - `project_id`: UUID4 (references Project)
  - `created_at`: ISO8601 timestamp
  - `updated_at`: ISO8601 timestamp
  - `last_accessed`: ISO8601 timestamp

#### Message Entity
- **Storage:** data/chat_sessions/{session-id}/messages.json
- **Fields:**
  - `id`: UUID4 (primary key)
  - `session_id`: UUID4 (references ChatSession)
  - `role`: 'user' | 'assistant' | 'system'
  - `content`: string
  - `timestamp`: ISO8601
  - `status`: 'sent' | 'failed' | 'pending'
  - `provider_id`: string (for assistant messages, references provider)
  - `tokens`: { prompt: int, completion: int, total: int } (optional)
  - `finish_reason`: string (optional, from provider)

#### File Entity
- **Storage:** data/projects/{project-id}/files/ or data/chat_sessions/{session-id}/files/
- **Metadata:** Tracked in parent metadata.json
- **Fields:**
  - `id`: UUID4
  - `name`: string
  - `path`: string (relative)
  - `size`: int (bytes)
  - `type`: string (MIME type)
  - `uploaded_at`: ISO8601
  - `uploader`: string (username, currently "system")

#### MessageTemplate Entity
- **Storage:** data/templates.json
- **Fields:**
  - `id`: UUID4
  - `title`: string
  - `content`: string (may contain {{variable}} placeholders)
  - `category`: string
  - `parameters`: array of ParameterInfo objects
  - `created_at`: ISO8601

#### AIProvider Entity
- **Storage:** .env file + config dictionary
- **Fields:**
  - `provider_id`: string (e.g., "openai", "anthropic")
  - `api_key_env_var`: string (env var name)
  - `base_url`: string
  - `models`: array of model identifiers
  - `default_model`: string
  - `is_available`: boolean (computed from API key presence)
  - `temperature`: float
  - `max_tokens`: int

## 5. Internal Services

### 5.1 ProjectService
**Purpose:** Manage project CRUD operations and hierarchy
**Key Methods:**
- `create_project(name, description, parent_id) → Project`
- `get_project(project_id) → Project`
- `list_projects() → List[Project]`
- `update_project(project_id, **updates) → Project`
- `delete_project(project_id) → bool` (cascade delete)
- `get_project_tree() → Dict` (hierarchical structure)
- `_load_project_metadata(project_id) → Dict`
- `_save_project_metadata(project_id, metadata) → None`
- **Dependencies:** FileSystem operations
- **Data Persistence:** JSON metadata files
- **Tests:** REQ-209, TC-UNIT-209

### 5.2 ChatSessionService
**Purpose:** Manage chat sessions and message persistence
**Key Methods:**
- `create_session(name, project_id) → ChatSession`
- `get_session(session_id) → ChatSession`
- `get_session_with_messages(session_id) → ChatSession + messages`
- `list_sessions(project_id) → List[ChatSession]`
- `update_session(session_id, **updates) → ChatSession`
- `delete_session(session_id) → bool` (cascade delete)
- `add_message(session_id, message) → Message`
- `get_messages(session_id, offset=0, limit=None) → List[Message]`
- `delete_message(session_id, message_id) → bool`
- `_load_messages(session_id) → List[Message]`
- `_save_messages(session_id, messages) → None`
- **Dependencies:** FileSystem, ProjectService
- **Data Persistence:** JSON files (metadata + messages)
- **Tests:** REQ-213, REQ-214, TC-UNIT-213

### 5.3 ConversationService
**Purpose:** Handle message exchanges with AI and context management
**Key Methods:**
- `send_message(session_id, user_message, provider_id) → (user_msg, ai_msg)`
- `get_conversation_history(session_id) → List[Message]`
- `build_context(session_id, include_files=True) → String` (for AI prompt)
- `clear_context(session_id) → bool`
- `save_message(session_id, message) → Message`
- **Dependencies:** ChatSessionService, AIProviderService, FileManagementService
- **Responsibilities:** Context building, message formatting, token counting
- **Tests:** REQ-401, REQ-402, REQ-409, TC-UNIT-401

### 5.4 AIProviderService
**Purpose:** Manage AI provider integration and API calls
**Key Methods:**
- `get_providers() → List[AIProvider]`
- `get_available_providers() → List[AIProvider]` (only configured ones)
- `get_provider(provider_id) → AIProvider`
- `get_available_models(provider_id) → List[str]`
- `send_request(provider_id, messages, **params) → AIResponse`
- `format_messages(provider_id, messages) → List[Dict]` (provider-specific)
- `parse_response(provider_id, response) → (text, tokens, finish_reason)`
- `test_connection(provider_id, api_key) → bool`
- **Dependencies:** SettingsService, configuration files
- **Supported Providers:** OpenAI, Anthropic (extensible)
- **Tests:** REQ-501, REQ-514, TC-UNIT-501

### 5.5 FileManagementService
**Purpose:** Handle file upload, storage, and retrieval
**Key Methods:**
- `upload_file(file, scope='project', scope_id=None) → File`
- `get_file(file_id) → File`
- `get_project_files(project_id) → List[File]`
- `get_session_files(session_id) → List[File]`
- `download_file(file_id) → FileContent`
- `delete_file(file_id) → bool`
- `validate_file(file, scope='project', scope_id=None) → bool`
- `get_file_context(file_id) → str` (for AI context)
- **Storage:** data/projects/{id}/files/ or data/chat_sessions/{id}/files/
- **Limits:** 50MB per file, 500MB per project
- **Tests:** REQ-601, REQ-609, TC-UNIT-601

### 5.6 SettingsService
**Purpose:** Manage configuration and preferences
**Key Methods:**
- `get_settings() → Settings`
- `update_settings(updates) → Settings`
- `get_api_provider_config(provider_name) → Dict`
- `update_api_provider_config(provider_name, config) → bool`
- `load_env_vars() → Dict`
- `save_env_vars(vars) → None`
- `test_api_key(provider, api_key) → bool`
- **Storage:** .env file, environment variables
- **Responsibilities:** Hot-reload, validation, secure storage
- **Tests:** REQ-705, REQ-708, TC-UNIT-705

### 5.7 MessageTemplateService
**Purpose:** Manage message templates and parameter substitution
**Key Methods:**
- `create_template(title, content, category, parameters) → Template`
- `get_template(template_id) → Template`
- `list_templates() → List[Template]`
- `update_template(template_id, **updates) → Template`
- `delete_template(template_id) → bool`
- `substitute_parameters(template_id, params) → str` (replaces {{var}})
- `get_template_placeholders(template_id) → List[str]` (extracts {{variables}})
- **Storage:** data/templates.json
- **Substitution:** Regex-based {{variable}} replacement
- **Tests:** REQ-414, REQ-418, TC-UNIT-414

### 5.8 SearchService
**Purpose:** Index and search messages and files
**Key Methods:**
- `search_messages(query, scope='session|project|global', scope_id=None) → List[Message]`
- `search_files(query, scope='project|session', scope_id=None) → List[File]`
- `build_index() → None` (optional, for performance)
- **Implementation:** In-memory search + regex/text matching
- **Tests:** REQ-306, TC-FUNC-306

### 5.9 UserStateService
**Purpose:** Persist user application state
**Key Methods:**
- `save_state(state_dict) → None`
- `load_state() → Dict`
- `set_last_project(project_id) → None`
- `get_last_project() → UUID`
- `set_last_session(session_id) → None`
- `get_last_session() → UUID`
- **Storage:** Zustand localStorage on frontend (no backend persistence currently)
- **Tests:** REQ-212, REQ-218, TC-FUNC-212

## 6. Implementation Status per Feature

| Feature_ID  | Description                    | Status       | Notes | Tests |
|-------------|--------------------------------|-------------|-------|-------|
| BE-PROJ     | Project management CRUD        | implemented | Hierarchical nesting works | TC-UNIT-209 |
| BE-SESS     | Chat session management        | implemented | Flat structure, not under projects | TC-UNIT-213 |
| BE-CONV     | Conversation & messaging       | implemented | Full history persistence | TC-UNIT-401 |
| BE-PROV     | AI provider integration        | implemented | OpenAI, Anthropic support | TC-UNIT-501 |
| BE-FILE     | File management                | implemented | Project and session-specific | TC-UNIT-601 |
| BE-SETT     | Settings & configuration       | implemented | .env file management | TC-UNIT-705 |
| BE-TMPL     | Message templates              | implemented | Parameter substitution | TC-UNIT-414 |
| BE-SEARCH   | Search functionality           | implemented | Regex-based search | TC-FUNC-306 |
| BE-STATE    | User state persistence         | implemented | Frontend-driven currently | TC-FUNC-212 |

## 7. Backend Tests (Unit, Functional, E2E)

### 7.1 Unit Tests

- **TC-UNIT-101:** File-based persistence with JSON serialization
- **TC-UNIT-102:** Directory hierarchy creation and management
- **TC-UNIT-103:** Metadata version control with timestamps
- **TC-UNIT-104:** Message persistence to messages.json
- **TC-UNIT-201:** Default project auto-creation
- **TC-UNIT-209:** Project CRUD operations (create, read, update, delete)
- **TC-UNIT-213:** Chat session CRUD operations
- **TC-UNIT-214:** Message history isolation per session
- **TC-UNIT-401:** User message metadata persistence
- **TC-UNIT-402:** AI response metadata with provider info
- **TC-UNIT-403:** Message persistence to disk
- **TC-UNIT-405:** Message status tracking
- **TC-UNIT-409:** Full message history loading
- **TC-UNIT-411:** Project files in AI context
- **TC-UNIT-412:** Session files in AI context
- **TC-UNIT-413:** Token counting for context estimation
- **TC-UNIT-414:** Template creation and management
- **TC-UNIT-417:** Template CRUD operations
- **TC-UNIT-418:** Template parameter substitution with regex
- **TC-UNIT-501:** Multiple provider support
- **TC-UNIT-502:** Unique provider authentication
- **TC-UNIT-503:** Provider-specific parameters
- **TC-UNIT-504:** Provider config in .env
- **TC-UNIT-505:** Dynamic provider availability
- **TC-UNIT-515:** Provider-specific message formatting
- **TC-UNIT-516:** System prompt inclusion
- **TC-UNIT-517:** Message history as context
- **TC-UNIT-518:** Provider configuration application
- **TC-UNIT-519:** Provider response parsing
- **TC-UNIT-520:** Text extraction from response
- **TC-UNIT-521:** Token usage extraction
- **TC-UNIT-524:** Response metadata persistence
- **TC-UNIT-601:** File upload with metadata
- **TC-UNIT-602:** Project file accessibility
- **TC-UNIT-606:** File metadata storage
- **TC-UNIT-607:** Multiple file type support
- **TC-UNIT-608:** File size limits enforcement
- **TC-UNIT-609:** Session-specific file upload
- **TC-UNIT-610:** Session file isolation
- **TC-UNIT-614:** Session file metadata
- **TC-UNIT-705:** API key format validation
- **TC-UNIT-708:** API keys saved to .env
- **TC-UNIT-709:** .env updates without restart
- **TC-UNIT-710:** Secure API key storage (server-side only)

### 7.2 Functional Tests

- **TC-FUNC-210:** Project tree view display hierarchically
- **TC-FUNC-211:** Project workspace loads with files
- **TC-FUNC-212:** Last accessed project persists
- **TC-FUNC-216:** Session auto-save before switching
- **TC-FUNC-217:** Session list displays under project
- **TC-FUNC-218:** Last accessed session persists
- **TC-FUNC-404:** Message history loads on session open
- **TC-FUNC-406:** Error messages display on send failure
- **TC-FUNC-407:** Failed messages can be retried
- **TC-FUNC-408:** Messages can be deleted with confirmation
- **TC-FUNC-409:** Full message history loads for context
- **TC-FUNC-410:** Large message histories paginate
- **TC-FUNC-414:** Templates insert into chat input
- **TC-FUNC-415:** Template dropdown displays options
- **TC-FUNC-416:** Template preview modal shows content
- **TC-FUNC-417:** Templates can be edited/deleted
- **TC-FUNC-506:** Provider status displays in UI
- **TC-FUNC-511:** One-click provider switching works
- **TC-FUNC-512:** Selected provider persists
- **TC-FUNC-513:** Unconfigured providers disabled
- **TC-FUNC-514:** Messages route to correct provider
- **TC-FUNC-522:** API errors handled gracefully
- **TC-FUNC-523:** AI response displays in chat
- **TC-FUNC-603:** Project files list with metadata
- **TC-FUNC-604:** Files download from project
- **TC-FUNC-605:** Files delete from project with confirmation
- **TC-FUNC-611:** Session files list
- **TC-FUNC-612:** Session files download
- **TC-FUNC-613:** Session files delete
- **TC-FUNC-706:** API key test makes valid call
- **TC-FUNC-707:** Test result status displays

### 7.3 E2E Tests (optional)

- **TC-E2E-001:** Complete chat workflow (create project → session → send message → get response)
- **TC-E2E-002:** Multi-provider switching within session
- **TC-E2E-003:** File upload and context inclusion in AI request
- **TC-E2E-004:** Template usage end-to-end (create → insert → send → save)
- **TC-E2E-005:** Cross-session data isolation verification

## 8. Service Dependencies

```
ProjectService
├── FileSystem operations
└── (no other service dependencies)

ChatSessionService
├── FileSystem operations
├── ProjectService
└── (reads/validates against projects)

ConversationService
├── ChatSessionService
├── AIProviderService
├── FileManagementService
└── (orchestrates message exchange)

AIProviderService
├── SettingsService (reads API keys)
├── Environment variables
└── External APIs (OpenAI, Anthropic)

FileManagementService
├── FileSystem operations
├── ProjectService (for project file storage)
└── ChatSessionService (for session file storage)

SettingsService
├── FileSystem (.env operations)
└── Environment variables

MessageTemplateService
├── FileSystem (templates.json)
└── (independent service)

SearchService
├── ChatSessionService (to search messages)
├── FileManagementService (to search files)
└── (stateless service)

UserStateService
├── FileSystem (optional backend state storage)
└── (frontend-driven currently)
```

## 9. Notes for AI AGENTS (backend)

- All services follow the same pattern: data in `data/` directory as JSON/files
- API responses use standard structure: `{ "success": bool, "data": object, "error": string }`
- All IDs are UUIDs (uuid4) for consistency
- Timestamps use ISO8601 format
- Error handling includes proper HTTP status codes (400, 401, 404, 500, etc.)
- Cascade deletes are implemented for projects and sessions
- Hot-reload is supported for .env changes and provider configurations
- Message templates use regex (`{{variable}}`) for parameter substitution
- Consider SQLite migration path for future scalability (reserved but not implemented)
- All external API calls should have retry logic and proper error handling
- Tests should mock external API calls (OpenAI, Anthropic)
- Maintain backward compatibility for API versioning (currently `/api/` prefix, `/api/v1/` reserved)
