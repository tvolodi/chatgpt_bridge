# Development Guide

## Getting Started with Development

### Initial Setup (One Time)

```bash
# 1. Clone the repository
cd c:\pf\AI-Chat-Assistant

# 2. Initialize git (if not already done)
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"

# 3. Create Python virtual environment
python -m venv venv

# 4. Activate virtual environment
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 5. Install backend dependencies
pip install -r requirements.txt

# 6. Install frontend dependencies
cd frontend
npm install
cd ..

# 7. Create .env file
copy .env.example .env

# 8. Edit .env with your configuration
notepad .env
```

## Running the Application

### Option 1: Local Development (Recommended)

**Terminal 1 - Backend:**
```bash
# Activate virtual environment
.\venv\Scripts\activate

# Run FastAPI with auto-reload
python -m backend.main

# Output:
# 🚀 Starting AI Chat Assistant API
#    Running on http://0.0.0.0:8000
#    Debug mode: True
#    API docs: http://0.0.0.0:8000/docs
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev

# Output:
#   VITE v5.0.0  ready in 234 ms
#
#   ➜  Local:   http://localhost:3000/
#   ➜  press h to show help
```

**Terminal 3 (Optional) - Run Tests:**
```bash
.\venv\Scripts\activate
pytest -v --tb=short
```

Visit: http://localhost:3000

### Option 2: Docker Compose

```bash
# Start all services
docker-compose up --build

# View logs
docker-compose logs -f api
docker-compose logs -f frontend

# Stop services
docker-compose down

# Clean everything
docker-compose down -v
```

## Project Structure Explanation

### Backend (`backend/`)

**main.py**
- Application entry point
- FastAPI app initialization
- Middleware setup (CORS, logging)
- Route registration

