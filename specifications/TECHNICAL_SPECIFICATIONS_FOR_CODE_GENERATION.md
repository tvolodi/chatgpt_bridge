# 🔧 Technical Specifications for Code Generation

**Date:** November 11, 2025  
**Purpose:** Detailed technical specifications for AI code generation  
**Audience:** AI models, senior developers  
**Depth Level:** Implementation-ready

---

## Table of Contents

1. [Core Architecture Specifications](#1-core-architecture-specifications)
2. [Data Model & Schema](#2-data-model--schema)
3. [Frontend Component Specifications](#3-frontend-component-specifications)
4. [Backend Service Specifications](#4-backend-service-specifications)
5. [API Endpoint Specifications](#5-api-endpoint-specifications)
6. [State Management Specifications](#6-state-management-specifications)
7. [Database Schema & Operations](#7-database-schema--operations)
8. [File System Structure & Operations](#8-file-system-structure--operations)

---

## 1. Core Architecture Specifications

### 1.1 Application Bootstrap Flow

**Entry Point:** `frontend/src/main.tsx`
```typescript
// Initialize React application with Zustand stores
1. Create Zustand store instances
2. Initialize API client with base URL
3. Load user preferences from localStorage
4. Mount React application to DOM element #root
5. Set up error boundary wrapper
6. Initialize route manager
```

**Backend Entry Point:** `backend/main.py`
```python
# FastAPI application initialization
1. Create FastAPI application instance
2. Configure CORS middleware for http://localhost:3000
3. Load environment variables from .env
4. Initialize service instances
5. Register API routers (/api/chats, /api/projects, /api/files, /api/providers, /api/settings)
6. Start Uvicorn server on 0.0.0.0:8000
7. Serve API documentation on /docs
```

### 1.2 Directory Structure (Complete)

**Frontend Structure:**
```
frontend/
├── src/
│   ├── main.tsx                          # Entry point
│   ├── App.tsx                           # Root component with routing
│   ├── index.css                         # Global styles (Tailwind)
│   ├── components/
│   │   ├── Header.tsx                    # App header with logo, search, provider selector
│   │   ├── Sidebar.tsx                   # Project tree + session list navigation
│   │   ├── ChatArea.tsx                  # Message display area
│   │   ├── ChatMessage.tsx               # Individual message component (user/AI formatted)
│   │   ├── ChatInput.tsx                 # Message input field with multi-line, send button
│   │   ├── ProviderSelector.tsx          # Dropdown to select AI provider
│   │   ├── ProjectTree.tsx               # Hierarchical project list
│   │   ├── SessionList.tsx               # Sessions within current project
│   │   ├── ErrorBoundary.tsx             # Error handling wrapper
│   │   ├── LoadingSpinner.tsx            # Loading indicator
│   │   └── Toast.tsx                     # Notification system
│   ├── pages/
│   │   ├── ChatPage.tsx                  # Main chat interface
│   │   ├── SettingsPage.tsx              # Settings & API key configuration
│   │   ├── ProjectsPage.tsx              # Project management page
│   │   ├── ProviderManagementPage.tsx    # Manage AI providers
│   │   └── NotFoundPage.tsx              # 404 page
│   ├── services/
│   │   ├── api.ts                        # Axios API client instance
│   │   ├── chatService.ts                # Chat-related API calls
│   │   ├── projectService.ts             # Project-related API calls
│   │   ├── fileService.ts                # File-related API calls
│   │   ├── providerService.ts            # Provider-related API calls
│   │   └── settingsService.ts            # Settings API calls
│   ├── stores/
│   │   ├── chatStore.ts                  # Zustand: chat sessions, messages, UI state
│   │   ├── projectStore.ts               # Zustand: projects, current project
│   │   ├── uiStore.ts                    # Zustand: sidebar state, theme
│   │   ├── providersStore.ts             # Zustand: available providers, current provider
│   │   └── settingsStore.ts              # Zustand: user settings, API keys
│   ├── hooks/
│   │   ├── useChat.ts                    # Chat operations hook
│   │   ├── useProject.ts                 # Project operations hook
│   │   ├── useProviders.ts               # Provider operations hook
│   │   ├── useSettings.ts                # Settings operations hook
│   │   └── useLocalStorage.ts            # LocalStorage persistence hook
│   ├── types/
│   │   ├── index.ts                      # Type definitions
│   │   ├── chat.ts                       # Chat-related types
│   │   ├── project.ts                    # Project-related types
│   │   ├── provider.ts                   # Provider-related types
│   │   └── api.ts                        # API response types
│   ├── utils/
│   │   ├── formatters.ts                 # Format dates, text, etc.
│   │   ├── validators.ts                 # Input validation
│   │   └── errorHandler.ts               # Error handling utilities
│   └── test/
│       ├── components/                   # Component tests (350+ tests)
│       ├── pages/                        # Page tests
│       └── e2e/                          # End-to-end tests
├── public/
│   ├── index.html
│   └── favicon.ico
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── vitest.config.ts

Backend Structure:
backend/
├── main.py                               # Entry point, ASGI server setup
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── chat.py                           # Chat session endpoints
│   ├── projects.py                       # Project management endpoints
│   ├── files.py                          # File management endpoints
│   ├── providers.py                      # Provider configuration endpoints
│   └── settings.py                       # Settings endpoints
├── services/
│   ├── __init__.py
│   ├── chat_session_service.py           # ChatSessionService (core logic)
│   ├── conversation_service.py           # ConversationService (message handling)
│   ├── project_service.py                # ProjectService (project CRUD)
│   ├── file_management_service.py        # FileManagementService (file ops)
│   ├── ai_provider_service.py            # AIProviderService (provider API calls)
│   ├── settings_service.py               # SettingsService (settings CRUD)
│   ├── search_service.py                 # SearchService (search functionality)
│   └── user_state_service.py             # UserStateService (user state persistence)
├── models/
│   ├── __init__.py
│   ├── chat_session.py                   # ChatSession, Message, ChatSessionCreate models
│   ├── project.py                        # Project, ProjectCreate models
│   ├── file.py                           # FileMetadata, FileCreate models
│   ├── provider.py                       # Provider, ProviderConfig models
│   └── settings.py                       # Settings, UserSettings models
├── config/
│   ├── __init__.py
│   └── settings.py                       # Configuration management (env vars, defaults)
├── utils/
│   ├── __init__.py
│   ├── validators.py                     # Input validation
│   └── error_handlers.py                 # Error handling utilities
└── tests/                                # Unit & integration tests (250+ tests)
```

---

## 2. Data Model & Schema

### 2.1 Core Data Types (TypeScript)

```typescript
// Types are in frontend/src/types/

// ========== CHAT SESSION TYPES ==========
interface ChatSession {
  id: string;                              // UUID
  projectId: string;                       // UUID of parent project
  title: string;                           // Session name (max 255 chars)
  description?: string;                    // Optional description
  createdAt: ISO8601DateTime;              // Creation timestamp
  updatedAt: ISO8601DateTime;              // Last modification
  messagesCount: number;                   // Count of messages
  tags: string[];                          // For categorization
  isArchived: boolean;                     // Soft delete flag
  metadata: Record<string, any>;           // Flexible metadata storage
}

interface Message {
  id: string;                              // UUID
  sessionId: string;                       // Parent session UUID
  content: string;                         // Message text (no length limit)
  role: 'user' | 'assistant';              // Message sender type
  timestamp: ISO8601DateTime;              // When message was created
  tokens?: number;                         // For API tracking
  providerId?: string;                     // Which provider responded (if assistant)
  status: 'sent' | 'failed' | 'pending';   // Message delivery status
  metadata: Record<string, any>;           // Flexible metadata
}

interface ChatSessionCreate {
  projectId: string;
  title: string;
  description?: string;
  metadata?: Record<string, any>;
}

interface ChatSessionUpdate {
  title?: string;
  description?: string;
  metadata?: Record<string, any>;
}

interface ChatSessionWithMessages extends ChatSession {
  messages: Message[];                     // All messages in session
}

// ========== PROJECT TYPES ==========
interface Project {
  id: string;                              // UUID
  parentProjectId?: string;                // UUID for nested projects
  name: string;                            // Project name (max 255 chars)
  description?: string;                    // Optional description
  createdAt: ISO8601DateTime;
  updatedAt: ISO8601DateTime;
  childProjectIds: string[];               // Sub-project IDs
  sessions: ChatSession[];                 // Sessions in this project
  filesCount: number;                      // Number of project files
  isDefault: boolean;                      // Is this the default project?
  metadata: Record<string, any>;
}

interface ProjectCreate {
  name: string;
  description?: string;
  parentProjectId?: string;
  metadata?: Record<string, any>;
}

interface ProjectUpdate {
  name?: string;
  description?: string;
  metadata?: Record<string, any>;
}

// ========== FILE TYPES ==========
interface FileMetadata {
  id: string;                              // UUID
  projectId: string;                       // Can be project-level or session-level
  sessionId?: string;                      // Optional session association
  fileName: string;                        // Original filename
  filePath: string;                        // Full file system path
  fileSize: number;                        // In bytes
  mimeType: string;                        // e.g., 'text/plain', 'application/json'
  uploadedAt: ISO8601DateTime;
  updatedAt: ISO8601DateTime;
  tags: string[];
  metadata: Record<string, any>;
}

interface FileUploadRequest {
  projectId: string;
  sessionId?: string;
  file: File;                              // Actual file object from form
}

// ========== PROVIDER TYPES ==========
interface Provider {
  id: string;                              // UUID
  name: string;                            // 'openai', 'anthropic', etc. (max 50 chars)
  displayName: string;                     // 'OpenAI', 'Anthropic' (UI display)
  description: string;                     // Provider description
  baseURL: string;                         // API base URL
  apiKeyEnvVar: string;                    // Environment variable name (e.g., 'OPENAI_API_KEY')
  models: string[];                        // Available model IDs
  isAvailable: boolean;                    // API key configured and accessible?
  createdAt: ISO8601DateTime;
  updatedAt: ISO8601DateTime;
  config: ProviderConfig;
}

interface ProviderConfig {
  providerId: string;
  temperature?: number;                    // 0-1, default 0.7
  maxTokens?: number;                      // Default 2000
  topP?: number;                           // 0-1, nucleus sampling
  frequencyPenalty?: number;               // -2 to 2
  presencePenalty?: number;                // -2 to 2
  customSettings?: Record<string, any>;    // Provider-specific settings
}

interface ProviderRequest {
  providerId: string;
  messages: Message[];                     // All messages in context
  systemPrompt?: string;                   // Optional system message
  config?: Partial<ProviderConfig>;        // Override default config
}

interface ProviderResponse {
  id: string;                              // Response ID
  content: string;                         // Generated text
  tokens: {
    prompt: number;
    completion: number;
    total: number;
  };
  finishReason: 'stop' | 'length' | 'error';
  providerId: string;
}

// ========== SETTINGS TYPES ==========
interface UserSettings {
  userId: string;                          // User identifier (username or ID)
  theme: 'light' | 'dark' | 'auto';        // UI theme
  defaultProjectId: string;                // UUID of default project
  defaultProviderId: string;               // UUID of default provider
  autoSaveInterval: number;                // In milliseconds, default 30000
  notificationsEnabled: boolean;
  apiKeys: Record<string, string>;         // Provider API keys (client-side temp storage)
  createdAt: ISO8601DateTime;
  updatedAt: ISO8601DateTime;
}

interface SettingsUpdate {
  theme?: 'light' | 'dark' | 'auto';
  defaultProjectId?: string;
  defaultProviderId?: string;
  autoSaveInterval?: number;
  notificationsEnabled?: boolean;
}

// ========== API ERROR TYPES ==========
interface ApiError {
  code: string;                            // Error code (e.g., 'VALIDATION_ERROR')
  message: string;                         // Human-readable message
  details?: Record<string, any>;           // Additional error details
  timestamp: ISO8601DateTime;
}

interface ValidationError extends ApiError {
  code: 'VALIDATION_ERROR';
  details: {
    field: string;
    error: string;
  }[];
}

interface NotFoundError extends ApiError {
  code: 'NOT_FOUND';
}

interface UnauthorizedError extends ApiError {
  code: 'UNAUTHORIZED';
}

interface ServerError extends ApiError {
  code: 'SERVER_ERROR';
}
```

### 2.2 Python Data Models (Pydantic)

```python
# backend/models/chat_session.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class MessageBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=100000)
    role: Literal['user', 'assistant']
    tokens: Optional[int] = None
    provider_id: Optional[str] = None
    status: Literal['sent', 'failed', 'pending'] = 'pending'
    metadata: dict = {}

class MessageCreate(MessageBase):
    session_id: UUID

class Message(MessageBase):
    id: UUID
    session_id: UUID
    timestamp: datetime
    
    class Config:
        from_attributes = True

class ChatSessionBase(BaseModel):
    project_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    metadata: dict = {}

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    metadata: Optional[dict] = None

class ChatSession(ChatSessionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    messages_count: int = 0
    tags: List[str] = []
    is_archived: bool = False
    
    class Config:
        from_attributes = True

class ChatSessionWithMessages(ChatSession):
    messages: List[Message] = []

# backend/models/project.py
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    parent_project_id: Optional[UUID] = None
    metadata: dict = {}

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    metadata: Optional[dict] = None

class Project(ProjectBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    child_project_ids: List[UUID] = []
    is_default: bool = False
    files_count: int = 0
    
    class Config:
        from_attributes = True

# backend/models/provider.py
class ProviderConfigBase(BaseModel):
    temperature: Optional[float] = Field(None, ge=0, le=1)
    max_tokens: Optional[int] = Field(None, ge=1, le=32000)
    top_p: Optional[float] = Field(None, ge=0, le=1)
    frequency_penalty: Optional[float] = Field(None, ge=-2, le=2)
    presence_penalty: Optional[float] = Field(None, ge=-2, le=2)
    custom_settings: Optional[dict] = {}

class ProviderConfig(ProviderConfigBase):
    provider_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProviderBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    description: str
    base_url: str = Field(..., min_length=10)
    api_key_env_var: str = Field(..., min_length=1, max_length=100)
    models: List[str] = []

class Provider(ProviderBase):
    id: UUID
    is_available: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProviderRequest(BaseModel):
    provider_id: UUID
    messages: List[Message]
    system_prompt: Optional[str] = None
    config: Optional[ProviderConfigBase] = None
```

---

## 3. Frontend Component Specifications

### 3.1 Header Component (Header.tsx)

**Purpose:** Application top bar with navigation, search, and provider selector

**Props:** None (connects to stores)

**State:**
```typescript
const searchQuery = ref('')                    // Search input text
const isSearchActive = ref(false)              // Search dropdown visible?
const currentProvider = useProvidersStore()    // Currently selected provider
const userSettings = useSettingsStore()        // User preferences
```

**Structure:**
```html
<header className="flex items-center justify-between p-4 border-b bg-white shadow-sm">
  <!-- Left section: Logo & Title -->
  <div className="flex items-center gap-4">
    <img src="/logo.svg" alt="Logo" className="w-8 h-8" />
    <h1 className="text-2xl font-bold">AI Chat Assistant</h1>
  </div>
  
  <!-- Center section: Search Bar -->
  <div className="flex-1 mx-8">
    <SearchBar 
      value={searchQuery}
      onChange={handleSearch}
      onActive={() => isSearchActive = true}
      placeholder="Search messages and files..."
    />
  </div>
  
  <!-- Right section: Provider Selector & Settings -->
  <div className="flex items-center gap-6">
    <ProviderSelector
      currentProvider={currentProvider}
      onProviderChange={handleProviderChange}
    />
    <SettingsButton onClick={() => navigate('/settings')} />
    <UserProfileDropdown />
  </div>
</header>
```

**Key Functions:**
- `handleSearch(query)`: Trigger search service, show results in dropdown
- `handleProviderChange(providerId)`: Update store, persist to localStorage
- Navigate to settings page on settings icon click

### 3.2 Sidebar Component (Sidebar.tsx)

**Purpose:** Navigation tree showing projects and chat sessions

**State:**
```typescript
const projects = useProjectStore((state) => state.projects)
const currentProject = useProjectStore((state) => state.currentProject)
const sessions = useChatStore((state) => state.sessions)
const expandedProjects = ref(new Set())
```

**Structure:**
```html
<aside className="w-64 border-r bg-gray-50 flex flex-col overflow-hidden">
  <!-- Project Tree Section -->
  <div className="flex-1 overflow-y-auto">
    <ProjectTree
      projects={projects}
      currentProject={currentProject}
      expandedProjects={expandedProjects}
      onProjectSelect={handleProjectSelect}
      onToggleExpand={handleToggleExpand}
    />
  </div>
  
  <!-- Session List Section -->
  {currentProject && (
    <div className="border-t p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-semibold">Sessions</h3>
        <button onClick={handleCreateSession} className="text-blue-500">
          + New
        </button>
      </div>
      <SessionList
        sessions={sessions.filter(s => s.projectId === currentProject.id)}
        onSessionSelect={handleSessionSelect}
        onDeleteSession={handleDeleteSession}
      />
    </div>
  )}
  
  <!-- New Project Button -->
  <div className="border-t p-4">
    <button 
      onClick={handleCreateProject}
      className="w-full px-4 py-2 bg-blue-500 text-white rounded"
    >
      + New Project
    </button>
  </div>
</aside>
```

**Key Functions:**
- `handleProjectSelect(projectId)`: Load project, fetch sessions, update store
- `handleSessionSelect(sessionId)`: Save current session, load new session messages
- `handleCreateSession()`: Show modal, create session in project
- `handleToggleExpand(projectId)`: Toggle nested projects visibility

### 3.3 ChatArea Component (ChatArea.tsx)

**Purpose:** Display message history in conversation format

**Props:**
```typescript
interface ChatAreaProps {
  sessionId: string
  messages: Message[]
  isLoading: boolean
  onSendMessage: (content: string) => void
}
```

**State:**
```typescript
const messages = useChatStore((state) => state.messages)
const isLoading = useChatStore((state) => state.isLoading)
const messagesEndRef = ref(null)
```

**Structure:**
```html
<div className="flex-1 flex flex-col bg-white">
  <!-- Messages Container -->
  <div className="flex-1 overflow-y-auto p-6 space-y-4">
    {messages.map(message => (
      <ChatMessage
        key={message.id}
        message={message}
        isUser={message.role === 'user'}
      />
    ))}
    {isLoading && <LoadingSpinner />}
    <div ref={messagesEndRef} />
  </div>
  
  <!-- Input Area -->
  <div className="border-t p-4 bg-gray-50">
    <ChatInput
      onSendMessage={handleSendMessage}
      disabled={isLoading}
      placeholder="Type your message (Shift+Enter for new line)..."
    />
  </div>
</div>
```

**Key Functions:**
- `handleSendMessage(content)`: Create message object, call API, update store
- Auto-scroll to bottom on new messages
- Show loading state while waiting for AI response

### 3.4 ChatMessage Component (ChatMessage.tsx)

**Purpose:** Individual message display with role-based formatting

**Props:**
```typescript
interface ChatMessageProps {
  message: Message
  isUser: boolean
}
```

**Render Logic:**
```typescript
<div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
  <div 
    className={`max-w-[70%] rounded-lg p-4 ${
      isUser 
        ? 'bg-blue-500 text-white rounded-br-none' 
        : 'bg-gray-200 text-black rounded-bl-none'
    }`}
  >
    <p className="whitespace-pre-wrap">{message.content}</p>
    <span className="text-xs mt-2 opacity-70">
      {formatTime(message.timestamp)}
    </span>
  </div>
</div>
```

### 3.5 ChatInput Component (ChatInput.tsx)

**Purpose:** User message input with multi-line support

**Props:**
```typescript
interface ChatInputProps {
  onSendMessage: (content: string) => void
  disabled?: boolean
  placeholder?: string
}
```

**State:**
```typescript
const inputValue = ref('')
const rowCount = ref(1)  // Dynamic height
```

**Key Features:**
- Multi-line text area (Shift+Enter for newline, Enter to send)
- Dynamic height based on content
- Auto-focus on mount
- Disable send button while loading
- Character counter (optional)

**Implementation:**
```typescript
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSendMessage()
  }
}

const handleSendMessage = () => {
  if (inputValue.value.trim()) {
    onSendMessage(inputValue.value)
    inputValue.value = ''
    rowCount.value = 1
  }
}
```

### 3.6 ProviderSelector Component (ProviderSelector.tsx)

**Purpose:** Dropdown to select AI provider

**Props:**
```typescript
interface ProviderSelectorProps {
  currentProvider: Provider
  onProviderChange: (providerId: string) => void
}
```

**State:**
```typescript
const providers = useProvidersStore((state) => state.providers)
const isDropdownOpen = ref(false)
```

**Render:**
```html
<div className="relative">
  <button 
    onClick={() => isDropdownOpen.value = !isDropdownOpen.value}
    className="px-4 py-2 bg-white border rounded flex items-center gap-2"
  >
    {currentProvider?.displayName || 'Select Provider'}
    <ChevronDown size={16} />
  </button>
  
  {isDropdownOpen.value && (
    <div className="absolute top-12 right-0 bg-white border rounded shadow-lg w-64 z-50">
      {providers.map(provider => (
        <div
          key={provider.id}
          onClick={() => handleProviderChange(provider.id)}
          className="p-4 border-b hover:bg-gray-50 cursor-pointer"
        >
          <div className="font-semibold">{provider.displayName}</div>
          <div className="text-sm text-gray-600">{provider.description}</div>
          <div className="text-xs text-gray-500 mt-1">
            {provider.models.length} models • {provider.isAvailable ? '✓ Configured' : '✗ Not configured'}
          </div>
          {provider.id === currentProvider?.id && <CheckIcon />}
        </div>
      ))}
    </div>
  )}
</div>
```

### 3.7 Settings Page (SettingsPage.tsx)

**Purpose:** Configure API keys and user preferences

**Sections:**
1. **API Key Management**
   - Input field for each provider's API key
   - Masked display (show only first 10 chars)
   - Test button to validate key
   - Save button (updates .env via API)

2. **User Preferences**
   - Theme selector (light/dark/auto)
   - Default project selector
   - Default provider selector
   - Auto-save interval slider

3. **Advanced Settings**
   - Data export button
   - Data import button
   - Reset to defaults button

---

## 4. Backend Service Specifications

### 4.1 ChatSessionService

**File:** `backend/services/chat_session_service.py`

**Methods:**

```python
class ChatSessionService:
    def __init__(self, data_dir: str = "data/chat_sessions"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    # ===== CREATE =====
    async def create_session(
        self, 
        session_data: ChatSessionCreate
    ) -> ChatSession:
        """
        Create new chat session
        
        Steps:
        1. Generate UUID for session
        2. Create session directory: data/chat_sessions/{session_id}/
        3. Create metadata.json with session info
        4. Create messages.jsonl (empty initially)
        5. Return ChatSession object
        
        Validation:
        - Project must exist
        - Title max 255 chars
        """
        session_id = uuid4()
        session_dir = self.data_dir / str(session_id)
        session_dir.mkdir(parents=True, exist_ok=True)
        
        metadata = {
            'id': str(session_id),
            'project_id': str(session_data.project_id),
            'title': session_data.title,
            'description': session_data.description or '',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'messages_count': 0,
            'is_archived': False,
            'tags': [],
            'metadata': session_data.metadata or {}
        }
        
        # Write metadata
        metadata_file = session_dir / 'metadata.json'
        metadata_file.write_text(json.dumps(metadata, indent=2))
        
        # Create empty messages file
        messages_file = session_dir / 'messages.jsonl'
        messages_file.write_text('')
        
        return ChatSession(**metadata)
    
    # ===== READ =====
    async def get_session(self, session_id: UUID) -> ChatSession:
        """
        Load chat session from disk
        
        Steps:
        1. Locate session directory
        2. Read metadata.json
        3. Parse and return ChatSession
        """
        session_dir = self.data_dir / str(session_id)
        metadata_file = session_dir / 'metadata.json'
        
        if not metadata_file.exists():
            raise NotFoundError(f"Session {session_id} not found")
        
        data = json.loads(metadata_file.read_text())
        return ChatSession(**data)
    
    async def list_sessions(self, project_id: UUID) -> List[ChatSession]:
        """
        List all sessions for a project
        
        Steps:
        1. Scan all session directories
        2. Filter by project_id in metadata
        3. Return list of ChatSession objects
        """
        sessions = []
        for session_dir in self.data_dir.iterdir():
            if session_dir.is_dir():
                metadata_file = session_dir / 'metadata.json'
                if metadata_file.exists():
                    data = json.loads(metadata_file.read_text())
                    if data['project_id'] == str(project_id):
                        sessions.append(ChatSession(**data))
        
        return sorted(sessions, key=lambda s: s.updated_at, reverse=True)
    
    async def get_session_with_messages(
        self, 
        session_id: UUID
    ) -> ChatSessionWithMessages:
        """
        Load session including all messages
        
        Steps:
        1. Load session metadata
        2. Read messages.jsonl line by line
        3. Parse each line as Message
        4. Return ChatSessionWithMessages
        """
        session = await self.get_session(session_id)
        messages = await self._load_messages(session_id)
        
        return ChatSessionWithMessages(
            **session.dict(),
            messages=messages
        )
    
    # ===== UPDATE =====
    async def update_session(
        self,
        session_id: UUID,
        update_data: ChatSessionUpdate
    ) -> ChatSession:
        """
        Update session metadata
        
        Steps:
        1. Load current metadata
        2. Update fields
        3. Write back to disk
        4. Return updated ChatSession
        """
        session_dir = self.data_dir / str(session_id)
        metadata_file = session_dir / 'metadata.json'
        
        data = json.loads(metadata_file.read_text())
        
        if update_data.title:
            data['title'] = update_data.title
        if update_data.description is not None:
            data['description'] = update_data.description
        if update_data.metadata:
            data['metadata'] = {**data.get('metadata', {}), **update_data.metadata}
        
        data['updated_at'] = datetime.now().isoformat()
        
        metadata_file.write_text(json.dumps(data, indent=2))
        return ChatSession(**data)
    
    # ===== DELETE =====
    async def delete_session(self, session_id: UUID) -> bool:
        """
        Delete session and all messages
        
        Steps:
        1. Locate session directory
        2. Remove all files
        3. Remove directory
        4. Return success
        """
        session_dir = self.data_dir / str(session_id)
        
        if session_dir.exists():
            import shutil
            shutil.rmtree(session_dir)
            return True
        
        return False
    
    # ===== MESSAGES =====
    async def _load_messages(self, session_id: UUID) -> List[Message]:
        """
        Load all messages from messages.jsonl
        
        Format: Each line is a JSON object representing a Message
        
        Returns: List of Message objects sorted by timestamp
        """
        session_dir = self.data_dir / str(session_id)
        messages_file = session_dir / 'messages.jsonl'
        
        messages = []
        if messages_file.exists():
            for line in messages_file.read_text().strip().split('\n'):
                if line.strip():
                    data = json.loads(line)
                    messages.append(Message(**data))
        
        return sorted(messages, key=lambda m: m.timestamp)
    
    async def add_message(
        self,
        session_id: UUID,
        message: MessageCreate
    ) -> Message:
        """
        Add message to session
        
        Steps:
        1. Generate UUID for message
        2. Append to messages.jsonl as new line
        3. Update messages_count in metadata
        4. Return Message object
        """
        session_dir = self.data_dir / str(session_id)
        messages_file = session_dir / 'messages.jsonl'
        
        message_id = uuid4()
        message_data = {
            'id': str(message_id),
            'session_id': str(session_id),
            'content': message.content,
            'role': message.role,
            'timestamp': datetime.now().isoformat(),
            'tokens': message.tokens,
            'provider_id': message.provider_id,
            'status': message.status,
            'metadata': message.metadata
        }
        
        # Append to file
        with open(messages_file, 'a') as f:
            f.write(json.dumps(message_data) + '\n')
        
        # Update messages count
        metadata_file = session_dir / 'metadata.json'
        data = json.loads(metadata_file.read_text())
        data['messages_count'] = data.get('messages_count', 0) + 1
        data['updated_at'] = datetime.now().isoformat()
        metadata_file.write_text(json.dumps(data, indent=2))
        
        return Message(**message_data)
```

### 4.2 AIProviderService

**File:** `backend/services/ai_provider_service.py`

**Purpose:** Handle communication with AI APIs (OpenAI, Anthropic, etc.)

**Methods:**

```python
class AIProviderService:
    def __init__(self):
        self.providers_config = {
            'openai': {
                'base_url': 'https://api.openai.com/v1',
                'api_key_env': 'OPENAI_API_KEY',
                'models': ['gpt-4', 'gpt-3.5-turbo']
            },
            'anthropic': {
                'base_url': 'https://api.anthropic.com/v1',
                'api_key_env': 'ANTHROPIC_API_KEY',
                'models': ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku']
            }
        }
    
    async def get_available_providers(self) -> List[Provider]:
        """
        Get all configured providers with status
        
        Returns list of Provider objects with is_available flag
        """
        providers = []
        for provider_name, config in self.providers_config.items():
            api_key = os.getenv(config['api_key_env'])
            is_available = bool(api_key)
            
            provider = Provider(
                id=uuid4(),
                name=provider_name,
                display_name=provider_name.title(),
                description=f"{provider_name.title()} AI models",
                base_url=config['base_url'],
                api_key_env_var=config['api_key_env'],
                models=config['models'],
                is_available=is_available
            )
            providers.append(provider)
        
        return providers
    
    async def send_request(
        self,
        provider_id: str,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        config: Optional[ProviderConfig] = None
    ) -> ProviderResponse:
        """
        Send request to AI provider
        
        Steps:
        1. Validate provider exists and API key available
        2. Format messages for provider API
        3. Make HTTP request to provider
        4. Parse response
        5. Return ProviderResponse
        
        Error handling:
        - If API key missing: raise UnauthorizedError
        - If provider unavailable: raise ProviderError
        - If rate limited: raise RateLimitError
        - If invalid request: raise ValidationError
        """
        # Get provider config
        provider_config = self.providers_config.get(provider_id)
        if not provider_config:
            raise ValueError(f"Unknown provider: {provider_id}")
        
        # Get API key
        api_key = os.getenv(provider_config['api_key_env'])
        if not api_key:
            raise UnauthorizedError(f"API key not configured for {provider_id}")
        
        # Format messages
        formatted_messages = [
            {
                'role': msg.role,
                'content': msg.content
            }
            for msg in messages
        ]
        
        # Prepare request based on provider
        if provider_id == 'openai':
            response = await self._send_openai_request(
                api_key,
                formatted_messages,
                system_prompt,
                config
            )
        elif provider_id == 'anthropic':
            response = await self._send_anthropic_request(
                api_key,
                formatted_messages,
                system_prompt,
                config
            )
        else:
            raise ValueError(f"Unsupported provider: {provider_id}")
        
        return response
    
    async def _send_openai_request(
        self,
        api_key: str,
        messages: List[dict],
        system_prompt: Optional[str],
        config: Optional[ProviderConfig]
    ) -> ProviderResponse:
        """
        Send request to OpenAI API
        
        Endpoint: POST https://api.openai.com/v1/chat/completions
        
        Request body:
        {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        """
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'gpt-4',
            'messages': messages,
            'temperature': config.temperature if config else 0.7,
            'max_tokens': config.max_tokens if config else 2000
        }
        
        if system_prompt:
            payload['messages'].insert(0, {
                'role': 'system',
                'content': system_prompt
            })
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise ProviderError(f"OpenAI API error: {response.text}")
            
            data = response.json()
            
            return ProviderResponse(
                id=str(uuid4()),
                content=data['choices'][0]['message']['content'],
                tokens={
                    'prompt': data['usage']['prompt_tokens'],
                    'completion': data['usage']['completion_tokens'],
                    'total': data['usage']['total_tokens']
                },
                finish_reason=data['choices'][0]['finish_reason'],
                provider_id='openai'
            )
```

### 4.3 ProjectService

**File:** `backend/services/project_service.py`

**Responsibilities:**
- CRUD operations for projects
- Nested project support
- Directory management
- Session listing per project

**Key Methods:**
```python
async def create_project(data: ProjectCreate) -> Project
async def get_project(project_id: UUID) -> Project
async def list_projects(parent_id: Optional[UUID] = None) -> List[Project]
async def update_project(project_id: UUID, data: ProjectUpdate) -> Project
async def delete_project(project_id: UUID) -> bool
async def get_project_tree() -> Project  # Nested structure
async def add_session_to_project(project_id: UUID, session_id: UUID) -> bool
```

### 4.4 FileManagementService

**File:** `backend/services/file_management_service.py`

**Responsibilities:**
- File upload/download
- File listing
- File metadata storage
- Directory structure for project/session files

**Key Methods:**
```python
async def upload_file(
    project_id: UUID,
    session_id: Optional[UUID],
    file: UploadFile
) -> FileMetadata

async def download_file(file_id: UUID) -> bytes

async def list_project_files(project_id: UUID) -> List[FileMetadata]

async def list_session_files(session_id: UUID) -> List[FileMetadata]

async def delete_file(file_id: UUID) -> bool

async def get_file_metadata(file_id: UUID) -> FileMetadata
```

---

## 5. API Endpoint Specifications

### 5.1 Chat Session Endpoints

**Base URL:** `http://localhost:8000/api`

#### GET `/chat-sessions/{sessionId}`
**Purpose:** Get chat session with messages

**Request:**
```
GET /chat-sessions/550e8400-e29b-41d4-a716-446655440000
```

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "projectId": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Project Analysis",
  "description": "Analyzing project requirements",
  "createdAt": "2025-11-11T10:30:00Z",
  "updatedAt": "2025-11-11T10:35:00Z",
  "messagesCount": 12,
  "messages": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "sessionId": "550e8400-e29b-41d4-a716-446655440000",
      "content": "Can you help me understand this code?",
      "role": "user",
      "timestamp": "2025-11-11T10:30:15Z",
      "status": "sent"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "sessionId": "550e8400-e29b-41d4-a716-446655440000",
      "content": "Of course! I'd be happy to help...",
      "role": "assistant",
      "timestamp": "2025-11-11T10:30:30Z",
      "tokens": 150,
      "providerId": "openai",
      "status": "sent"
    }
  ]
}
```

#### POST `/chat-sessions`
**Purpose:** Create new chat session

**Request:**
```json
{
  "projectId": "550e8400-e29b-41d4-a716-446655440001",
  "title": "New Chat",
  "description": "Optional description",
  "metadata": {}
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "projectId": "550e8400-e29b-41d4-a716-446655440001",
  "title": "New Chat",
  "createdAt": "2025-11-11T10:30:00Z",
  "messagesCount": 0
}
```

#### POST `/chat-sessions/{sessionId}/messages`
**Purpose:** Send message and get AI response

**Request:**
```json
{
  "content": "What is the weather today?",
  "providerId": "openai",
  "config": {
    "temperature": 0.7,
    "maxTokens": 2000
  }
}
```

**Response (200):**
```json
{
  "userMessage": {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "sessionId": "550e8400-e29b-41d4-a716-446655440000",
    "content": "What is the weather today?",
    "role": "user",
    "timestamp": "2025-11-11T10:30:15Z",
    "status": "sent"
  },
  "aiMessage": {
    "id": "550e8400-e29b-41d4-a716-446655440003",
    "sessionId": "550e8400-e29b-41d4-a716-446655440000",
    "content": "I don't have access to real-time weather data...",
    "role": "assistant",
    "timestamp": "2025-11-11T10:30:30Z",
    "tokens": 125,
    "providerId": "openai",
    "status": "sent"
  }
}
```

#### DELETE `/chat-sessions/{sessionId}`
**Purpose:** Delete chat session

**Response (204):** No content

### 5.2 Provider Endpoints

#### GET `/providers`
**Purpose:** List all AI providers

**Response (200):**
```json
{
  "providers": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "openai",
      "displayName": "OpenAI",
      "description": "OpenAI GPT models including GPT-4, GPT-3.5, and DALL-E",
      "baseUrl": "https://api.openai.com/v1",
      "models": ["gpt-4", "gpt-3.5-turbo"],
      "isAvailable": true,
      "createdAt": "2025-11-11T10:00:00Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "name": "anthropic",
      "displayName": "Anthropic",
      "description": "Anthropic Claude models",
      "baseUrl": "https://api.anthropic.com/v1",
      "models": ["claude-3-opus", "claude-3-sonnet"],
      "isAvailable": false,
      "createdAt": "2025-11-11T10:00:00Z"
    }
  ]
}
```

### 5.3 Project Endpoints

#### GET `/projects`
**Purpose:** Get project tree (nested structure)

**Response (200):**
```json
{
  "projects": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "Main Project",
      "isDefault": true,
      "sessions": [
        {
          "id": "550e8400-e29b-41d4-a716-446655440010",
          "title": "Chat Session 1"
        }
      ],
      "childProjects": [
        {
          "id": "550e8400-e29b-41d4-a716-446655440002",
          "name": "Sub Project",
          "sessions": []
        }
      ]
    }
  ]
}
```

### 5.4 Settings Endpoints

#### GET `/settings`
**Purpose:** Get user settings

**Response (200):**
```json
{
  "theme": "dark",
  "defaultProjectId": "550e8400-e29b-41d4-a716-446655440001",
  "defaultProviderId": "openai",
  "autoSaveInterval": 30000,
  "notificationsEnabled": true
}
```

#### PUT `/settings`
**Purpose:** Update settings

**Request:**
```json
{
  "theme": "light",
  "defaultProviderId": "anthropic"
}
```

#### PUT `/settings/api-keys`
**Purpose:** Update API keys (writes to .env file)

**Request:**
```json
{
  "OPENAI_API_KEY": "sk-...",
  "ANTHROPIC_API_KEY": "sk-ant-..."
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "API keys updated successfully"
}
```

---

## 6. State Management Specifications

### 6.1 Zustand Stores (TypeScript)

#### Chat Store

```typescript
// frontend/src/stores/chatStore.ts
import { create } from 'zustand'

interface ChatState {
  // Data
  sessions: ChatSession[]
  currentSessionId: string | null
  messages: Message[]
  
  // UI
  isLoading: boolean
  error: string | null
  
  // Actions
  setSessions: (sessions: ChatSession[]) => void
  setCurrentSession: (sessionId: string) => void
  setMessages: (messages: Message[]) => void
  addMessage: (message: Message) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearCurrentSession: () => void
}

export const useChatStore = create<ChatState>((set) => ({
  sessions: [],
  currentSessionId: null,
  messages: [],
  isLoading: false,
  error: null,
  
  setSessions: (sessions) => set({ sessions }),
  setCurrentSession: (sessionId) => set({ currentSessionId: sessionId }),
  setMessages: (messages) => set({ messages }),
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message]
  })),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  clearCurrentSession: () => set({ 
    currentSessionId: null,
    messages: []
  })
}))
```

#### Providers Store

```typescript
interface ProvidersState {
  providers: Provider[]
  currentProviderId: string | null
  isLoading: boolean
  error: string | null
  
