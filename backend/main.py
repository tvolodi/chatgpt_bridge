"""
FastAPI Application Entry Point
Main server for AI Chat Assistant Backend
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.config.settings import settings
from backend.api import chat, files, workspace, projects, chat_sessions, ai_providers, conversations, file_management, settings as settings_api, search, user_state

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
)

# Add middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(projects.router)
app.include_router(chat_sessions.router)
app.include_router(ai_providers.router)
app.include_router(conversations.router)
app.include_router(file_management.router, prefix="/api/files", tags=["file-management"])
app.include_router(settings_api.router)
app.include_router(search.router)
app.include_router(user_state.router)
app.include_router(files.router, prefix="/api/workspace-files", tags=["workspace-files"])
app.include_router(workspace.router, prefix="/api/workspace", tags=["workspace"])


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.API_VERSION}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Chat Assistant API",
        "version": settings.API_VERSION,
        "docs": "/docs",
    }


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return {
        "error": str(exc),
        "type": type(exc).__name__,
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting {settings.API_TITLE}")
    logger.info(f"   Running on http://{settings.HOST}:{settings.PORT}")
    logger.info(f"   Debug mode: {settings.DEBUG}")
    logger.info(f"   API docs: http://{settings.HOST}:{settings.PORT}/docs")
    
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )
