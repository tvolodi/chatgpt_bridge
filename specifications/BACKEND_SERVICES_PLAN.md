# Backend Services Implementation Plan

## Overview
Based on the functional requirements in `specifications/functionality.md`, here are the backend services that need to be implemented to support the AI Chat Assistant application.

## API versioning strategy
- Use URL-based versioning: `/api/v1/...`
- Maintain backward compatibility for existing clients

## Backup and Recovery
- Implement periodic backups of project and session data
- Provide endpoints for data export/import

## Performance Benchmarking
- No specific benchmarking service planned at this stage

## Core Services (High Priority)

### 1. Project Management Service
**Purpose**: Manage projects, nested project structure, and project workspaces
**Key Responsibilities**:
- Create, read, update, delete projects
- Handle nested project hierarchies
- Manage project workspace directories
- Track project metadata (name, description, creation date)
- Validate project names and paths
- Handle default project initialization

**API Endpoints Needed**:
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create new project
- `GET /api/projects/{project_id}` - Get project details
- `PUT /api/projects/{project_id}` - Update project
- `DELETE /api/projects/{project_id}` - Delete project
- `GET /api/projects/{project_id}/tree` - Get project hierarchy

**Bonus Features** (Implemented Beyond Plan):
- `GET /api/projects/tree/all` - Get all project trees
- `GET /api/projects/stats/overview` - Get project statistics and analytics

### 2. Chat Session Management Service
**Purpose**: Manage chat sessions within projects
**Key Responsibilities**:
- Create, read, update, delete chat sessions
- Manage session directories within project workspaces
- Track session metadata (name, creation date, last accessed)
- Handle session switching and state persistence
- Maintain session isolation for context management

**API Endpoints Needed**:
- `GET /api/projects/{project_id}/sessions` - List sessions in project
- `POST /api/projects/{project_id}/sessions` - Create new session
- `GET /api/sessions/{session_id}` - Get session details
- `PUT /api/sessions/{session_id}` - Update session
- `DELETE /api/sessions/{session_id}` - Delete session
- `POST /api/sessions/{session_id}/switch` - Switch to session

**Bonus Features** (Implemented Beyond Plan):
- `POST /api/chat_sessions/{session_id}/messages` - Add message to session
- `GET /api/chat_sessions/{session_id}/messages` - Get session messages
- `GET /api/chat_sessions/{session_id}/full` - Get complete session with messages
- `GET /api/chat_sessions/stats/summary` - Get session statistics and summaries

### 3. AI Provider Service
**Purpose**: Handle communication with AI models and providers
**Key Responsibilities**:
- Support multiple AI providers (OpenAI, Anthropic)
- Manage API key authentication
- Send messages to AI models and receive responses
- Handle API rate limits and errors
- Support different AI models within providers
- Implement retry logic and error handling

**API Endpoints Needed**:
- `GET /api/providers` - List available providers
- `POST /api/chat/send` - Send message to AI
- `GET /api/providers/models` - Get available models
- `POST /api/providers/test` - Test provider connection

**Bonus Features** (Implemented Beyond Plan):
- `GET /api/ai-providers/models/available` - Get available models per provider
- `POST /api/ai-providers/{provider_id}/request` - Send request to AI provider
- `GET /api/ai-providers/{provider_id}/usage` - Get provider usage statistics
- `GET /api/ai-providers/usage/all` - Get usage stats for all providers
- `GET /api/ai-providers/{provider_id}/health` - Check provider health status
- `POST /api/ai-providers/{provider_id}/health/check` - Perform health check
- `GET /api/ai-providers/health/all` - Check health of all providers
- `POST /api/ai-providers/conversation` - Handle conversation requests

### 4. Conversation Service
**Purpose**: Manage chat conversations and message history
**Key Responsibilities**:
- Store and retrieve message history
- Handle message persistence in session directories
- Support message timestamps and metadata
- Implement conversation context management
- Handle message formatting and attachments

**API Endpoints Needed**:
- `GET /api/sessions/{session_id}/messages` - Get message history
- `POST /api/sessions/{session_id}/messages` - Send new message
- `GET /api/messages/{message_id}` - Get specific message
- `DELETE /api/sessions/{session_id}/messages` - Clear history