  setProviders: (providers: Provider[]) => void
  setCurrentProvider: (providerId: string) => void
  addProvider: (provider: Provider) => void
  updateProvider: (providerId: string, updates: Partial<Provider>) => void
  deleteProvider: (providerId: string) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

export const useProvidersStore = create<ProvidersState>((set) => ({
  providers: [],
  currentProviderId: null,
  isLoading: false,
  error: null,
  
  setProviders: (providers) => set({ providers }),
  setCurrentProvider: (providerId) => set({ currentProviderId: providerId }),
  addProvider: (provider) => set((state) => ({
    providers: [...state.providers, provider]
  })),
  updateProvider: (providerId, updates) => set((state) => ({
    providers: state.providers.map(p =>
      p.id === providerId ? { ...p, ...updates } : p
    )
  })),
  deleteProvider: (providerId) => set((state) => ({
    providers: state.providers.filter(p => p.id !== providerId)
  })),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error })
}))
```

---

## 7. Database Schema & Operations

### 7.1 File System Structure

**Complete Directory Layout:**

```
data/
├── chat_sessions/
│   ├── {session-uuid}/
│   │   ├── metadata.json          # Session metadata
│   │   ├── messages.jsonl         # Messages (one per line)
│   │   └── files/                 # Session-specific files
│   │       ├── file1.txt
│   │       └── file2.pdf
│   ├── {session-uuid}/
│   │   └── ...
│   └── {session-uuid}/
│
├── projects/
│   ├── {project-uuid}/
│   │   ├── metadata.json          # Project metadata
│   │   ├── settings.json          # Project settings
│   │   ├── files/                 # Project-wide files
│   │   │   ├── README.md
│   │   │   └── config.json
│   │   └── sessions.json          # List of session IDs
│   ├── {project-uuid}/
│   │   └── ...
│   └── default/                   # Default project
│       └── metadata.json
│
├── settings/
│   ├── user_settings.json         # User preferences
│   ├── provider_configs.json      # Provider configurations
│   └── history.json               # Session history
│
└── backups/
    ├── backup_2025-11-11_10-00.tar.gz
    └── ...
