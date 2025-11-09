# AI Chat Assistant

A standalone AI-powered chat assistant application with local file management capabilities, designed as a GitHub Copilot analog but without coding specialization.

## Architecture Overview

This project follows a modern **FastAPI + React** architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                   │
│  • Chat interface                                             │
│  • File browser / workspace tree                             │
│  • Real-time messaging                                        │
│  • Session management                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST + WebSocket
                       │
┌──────────────────────▼──────────────────────────────────────┐
│               Backend (FastAPI + Python)                     │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │  Chat Engine   │  │  File Manager  │  │  Workspace   │  │
│  │  & Conversation│  │                │  │  Indexer     │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           AI Provider Abstraction Layer                │ │
│  │  (OpenAI, Claude, Local LLMs, etc.)                    │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           Connector System                             │ │
│  │  (Notion, GitHub, Local Filesystem, etc.)             │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
ai-chat-assistant/
├── backend/                           # FastAPI backend
│   ├── __init__.py
│   ├── main.py                        # Application entry point
│   ├── api/                           # API endpoints
│   │   ├── __init__.py
│   │   ├── chat.py                    # Chat endpoints
│   │   ├── files.py                   # File management endpoints
│   │   └── workspace.py               # Workspace endpoints
│   ├── services/                      # Business logic
│   │   ├── __init__.py
│   │   ├── conversation.py            # Conversation management
│   │   ├── ai_provider.py             # AI model abstraction
│   │   └── file_manager.py            # File operations
│   └── config/                        # Configuration
│       ├── __init__.py
│       └── settings.py                # Settings & environment
│
├── frontend/                          # React + Vite frontend
│   ├── src/
│   │   ├── components/                # React components
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   ├── ChatArea.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── FileTree.tsx
│   │   ├── pages/                     # Page components
│   │   │   └── ChatPage.tsx
│   │   ├── services/                  # API clients
│   │   │   └── api.ts
│   │   ├── stores/                    # State management (Zustand)
│   │   │   └── chatStore.ts
│   │   ├── hooks/                     # Custom React hooks
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/                        # Static assets
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── tailwind.config.js
│
├── core/                              # Shared core modules
│   ├── __init__.py
│   ├── memory_manager.py              # Conversation memory
│   ├── file_manager.py                # File operations
│   └── context_builder.py             # Workspace context
│
├── ai/                                # AI abstraction layer
│   ├── providers/                     # AI model providers
│   │   ├── base_provider.py
│   │   ├── openai_provider.py
│   │   └── anthropic_provider.py
│   ├── tools/                         # Tool definitions
│   │   ├── file_tools.py
│   │   ├── workspace_tools.py
│   │   └── generic_tools.py
│   └── conversation.py                # Conversation management
│
├── connectors/                        # External system connectors
│   ├── base_connector.py
│   ├── notion_connector.py
│   ├── github_connector.py
│   ├── local_connector.py
│   └── registry.py
│
├── data/                              # Data and state
│   ├── memory/                        # Persistent memory files
│   └── workspace/                     # Local workspace files
│
├── docker-compose.yml                 # Docker orchestration
├── Dockerfile.backend                 # Backend container
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment template
├── README.md                          # This file
└── DEVELOPMENT.md                     # Development guide
```

## Quick Start

### Prerequisites

- **Python 3.11+** (for backend)
- **Node.js 18+** (for frontend)
- **Docker & Docker Compose** (optional, for containerized development)

### Setup (Local Development)

#### 1. Clone & Enter Directory
```bash
cd c:\pf\AI-Chat-Assistant
```

#### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env

# Edit .env with your API keys
# Add: OPENAI_API_KEY, WORKSPACE_ROOT, etc.
```

#### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Create environment
copy .env.development .env.local
```

#### 4. Run Backend
```bash
# From project root, in first terminal
.\venv\Scripts\activate
python -m backend.main
```

Output should show:
```
🚀 Starting AI Chat Assistant API
   Running on http://0.0.0.0:8000
   API docs: http://0.0.0.0:8000/docs
