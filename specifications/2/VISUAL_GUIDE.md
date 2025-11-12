# 🚀 FastAPI + React Architecture - Visual Guide

## Project Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                                 │
├─────────────────────────────────────────────────────────────────────┤
│  http://localhost:3000                                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  FRONTEND (React + TypeScript + Tailwind)                  │   │
│  │  ┌────────────────────────────────────────────────────┐    │   │
│  │  │ Pages (ChatPage.tsx)                               │    │   │
│  │  │  ├── Components (ChatArea, ChatInput, etc)         │    │   │
│  │  │  ├── Stores (Zustand)                              │    │   │
│  │  │  └── Services (API client)                         │    │   │
│  │  └────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                    HTTP/REST/JSON
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│                    API SERVER (FastAPI)                              │
│                    http://localhost:8000                             │
├──────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ API Layer (backend/api/)                                  │    │
│  │  ├── /api/chat/*        ← Chat endpoints                  │    │
│  │  ├── /api/files/*       ← File endpoints                  │    │
│  │  └── /api/workspace/*   ← Workspace endpoints             │    │
│  └────────────────────────────────────────────────────────────┘    │
│                           │                                          │
│  ┌────────────────────────▼────────────────────────────────────┐   │
│  │ Services Layer (backend/services/)                          │   │
│  │  ├── conversation.py     ← Chat logic                       │   │
│  │  ├── file_manager.py     ← File operations                 │   │
│  │  ├── ai_provider.py      ← AI integration                  │   │
│  │  └── workspace.py        ← Context building                │   │
│  └────────────────────────────────────────────────────────────┘   │
│                           │                                          │
│  ┌────────────────────────▼────────────────────────────────────┐   │
│  │ External Services                                           │   │
│  │  ├── OpenAI API         ← AI responses                      │   │
│  │  ├── Local Filesystem   ← File operations                  │   │
│  │  ├── Memory (JSON)      ← Conversation history             │   │
│  │  └── Optional: Notion, GitHub, Database                   │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Config Layer                                                        │
│  └── settings.py           ← Environment configuration              │
└──────────────────────────────────────────────────────────────────────┘
```

## File Organization

```
YOUR PROJECT ROOT
│
├─ backend/                  ← Python FastAPI code
│  ├─ main.py              ← Entry point
│  ├─ api/                 ← HTTP endpoints
│  │  ├─ chat.py
│  │  ├─ files.py
│  │  └─ workspace.py
│  ├─ config/              ← Configuration
│  │  └─ settings.py
│  └─ services/            ← Business logic (TO IMPLEMENT)
│     ├─ conversation.py
│     ├─ ai_provider.py
│     └─ file_manager.py
│
├─ frontend/               ← React/TypeScript code
│  ├─ src/
│  │  ├─ components/       ← React components
│  │  │  ├─ ChatMessage.tsx
│  │  │  ├─ ChatInput.tsx
│  │  │  └─ ChatArea.tsx
│  │  ├─ pages/            ← Page components
│  │  │  └─ ChatPage.tsx
│  │  ├─ services/         ← API integration
│  │  │  └─ api.ts
│  │  ├─ stores/           ← State management
│  │  │  └─ chatStore.ts
│  │  ├─ App.tsx
│  │  └─ main.tsx
│  ├─ public/              ← Static files
│  ├─ index.html
│  ├─ package.json
│  └─ vite.config.ts
│
├─ core/                   ← Existing shared modules
│  ├─ memory_manager.py
│  └─ file_manager.py
│
├─ docker-compose.yml      ← Container orchestration
├─ requirements.txt        ← Python dependencies
├─ README.md              ← Main documentation
├─ DEVELOPMENT.md         ← Dev guide
├─ ARCHITECTURE.md        ← Design decisions
└─ .env.example          ← Configuration template
```

## Data Flow: Chat Request

```
1. User types in ChatInput component
   └─> input.tsx renders message input field

2. onSend handler triggered
   └─> calls chatAPI.sendMessage()

3. HTTP POST to http://localhost:8000/api/chat/send
   └─> JSON: { session_id, message, model, ... }

4. FastAPI receives at backend/api/chat.py
   └─> POST /send handler

5. Handler calls service layer
   └─> services/conversation.py processes message

6. Conversation service calls AI provider
   └─> services/ai_provider.py calls OpenAI API

7. OpenAI returns response
   └─> Service formats response

8. Response sent back to frontend
   └─> HTTP 200 with { message, model, ... }

9. Frontend receives response
   └─> chatStore updates with new messages

10. React re-renders ChatArea
    └─> New message displayed to user
```

## Request/Response Example

**Frontend sends:**
```typescript
const response = await chatAPI.sendMessage(
  "session-123",
  "What files are in my workspace?",
  "gpt-4-turbo"
)
```

**JSON sent to API:**
```json
{
  "session_id": "session-123",
  "message": "What files are in my workspace?",
  "model": "gpt-4-turbo",
  "include_workspace_context": true
}
```

**Backend processes:**
1. Validates request with Pydantic
2. Loads session from memory
3. Gets workspace context
4. Calls AI provider with tools
5. AI returns response
6. Saves to memory
7. Returns response

**JSON sent back:**
```json
{
  "session_id": "session-123",
  "message": "I found 47 files in your workspace. The main directories are...",
  "model": "gpt-4-turbo",
  "workspace_context_used": true
}
```

**Frontend updates:**
1. Receives response
2. Updates chatStore
3. Adds to messages array
4. ChatArea re-renders
5. New message appears

## Component Hierarchy

```
App
└── ChatPage
    ├── Header
    │   └── Title + Description
    ├── MainContent
    │   ├── ChatArea
    │   │   ├── Welcome (if no messages)
    │   │   └── Messages[]
    │   │       └── ChatMessage[]
    │   │           ├── User message bubble
    │   │           └── Assistant message bubble
    │   └── InputArea
    │       └── ChatInput
    │           ├── Text input field
    │           └── Send button
    └── (Future)
        ├── Sidebar
        │   └── FileTree
        └── Settings
```

## State Management Flow

```
ChatStore (Zustand)
├── sessionId          ← Current session ID
├── messages[]         ← Message history
│   ├── role (user/assistant)
│   ├── content
│   ├── id
│   └── timestamp
├── isLoading          ← Fetch in progress?
├── error              ← Error message
│
└── Actions
    ├── setSessionId()
    ├── addMessage()
    ├── setMessages()
    ├── setLoading()
    ├── setError()
    └── clearChat()
```

## API Endpoints Structure

```
/api/chat
├── POST /send
│   Request:  { session_id, message, model }
│   Response: { session_id, message, model, tool_calls }
│
├── GET /history/{session_id}
│   Response: { session_id, messages[] }
│
├── POST /sessions
│   Response: { session_id, created_at }
│
└── DELETE /sessions/{session_id}
    Response: { status, session_id }

/api/files
├── GET /list?directory=/
│   Response: { files[] }
│
├── GET /read?path=/file.txt
│   Response: { path, content, size }
│
├── POST /write
│   Request:  { path, content }
│   Response: { status, path }
│
└── POST /search
    Request:  { query, directory }
    Response: { results[] }

/api/workspace
├── GET /info
│   Response: { total_files, total_size, file_types }
│
├── GET /context
│   Response: { structure, stats, indexed_files }
│
├── GET /tree?max_depth=3
│   Response: { tree }
│
└── POST /index
    Response: { status, indexed_at }
```

## Environment Variables

```env
# SERVER CONFIG
API_PORT=8000                  Host port for API
API_HOST=0.0.0.0              Bind to all interfaces
DEBUG=True                    Development mode
RELOAD=True                   Auto-reload on changes

# AI CONFIGURATION
OPENAI_API_KEY=sk-...         Your OpenAI key
DEFAULT_MODEL=gpt-4-turbo     Model to use
ANTHROPIC_API_KEY=...         Optional: Claude key

# WORKSPACE
WORKSPACE_ROOT=./workspace    Local workspace path
MAX_FILE_SIZE_MB=10           Max file size
IGNORED_DIRS=.git,venv        Dirs to ignore

# MEMORY
MEMORY_FILE=data/memory.json  Persistent storage
MEMORY_REFRESH_HOURS=12       Cache duration

# FRONTEND (.env.local)
VITE_API_URL=http://localhost:8000/api
```

## Development Workflow

```
┌─────────────────────┐
│  Modify Backend     │
│  (main.py, api/*.py)│
└──────────┬──────────┘
           │ Save
           ▼
┌─────────────────────┐
│  Auto-reload        │ (RELOAD=True)
│  (Uvicorn reloads)  │
└──────────┬──────────┘
           │ Ready
           ▼
┌─────────────────────┐
│  Test in Frontend   │
│  (Call new endpoint)│
└──────────┬──────────┘
           │
┌──────────────────────────────────────────────┐
│     Frontend Source Change (React/TS)       │
└────────────────┬─────────────────────────────┘
                 │ Save
                 ▼
      ┌───────────────────────┐
      │  Vite Hot Reload      │ (Instant!)
      │  Browser auto-refresh │
      └───────────────────────┘
```

## Testing Flow

```
Backend Test (pytest)
├── Test API endpoints
├── Test services
├── Mock external APIs
└── Verify database state

Frontend Test (Jest)
├── Test components
├── Test state management
├── Mock API calls
└── Test user interactions

Integration Test
├── Start both servers
├── Make real API calls
├── Verify full flow
└── Cleanup
```

## Deployment Pipeline

```
Development
└─ Run locally (npm run dev + python main.py)

Testing
└─ Run tests (pytest + npm test)

Docker Build
├─ docker build -f Dockerfile.backend
└─ docker build -f frontend/Dockerfile

Docker Compose
└─ docker-compose up --build

Production
├─ Push to registry
├─ Deploy to platform
├─ Configure environment
└─ Start services
```

## Security Layers

```
Frontend
├─ HTTPS only (production)
├─ Environment variables in .env
└─ No sensitive data in code

Backend
├─ Input validation (Pydantic)
├─ CORS restrictions
├─ Rate limiting (optional)
├─ API key authentication
└─ Environment-based secrets

Infrastructure
├─ Docker isolation
├─ Network policies
└─ Secrets management
```

---

**This visual guide helps you understand the complete flow of data through the application!**