```

### 7.2 JSON Schema Examples

**Chat Session metadata.json:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "project_id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Project Analysis",
  "description": "Analyzing project requirements",
  "created_at": "2025-11-11T10:30:00Z",
  "updated_at": "2025-11-11T10:35:00Z",
  "messages_count": 12,
  "is_archived": false,
  "tags": ["important", "architecture"],
  "metadata": {
    "custom_field": "custom_value"
  }
}
```

**messages.jsonl (each line is one message):**
```jsonl
{"id":"msg-1","session_id":"550e8400-e29b-41d4-a716-446655440000","content":"Can you help me?","role":"user","timestamp":"2025-11-11T10:30:15Z","tokens":null,"provider_id":null,"status":"sent","metadata":{}}
{"id":"msg-2","session_id":"550e8400-e29b-41d4-a716-446655440000","content":"Of course!","role":"assistant","timestamp":"2025-11-11T10:30:30Z","tokens":50,"provider_id":"openai","status":"sent","metadata":{}}
```

**Project metadata.json:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "parent_project_id": null,
  "name": "Main Project",
  "description": "Default project for main chat",
  "created_at": "2025-11-11T10:00:00Z",
  "updated_at": "2025-11-11T10:00:00Z",
  "child_project_ids": [],
  "session_ids": ["550e8400-e29b-41d4-a716-446655440010"],
  "files_count": 2,
  "is_default": true,
  "metadata": {}
}
```

---

## 8. File System Structure & Operations

### 8.1 Data Persistence Operations

**Read Operation Example:**
```python
def read_session(session_id: UUID) -> dict:
    """
    1. Compute path: data/chat_sessions/{session_id}
    2. Check if directory exists
    3. Read metadata.json
    4. Parse JSON
    5. Return dict
    """
    session_dir = Path(f"data/chat_sessions/{session_id}")
    metadata_file = session_dir / "metadata.json"
    
    if not metadata_file.exists():
        raise FileNotFoundError(f"Session {session_id} not found")
    
    return json.loads(metadata_file.read_text())
