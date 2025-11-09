# ✅ Setup Checklist & Verification

Use this checklist to verify everything is set up correctly.

## Pre-Flight Checks

### System Requirements
- [ ] Python 3.11+ installed (`python --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] npm 8+ installed (`npm --version`)
- [ ] Git installed and configured
- [ ] 2GB free disk space
- [ ] Port 3000 available (frontend)
- [ ] Port 8000 available (backend)

### Environment Setup
- [ ] `.env` file created from `.env.example`
- [ ] `OPENAI_API_KEY` added to `.env`
- [ ] `WORKSPACE_ROOT` configured in `.env`
- [ ] `frontend/.env.local` created from `.env.development`

## Backend Setup

### Installation
- [ ] Virtual environment created: `python -m venv venv`
- [ ] Virtual environment activated: `.\venv\Scripts\activate`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] No pip errors or warnings

### Structure
- [ ] `backend/main.py` exists and contains FastAPI app
- [ ] `backend/api/` folder has chat.py, files.py, workspace.py
- [ ] `backend/config/settings.py` contains Settings class
- [ ] All `__init__.py` files present

### Verification
```bash
# Run these commands
python -c "import fastapi; print(f'FastAPI {fastapi.__version__}')"
python -c "import uvicorn; print(f'Uvicorn {uvicorn.__version__}')"
python -c "import pydantic; print(f'Pydantic {pydantic.__version__}')"
```

## Frontend Setup

### Installation
- [ ] Changed to `frontend/` directory
- [ ] Dependencies installed: `npm install`
- [ ] `node_modules/` folder created
- [ ] No npm errors or warnings
- [ ] `.env.local` created

### Structure
- [ ] `src/components/` has ChatMessage.tsx, ChatInput.tsx, ChatArea.tsx
- [ ] `src/pages/ChatPage.tsx` exists
- [ ] `src/services/api.ts` contains API client
- [ ] `src/stores/chatStore.ts` contains Zustand store
- [ ] `vite.config.ts` configured correctly
- [ ] `tailwind.config.js` configured

### Verification
```bash
cd frontend
npm list react react-dom typescript vite
# Should show installed versions without errors
```

## Starting the Servers

### Backend (Terminal 1)
```bash
# From project root
.\venv\Scripts\activate
python -m backend.main

# You should see:
# 🚀 Starting AI Chat Assistant API
#    Running on http://0.0.0.0:8000
#    Debug mode: True
#    API docs: http://0.0.0.0:8000/docs
```

**Verification:**
- [ ] FastAPI starts without errors
- [ ] No "port already in use" errors
- [ ] Can access http://localhost:8000
- [ ] Can access http://localhost:8000/docs

### Frontend (Terminal 2)
```bash
# From frontend directory
npm run dev

# You should see:
#   VITE v5.0.0  ready in XXX ms
#
#   ➜  Local:   http://localhost:3000/
```

**Verification:**
- [ ] Vite starts without errors
- [ ] No "port already in use" errors
- [ ] Can access http://localhost:3000
- [ ] Browser shows the chat interface

## API Testing

### Health Check
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","version":"0.1.0"}
```

- [ ] Health endpoint responds with status 200

### API Documentation
- [ ] Visit http://localhost:8000/docs in browser
- [ ] See interactive API documentation
- [ ] Can see all endpoints listed
- [ ] Can try endpoints from UI

### Chat Endpoint
- [ ] POST to `/api/chat/send` works (test in /docs)
- [ ] Returns response with proper structure
- [ ] No CORS errors in browser console

## Frontend Testing

### Page Load
- [ ] http://localhost:3000 loads without errors
- [ ] See "AI Chat Assistant" header
- [ ] Chat area displays welcome message
- [ ] Input field is visible and focused

### Console Check
- [ ] No JavaScript errors in browser console (F12)
- [ ] No warnings about missing modules
- [ ] API requests visible in Network tab

### Component Rendering
- [ ] ChatMessage components render correctly
- [ ] ChatInput field accepts text
- [ ] Send button is clickable
- [ ] ChatArea scrolls properly

## Communication Testing

### Request/Response Flow
- [ ] Type message in chat input
- [ ] Click send button
- [ ] See message appear in chat
- [ ] Backend logs the request
- [ ] Response displays (or loading spinner)
- [ ] No CORS errors

### Network Check (Browser DevTools)
- [ ] Open DevTools (F12)
- [ ] Go to Network tab
- [ ] Send a message
- [ ] See POST request to `/api/chat/send`
- [ ] Request has proper headers
- [ ] Response status is 200

## Configuration Verification

### Backend Settings
```python
# These should be accessible
python -c "from backend.config.settings import settings; print(settings.API_PORT)"
# Output: 8000

python -c "from backend.config.settings import settings; print(settings.DEFAULT_MODEL)"
# Output: gpt-4-turbo
```

- [ ] Settings load correctly
- [ ] Environment variables are read
- [ ] Default values apply

### Frontend Configuration
```bash
cd frontend
# Should show your API URL
cat .env.local | grep VITE_API_URL
```

- [ ] `.env.local` contains API URL
- [ ] Vite uses correct API URL

## Docker Setup (Optional)

If using Docker:

```bash
# Build images
docker-compose build

# Should complete without errors
- [ ] Backend image builds successfully
- [ ] Frontend image builds successfully
- [ ] No build errors or warnings

# Start containers
docker-compose up

# Should output service logs
- [ ] API container starts
- [ ] Frontend container starts
- [ ] Can access http://localhost:3000
- [ ] Can access http://localhost:8000

# Cleanup
docker-compose down
- [ ] Containers stop cleanly
- [ ] No error messages
```

## File Structure Verification

```bash
# Check key files exist
ls backend/main.py backend/api/chat.py backend/config/settings.py
ls frontend/src/main.tsx frontend/src/pages/ChatPage.tsx
ls docker-compose.yml requirements.txt .env.example
```

- [ ] All key files present
- [ ] No missing critical files
- [ ] Correct file permissions (readable)

## Performance Checks

### Response Time
- [ ] API `/health` responds in < 100ms
- [ ] Frontend loads in < 2s
- [ ] No slow network requests
- [ ] Browser console shows no performance warnings

### Memory Usage
- [ ] Backend process uses < 100MB RAM
- [ ] Frontend page uses < 50MB
- [ ] No memory leaks after sending messages

## Troubleshooting Steps

### If Backend Won't Start
- [ ] Check `OPENAI_API_KEY` is set in `.env`
- [ ] Check port 8000 is not in use
- [ ] Check all dependencies installed: `pip list | grep fastapi`
- [ ] Check Python version: `python --version`
- [ ] Try reinstalling: `pip install -r requirements.txt --upgrade`

### If Frontend Won't Start
- [ ] Check port 3000 is not in use
- [ ] Check Node version: `node --version`
- [ ] Delete node_modules and package-lock.json, reinstall: `npm install`
- [ ] Clear browser cache
- [ ] Check `.env.local` is correct

### If Communication Fails
- [ ] Check backend is running: `curl http://localhost:8000/health`
- [ ] Check frontend can see backend: Browser DevTools -> Network tab
- [ ] Check CORS settings in `backend/config/settings.py`
- [ ] Check CORS_ORIGINS includes `http://localhost:3000`

### If CORS Errors Occur
1. Go to `backend/config/settings.py`
2. Add your frontend URL to `CORS_ORIGINS`
3. Restart backend
4. Clear browser cache
5. Refresh page

## Post-Setup Tasks

### Documentation Review
- [ ] Read `README.md`
- [ ] Read `DEVELOPMENT.md`
- [ ] Read `ARCHITECTURE.md`
- [ ] Read `VISUAL_GUIDE.md`

### Feature Implementation Planning
- [ ] Identify first feature to implement
- [ ] Plan service layer structure
- [ ] Plan React component structure
- [ ] Create implementation tasks

### Customization
- [ ] Update project name in documentation
- [ ] Customize welcome message
- [ ] Add project logo if desired
- [ ] Update git remote if applicable

## Environment Variables Checklist

### Required
- [ ] `OPENAI_API_KEY` - Your OpenAI API key

### Recommended
- [ ] `WORKSPACE_ROOT` - Path to local workspace
- [ ] `DEBUG` - Set to True for development
- [ ] `API_PORT` - Port for backend (8000 default)

### Optional
- [ ] `ANTHROPIC_API_KEY` - For Claude support
- [ ] `GITHUB_TOKEN` - For GitHub integration
- [ ] `NOTION_TOKEN` - For Notion integration
- [ ] `LOG_LEVEL` - DEBUG, INFO, WARNING, ERROR

## Verification Commands

Run these to verify everything is working:

```bash
# Test backend
python -m pytest --version          # Pytest installed
python -c "from backend.main import app; print(app.title)"
curl http://localhost:8000/health

# Test frontend
npm test -- --version              # Jest available
npm run build                       # Build succeeds

# Test Docker (if using)
docker --version
docker-compose --version
docker-compose config              # Config valid
```

- [ ] All commands run without errors

## Final Sign-Off

- [ ] All checklist items completed
- [ ] Backend starts and responds
- [ ] Frontend loads and displays
- [ ] Can send messages and receive responses
- [ ] No errors in browser console
- [ ] No errors in terminal output
- [ ] Documentation is understood
- [ ] Ready to implement features

---

## What's Next?

After verifying everything works:

1. **Implement core services** - Start with `backend/services/conversation.py`
2. **Add AI integration** - Implement OpenAI in `backend/services/ai_provider.py`
3. **Build file manager** - Create `backend/services/file_manager.py`
4. **Enhance UI** - Add more components to frontend
5. **Add features** - Implement features from your roadmap

**You're all set! 🎉 Happy coding!**