```

#### 5. Run Frontend
```bash
# From frontend folder, in second terminal
npm run dev
```

Open http://localhost:3000 in your browser

### Docker Compose (Alternative)
```bash
# Build and start all services
docker-compose up --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Configuration

### Environment Variables

Create `.env` file in project root:

```env
# API Configuration
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000
RELOAD=True

# AI Provider
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_MODEL=gpt-4-turbo

# Workspace
WORKSPACE_ROOT=./workspace
MAX_FILE_SIZE_MB=10

# Memory
MEMORY_FILE=data/ai_dala_memory.json
MEMORY_REFRESH_HOURS=12

# External Connectors (Optional)
NOTION_TOKEN=...
GITHUB_TOKEN=...
```

### API Documentation

Once backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Features (Roadmap)

### Phase 1: Core MVP ✅ In Progress
- [x] FastAPI backend scaffold
- [x] React frontend scaffold
- [ ] Basic chat interface
- [ ] Session management
- [ ] OpenAI integration
- [ ] File reading/writing

### Phase 2: File Management
- [ ] Workspace file indexing
- [ ] File tree browser
- [ ] File search
- [ ] Safe file operations

### Phase 3: Advanced AI
- [ ] Multi-model support (Claude, Gemini)
- [ ] Local LLM support (Ollama)
- [ ] Streaming responses
- [ ] Tool use expansion

### Phase 4: System Integration
- [ ] Notion connector
- [ ] GitHub connector
- [ ] Database support
- [ ] Webhook support

### Phase 5: Production Ready
- [ ] Authentication & authorization
- [ ] WebSocket support (real-time)
- [ ] Rate limiting & caching
- [ ] Monitoring & logging
- [ ] Deployment guides (AWS, Azure, Docker Hub)

## API Endpoints

### Chat Endpoints
```
POST   /api/chat/send              Send a message
GET    /api/chat/history/{id}      Get conversation history
POST   /api/chat/sessions          Create new session
DELETE /api/chat/sessions/{id}     Delete session
```

### File Endpoints
```
GET    /api/files/list             List files in directory
GET    /api/files/read             Read file content
POST   /api/files/write            Write to file
POST   /api/files/upload           Upload file
POST   /api/files/search           Search files
```

### Workspace Endpoints
```
GET    /api/workspace/info         Workspace statistics
GET    /api/workspace/context      Full workspace context
GET    /api/workspace/tree         Directory tree
POST   /api/workspace/index        Reindex workspace
```

## Development

### Adding New Features

#### 1. Backend Feature
```python
# 1. Create endpoint in backend/api/
# 2. Implement service in backend/services/
# 3. Add models in backend/models/ (if needed)
# 4. Test with pytest
```

#### 2. Frontend Feature
```typescript
// 1. Create component in src/components/
// 2. Add API calls in src/services/api.ts
// 3. Update store if needed (src/stores/)
// 4. Use component in pages
```

### Testing

```bash
# Backend tests
pytest

# Frontend tests
npm test

# With coverage
pytest --cov=backend
```

### Code Quality

```bash
# Backend linting
flake8 backend/

# Backend formatting
black backend/

# Frontend linting
npm run lint

# Frontend formatting
npm run format
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (Windows)
taskkill /PID <PID> /F

# Or use different port
API_PORT=8001 python -m backend.main
```

### Module Not Found Errors
```bash
# Ensure virtual environment is activated
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### CORS Issues
Add your frontend URL to `CORS_ORIGINS` in `backend/config/settings.py`

### API Connection Failed
- Check backend is running: http://localhost:8000/health
- Check `VITE_API_URL` in frontend `.env.local`
- Check browser console for errors

## Contributing

1. Create feature branch: `git checkout -b feature/name`
2. Make changes and test
3. Commit: `git commit -am "Add feature"`
4. Push: `git push origin feature/name`
5. Create Pull Request

## License

MIT

## Support

For issues, questions, or suggestions:
- Check existing issues/documentation
- Create a new GitHub issue
- Contact project maintainers

---

**Happy coding! 🚀**