```

**Write Operation Example:**
```python
def write_message(session_id: UUID, message: dict) -> None:
    """
    1. Get session directory path
    2. Append message to messages.jsonl
    3. Update messages_count in metadata.json
    """
    session_dir = Path(f"data/chat_sessions/{session_id}")
    messages_file = session_dir / "messages.jsonl"
    
    with open(messages_file, 'a') as f:
        f.write(json.dumps(message) + '\n')
```

### 8.2 Error Handling

**Standard Error Responses:**
```python
class NotFoundError(Exception):
    code = "NOT_FOUND"
    status_code = 404
    def __init__(self, message):
        self.message = message

class ValidationError(Exception):
    code = "VALIDATION_ERROR"
    status_code = 400
    def __init__(self, field, message):
        self.field = field
        self.message = message

class ProviderError(Exception):
    code = "PROVIDER_ERROR"
    status_code = 503
    def __init__(self, message):
        self.message = message
```

---

## Summary

This technical specification provides:
✅ **Component-level specifications** for every UI component  
✅ **Service method signatures** with implementation details  
✅ **API endpoint definitions** with request/response formats  
✅ **Data model definitions** in TypeScript and Python  
✅ **State management structure** with Zustand stores  
✅ **File system operations** and data persistence patterns  
✅ **Error handling** and validation rules  
✅ **Directory structures** and file organization  

**AI Code Generation Ready:** All specifications include:
- Clear purpose and responsibility
- Input/output formats
- Error conditions
- Implementation steps
- Code examples

This is sufficient for AI models to generate production-ready source code.

---

**Last Updated:** November 11, 2025  
**Depth Level:** Implementation-ready (AI code generation suitable)  
**Status:** ✅ Complete and detailed