**api/** - API Endpoints
- `chat.py` - Conversation endpoints
- `files.py` - File management endpoints
- `workspace.py` - Workspace context endpoints

**services/** - Business Logic
- `conversation.py` - Manage chat sessions and history
- `ai_provider.py` - AI model abstraction
- `file_manager.py` - Safe file operations

**config/settings.py** - Configuration
- Environment variables
- Application settings
- Default values

### Frontend (`frontend/`)

**src/components/** - Reusable React Components
- `ChatMessage.tsx` - Renders individual messages
- `ChatInput.tsx` - Message input field
- `ChatArea.tsx` - Message display area
- `Sidebar.tsx` - Workspace sidebar (to implement)
- `FileTree.tsx` - File browser (to implement)

**src/pages/** - Page Components
- `ChatPage.tsx` - Main chat interface

**src/services/** - API Integration
- `api.ts` - Axios client with typed API calls

**src/stores/** - State Management (Zustand)
- `chatStore.ts` - Chat state (messages, session, etc.)

## Common Development Tasks

### Adding a New API Endpoint

1. **Create endpoint in `backend/api/`:**
```python
# backend/api/example.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ExampleRequest(BaseModel):
    name: str
    value: int

@router.post("/example")
async def create_example(request: ExampleRequest):
    """Create an example"""
    try:
        # Your logic here
        return {"status": "success", "name": request.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

2. **Register in `backend/main.py`:**
```python
from backend.api import example

app.include_router(example.router, prefix="/api/example", tags=["example"])
```

3. **Add API client in `frontend/src/services/api.ts`:**
```typescript
export const exampleAPI = {
  create: (name: string, value: number) =>
    apiClient.post('/example/example', { name, value }),
}
```

4. **Use in component:**
```typescript
import { exampleAPI } from '@/services/api'

const response = await exampleAPI.create("test", 42)
```

### Adding a New React Component

```typescript
// src/components/MyComponent.tsx
import React from 'react'

interface MyComponentProps {
  title: string
  onAction?: () => void
}

export const MyComponent: React.FC<MyComponentProps> = ({ 
  title, 
  onAction 
}) => {
  return (
    <div className="p-4 bg-slate-800 rounded-lg">
      <h2 className="text-xl font-bold">{title}</h2>
      <button 
        onClick={onAction}
        className="mt-2 px-4 py-2 bg-blue-600 rounded hover:bg-blue-700"
      >
        Action
      </button>
    </div>
  )
}

export default MyComponent
```

### Updating State Management

```typescript
// src/stores/newStore.ts
import { create } from 'zustand'

interface MyState {
  count: number
  increment: () => void
  decrement: () => void
}

export const useMyStore = create<MyState>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
}))
```

Use in component:
```typescript
import { useMyStore } from '@/stores/newStore'

const { count, increment } = useMyStore()
```

## Testing

### Backend Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_chat.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=backend

# Run in watch mode
pytest-watch
```

Example test:
```python
# tests/test_chat.py
import pytest
from backend.api import chat

@pytest.mark.asyncio
async def test_send_message():
    request = chat.ChatRequest(
        session_id="test-session",
        message="Hello"
    )
    response = await chat.send_message(request)
    assert response.session_id == "test-session"
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

## Debugging

### Backend Debugging

**Using VS Code:**
1. Add breakpoint in code
2. Run in debug mode:
```bash
python -m debugpy --listen 5678 -m backend.main
```
3. Attach debugger in VS Code

**Using print (simple):**
```python
import logging
logger = logging.getLogger(__name__)
logger.info(f"Debug: {variable}")
```

### Frontend Debugging

**Chrome DevTools:**
1. Open Chrome DevTools (F12)
2. Go to Console tab
3. Check for errors
4. Use debugger statements:
```typescript
debugger;  // Code execution will pause here
```

**VS Code Debugging:**
1. Add `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "chrome",
      "request": "launch",
      "name": "Launch Chrome",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}/frontend"
    }
  ]
}
```

## Code Quality

### Backend

```bash
# Code formatting
black backend/

# Linting
flake8 backend/ --max-line-length=100

# Type checking
mypy backend/ --ignore-missing-imports

# All checks
black backend/ && flake8 backend/ && mypy backend/
```

### Frontend

```bash
cd frontend

# Linting
npm run lint

# Format code
npm run format

# Both
npm run lint && npm run format
```

## Database & Persistence

Currently using JSON-based memory management. To add database support:

```python
# backend/services/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test.db"
# or PostgreSQL: "postgresql://user:password@localhost/dbname"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Environment Variables

### Backend (.env)

```env
# Server
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000
RELOAD=True

# AI
OPENAI_API_KEY=sk-...
DEFAULT_MODEL=gpt-4-turbo

# Workspace
WORKSPACE_ROOT=./workspace
MAX_FILE_SIZE_MB=10

# Logging
LOG_LEVEL=INFO
```

### Frontend (.env.local)

```env
VITE_API_URL=http://localhost:8000/api
```

## Performance Tips

1. **Frontend:**
   - Use React.memo for expensive components
   - Implement lazy loading for routes
   - Use Zustand for efficient state management

2. **Backend:**
   - Use async/await for I/O operations
   - Cache workspace context
   - Implement request logging and monitoring

3. **General:**
   - Monitor API response times
   - Use browser DevTools Performance tab
   - Profile with Python's cProfile

## Common Issues & Solutions

### 1. CORS Errors
**Problem:** Frontend can't reach backend
**Solution:** 
- Ensure backend CORS_ORIGINS includes your frontend URL
- Check backend is running
- Check API_BASE_URL in frontend

### 2. Module Not Found
**Problem:** `ModuleNotFoundError: No module named 'backend'`
**Solution:**
- Ensure you're in project root when running
- Check virtual environment is activated
- Run `pip install -r requirements.txt` again

### 3. Port Already in Use
**Problem:** `Address already in use`
**Solution:**
- Change port: `API_PORT=8001 python -m backend.main`
- Kill process: `taskkill /PID <PID> /F`

### 4. Dependencies Out of Date
**Problem:** Strange errors or missing features
**Solution:**
```bash
# Update all packages
pip install -r requirements.txt --upgrade
cd frontend && npm update && cd ..
```

## Next Steps

1. Implement core business logic in `backend/services/`
2. Build out chat UI components in `frontend/src/components/`
3. Integrate AI providers in `backend/ai/`
4. Add file management features
5. Implement authentication
6. Deploy to production

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [Vite Docs](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Zustand](https://github.com/pmndrs/zustand)

## Questions?

Check documentation or create an issue in the repository.
