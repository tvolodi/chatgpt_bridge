"""
Configuration Settings for AI Chat Assistant Backend
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings"""
    
    # API Configuration
    API_TITLE: str = "AI Chat Assistant API"
    API_VERSION: str = "0.1.0"
    API_DESCRIPTION: str = "FastAPI backend for AI Chat Assistant"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    HOST: str = os.getenv("API_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("API_PORT", "8000"))
    RELOAD: bool = os.getenv("RELOAD", "True").lower() == "true"
    
    # CORS Configuration
    CORS_ORIGINS: list = [
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8000",  # API itself
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # AI Provider Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-4-turbo")
    
    # Memory Configuration
    MEMORY_FILE: str = os.getenv("MEMORY_FILE", "data/ai_dala_memory.json")
    MEMORY_REFRESH_HOURS: int = int(os.getenv("MEMORY_REFRESH_HOURS", "12"))
    
    # Workspace Configuration
    WORKSPACE_ROOT: str = os.getenv("WORKSPACE_ROOT", "./workspace")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    ALLOWED_EXTENSIONS: list = [
        ".txt", ".md", ".py", ".js", ".ts", ".json", ".yaml", ".yml",
        ".html", ".css", ".java", ".cpp", ".c", ".rs", ".go"
    ]
    IGNORED_DIRS: list = [".git", ".venv", "venv", "node_modules", "__pycache__", ".env"]
    
    # Connector Configuration (for Notion, GitHub, etc.)
    NOTION_TOKEN: Optional[str] = os.getenv("NOTION_TOKEN")
    NOTION_ROOT_PAGE_ID: Optional[str] = os.getenv("NOTION_ROOT_PAGE_ID")
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Server-Sent Events (for streaming responses)
    SSE_TIMEOUT: int = int(os.getenv("SSE_TIMEOUT", "300"))


settings = Settings()
