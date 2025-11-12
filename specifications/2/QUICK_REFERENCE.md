# 🎯 Quick Reference Card

## 🚀 Getting Started (Copy & Paste)

### Windows PowerShell

```powershell
# 1. Setup Backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env

# 2. Setup Frontend
cd frontend
npm install
copy .env.development .env.local
cd ..

# 3. Terminal 1 - Backend
.\venv\Scripts\activate
python -m backend.main

# 4. Terminal 2 - Frontend
cd frontend
npm run dev

# 5. Open Browser
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### macOS/Linux

```bash
# 1. Setup Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# 2. Setup Frontend
cd frontend
npm install
cp .env.development .env.local
cd ..

# 3. Terminal 1 - Backend
source venv/bin/activate
python -m backend.main

# 4. Terminal 2 - Frontend
cd frontend
npm run dev

# 5. Open Browser
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

## 📁 File Locations

| What | Where |
|------|-------|
| Backend code | `backend/` |
| API endpoints | `backend/api/` |
| Configuration | `backend/config/settings.py` |
| Frontend code | `frontend/src/` |
| React components | `frontend/src/components/` |
| API client | `frontend/src/services/api.ts` |
| State store | `frontend/src/stores/chatStore.ts` |
| Environment file | `.env` (create from `.env.example`) |
| Python deps | `requirements.txt` |
| NPM deps | `frontend/package.json` |

## 🔌 API Endpoints

```
POST   /api/chat/send              Send a message
GET    /api/chat/history/{id}      Get history
POST   /api/chat/sessions          Create session
DELETE /api/chat/sessions/{id}     Delete session

GET    /api/files/list             List files
GET    /api/files/read             Read file
POST   /api/files/write            Write file
POST   /api/files/search           Search files

GET    /api/workspace/info         Workspace stats
GET    /api/workspace/context      Full context
GET    /api/workspace/tree         Directory tree
POST   /api/workspace/index        Reindex

GET    /health                     Health check
GET    /docs                       API documentation
```

## ⚙️ Configuration

### `.env` File (Required)
```env
OPENAI_API_KEY=sk-your-key-here
API_PORT=8000
DEBUG=True
WORKSPACE_ROOT=./workspace
DEFAULT_MODEL=gpt-4-turbo
```

### `frontend/.env.local` (Optional)
```env
VITE_API_URL=http://localhost:8000/api
```

## 🛠️ Development Commands

### Backend
```bash
python -m backend.main              # Start backend
pytest                              # Run tests
black backend/                      # Format code
flake8 backend/                     # Lint code
mypy backend/                       # Type check
```

### Frontend
```bash
npm run dev                         # Start dev server
npm run build                       # Build production
npm test                            # Run tests
npm run lint                        # Lint code
npm run format                      # Format code
```

### Docker
```bash
docker-compose up --build           # Start all services
docker-compose down                 # Stop services
docker-compose logs -f api          # View backend logs
docker-compose logs -f frontend     # View frontend logs
```

## 📝 Adding Features

### Add Backend Endpoint
1. Create function in `backend/api/` file
2. Use `@router.post()` or `@router.get()` decorator
3. Add Pydantic model for request/response
4. Include in router registration in `main.py`

### Add Frontend Component
1. Create `.tsx` file in `backend/src/components/`
2. Export as `export const Component: React.FC<Props> = ...`
3. Import and use in page/container

### Add API Call
1. Add method to `frontend/src/services/api.ts`
2. Use `apiClient.post()` or `apiClient.get()`
3. Call from component using `await apiClient.methodName()`

### Add State
1. Create store in `frontend/src/stores/`
2. Use `create<StateType>()` from Zustand
3. Import in component: `const { state, action } = useStore()`

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Port in use | Change `API_PORT=8001` or kill process |
| Module not found | Activate venv, reinstall: `pip install -r requirements.txt` |
| CORS errors | Add URL to `CORS_ORIGINS` in `backend/config/settings.py` |
| API not responding | Check backend running: `curl http://localhost:8000/health` |
| Frontend blank | Check browser console (F12), check `.env.local` |
| npm errors | Delete `node_modules/`, reinstall: `npm install` |
| Build fails | Check Python/Node versions, clear caches |

## 📚 Documentation Map

```
INDEX.md              ← Start here (navigation)
  ├─ README.md       ← Project overview
  ├─ DEVELOPMENT.md  ← How to develop
  ├─ ARCHITECTURE.md ← How it's built
  ├─ VISUAL_GUIDE.md ← Data flow diagrams
  ├─ CHECKLIST.md    ← Verification steps
  └─ SETUP_COMPLETE.md ← What was created
```

## 🔑 Environment Variables

### Backend (`.env`)
```
API_PORT=8000               Backend port
API_HOST=0.0.0.0           Bind address
DEBUG=True                 Debug mode
RELOAD=True                Auto-reload
OPENAI_API_KEY=...         Required
DEFAULT_MODEL=gpt-4-turbo  AI model
WORKSPACE_ROOT=./workspace Local path
LOG_LEVEL=INFO             Logging
```

### Frontend (`.env.local`)
```
VITE_API_URL=http://localhost:8000/api
```

## 🔍 Useful URLs

```
Local Frontend:    http://localhost:3000
Local Backend:     http://localhost:8000
API Docs:          http://localhost:8000/docs
Health Check:      http://localhost:8000/health
```

## 📊 Key Technologies

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend | FastAPI | 0.104 |
| Server | Uvicorn | 0.24 |
| Frontend | React | 18.2 |
| Build | Vite | 5.0 |
| Language | TypeScript | 5.3 |
| Styling | Tailwind | 3.3 |
| State | Zustand | 4.4 |
| HTTP | Axios | 1.6 |

## ✅ Daily Workflow

1. **Start servers** (2 terminals)
   ```bash
   # Terminal 1: Backend
   python -m backend.main
   
   # Terminal 2: Frontend
   cd frontend && npm run dev
   ```

2. **Make changes**
   - Backend: Edit `.py` files → auto-reloads
   - Frontend: Edit `.tsx` files → auto-refreshes

3. **Test changes**
   - Backend: http://localhost:8000/docs
   - Frontend: http://localhost:3000

4. **Run tests**
   ```bash
   pytest              # Backend tests
   npm test            # Frontend tests
   ```

5. **Format code**
   ```bash
   black backend/      # Backend
   npm run format      # Frontend
   ```

## 🎯 Common Tasks

### Run Specific Test
```bash
pytest tests/test_chat.py::test_send_message
```

### Format Single File
```bash
black backend/api/chat.py
```

### View API Response
```bash
curl http://localhost:8000/health
```

### Check Port Usage
```bash
# Windows
netstat -ano | findstr :8000

# macOS/Linux
lsof -i :8000
```

### Kill Process on Port
```bash
# Windows
taskkill /PID <PID> /F

# macOS/Linux
kill -9 <PID>
```

## 🚀 Deploy with Docker

```bash
# Build and start
docker-compose up --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Clean everything
docker-compose down -v
```

## 📞 Getting Help

1. **Error in console?** Read the error message carefully
2. **CORS issue?** Check CORS_ORIGINS in settings.py
3. **API not working?** Test in /docs endpoint first
4. **Component not rendering?** Check React DevTools
5. **Can't connect?** Verify both servers are running

Check **DEVELOPMENT.md** for detailed troubleshooting.

---

**Save this file for quick reference during development!**

Last Updated: November 9, 2025