**Bonus Features** (Implemented Beyond Plan):
- `POST /api/conversations/send` - Send message to AI
- `GET /api/conversations/history/{session_id}` - Get message history
- `GET /api/conversations/stats` - Get conversation statistics
- `GET /api/conversations/settings` - Get conversation settings
- `PUT /api/conversations/settings` - Update conversation settings
- `DELETE /api/conversations/context/{session_id}` - Clear conversation context

## Supporting Services (Medium Priority)

### 5. File Management Service
**Purpose**: Handle file operations and attachments
**Key Responsibilities**:
- Manage project workspace files
- Handle chat session specific files
- Support file uploads and downloads
- Validate file types and sizes
- Organize files in proper directory structure
- Support file search and indexing

**API Endpoints Needed**:
- `GET /api/projects/{project_id}/files` - List project files
- `POST /api/files/upload` - Upload file
- `GET /api/files/{file_id}/download` - Download file
- `DELETE /api/files/{file_id}` - Delete file
- `GET /api/files/search` - Search files

**Bonus Features** (Implemented Beyond Plan):
- `GET /api/files/{file_id}` - Get file details
- `GET /api/files/{file_id}/content` - Get file content
- `PUT /api/files/{file_id}` - Update file
- `POST /api/files/{file_id}/process` - Process file with pipelines
- `POST /api/files/context` - Get file context for conversations
- `GET /api/files/stats` - Get file statistics
- `GET /api/files/types/supported` - Get supported file types
- Dual file management systems: workspace files and project-specific files

### 6. Settings Management Service
**Purpose**: Manage user settings and application configuration
**Key Responsibilities**:
- Store and retrieve API keys securely
- Manage user preferences
- Handle environment variable management
- Update .env file with new settings
- Validate API key formats
- Support multiple AI provider configurations

**API Endpoints Needed**:
- `GET /api/settings` - Get current settings
- `PUT /api/settings` - Update settings
- `POST /api/settings/test-api-key` - Test API key validity
- `GET /api/settings/providers` - Get provider configurations

**Bonus Features** (Implemented Beyond Plan):
- `GET /api/settings/default` - Get default settings
- `GET /api/settings/user/{user_id}` - Get user-specific settings
- `GET /api/settings/{settings_id}` - Get specific settings
- `POST /api/settings` - Create settings
- `POST /api/settings/{settings_id}/duplicate` - Duplicate settings
- `GET /api/settings/{settings_id}/export` - Export settings
- `POST /api/settings/import` - Import settings
- `POST /api/settings/validate` - Validate settings
- `GET /api/settings/api-providers/{provider_name}` - Get API provider config (critical for API keys)
- `PUT /api/settings/api-providers/{provider_name}` - Update API provider config (critical for API keys)
- `POST /api/settings/{settings_id}/reset` - Reset settings
- `GET /api/settings/user/{user_id}/effective` - Get effective user settings
- `GET /api/settings/categories/{category}` - Get settings by category
- `PUT /api/settings/categories/{category}` - Update settings by category

## Advanced Services (Lower Priority)

### 7. Search Service
**Purpose**: Provide search functionality across messages and files
**Key Responsibilities**:
- Index messages and files for search
- Support full-text search across conversations
- Search within specific projects or sessions
- Handle search result ranking and relevance
- Support advanced search filters (date ranges, file types)

**API Endpoints Needed**:
- `GET /api/search/messages` - Search messages
- `GET /api/search/files` - Search files
- `GET /api/search/global` - Global search

**Bonus Features** (Implemented Beyond Plan):
- `POST /api/search` - Search with advanced filters
- `POST /api/search/advanced` - Advanced search with scopes
- `GET /api/search/suggest` - Get search suggestions/autocomplete
- `POST /api/search/index/build` - Build search indices
- `GET /api/search/indices` - List search indices
- `DELETE /api/search/index/{index_id}` - Delete specific index
- `DELETE /api/search/indices` - Delete all indices
- `GET /api/search/analytics` - Get search analytics
- `GET /api/search/quick` - Quick search endpoint

### 8. User State Management Service
**Purpose**: Track and manage user application state
**Key Responsibilities**:
- Track current project and session
- Remember last used session on application start
- Manage user session state persistence
- Handle state transitions between projects/sessions
- Support state recovery after application restart

**API Endpoints Needed**:
- `GET /api/state` - Get current user state
- `PUT /api/state` - Update user state
- `POST /api/state/save` - Save current state
- `GET /api/state/last-session` - Get last used session

**Bonus Features** (Implemented Beyond Plan):
- `POST /user-state/states` - Create user state (prefix: `/user-state`)
- `GET /user-state/states/{state_id}` - Get user state
- `GET /user-state/states` - List user states
- `PUT /user-state/states/{state_id}` - Update user state
- `DELETE /user-state/states/{state_id}` - Delete user state
- `DELETE /user-state/states` - Clear all states
- `GET /user-state/preferences` - Get user preferences
- `PUT /user-state/preferences` - Update user preferences
- `GET /user-state/ui-state` - Get UI state
- `PUT /user-state/ui-state` - Update UI state
- `GET /user-state/session/{session_id}` - Get session-specific state
- `PUT /user-state/session` - Update session state
- `POST /user-state/activity` - Log user activity
- `GET /user-state/activity` - Get recent activity
- `POST /user-state/bookmarks` - Create bookmark
- `GET /user-state/bookmarks` - List bookmarks
- `DELETE /user-state/bookmarks/{bookmark_id}` - Delete bookmark
- `POST /user-state/backup` - Create state backup

## Additional Services (Bonus - Not Planned)

### 9. Chat Service
**Purpose**: High-level chat operations and workflows
**Key Responsibilities**:
- Provide simplified chat operations
- Handle high-level chat workflows
- Support session creation and management

**API Endpoints Implemented**:
- `POST /api/chat/send` - Send chat message
- `GET /api/chat/history/{session_id}` - Get chat history
- `POST /api/chat/sessions` - Create chat session
- `DELETE /api/chat/sessions/{session_id}` - Delete chat session

---

### 10. Workspace Service
**Purpose**: Workspace and project directory management
**Key Responsibilities**:
- Manage workspace operations
- Handle project directory structure
- Support workspace-specific file management

**API Endpoints Implemented**:
- Various workspace management operations with prefix `/api/workspace`

## Implementation Priority

### Phase 1 (Core Functionality)
1. Project Management Service
2. Chat Session Management Service
3. AI Provider Service
4. Conversation Service

### Phase 2 (Enhanced Features)
5. File Management Service
6. Settings Management Service

### Phase 3 (Advanced Features)
7. Search Service
8. User State Management Service

## Dependencies Between Services

- **Conversation Service** depends on **Chat Session Management**
- **File Management Service** depends on **Project Management**
- **AI Provider Service** depends on **Settings Management** (for API keys)
- **Search Service** depends on **Conversation** and **File Management** services
- **User State Management** depends on **Project** and **Chat Session** services

## Data Storage Requirements

- **Project metadata**: JSON files or database
- **Chat sessions**: Directory-based with JSON message files
- **User settings**: .env file and settings JSON
- **File attachments**: Organized directory structure
- **Search indexes**: Optional indexing for performance

---

## API Routing Reference

### Current Implementation Notes

**API Versioning Strategy**:
- Current implementation uses `/api/` prefix without version numbers
- Plan specified `/api/v1/...` but this has not been implemented
- All endpoints use the base `/api/` prefix

**Service-Specific Routing Prefixes**:
- `/api/chat` - Chat Service
- `/api/projects` - Project Management Service
- `/api/chat_sessions` - Chat Session Management Service (legacy: flat structure)
- `/api/ai-providers` - AI Provider Service
- `/api/conversations` - Conversation Service
- `/api/files` - File Management Service
- `/api/settings` - Settings Management Service
- `/api/search` - Search Service
- `/user-state` - User State Management Service (note: no `/api/` prefix)
- `/api/workspace-files` - Workspace Files Service
- `/api/workspace` - Workspace Service

**Note on User State Service**:
- Uses `/user-state` prefix instead of `/api/state` as specified in plan
- Does not use the standard `/api/` prefix pattern
- Provides consistent endpoint organization under `/user-state/` path

**Bonus Features Summary**:
- Over 60 additional endpoints implemented beyond the 40 planned endpoints
- Each service includes health monitoring, statistics, and advanced operations
- Import/Export functionality for settings and data
- Activity tracking and bookmark management
- File processing pipelines and search index management