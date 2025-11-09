"""
Settings Models for AI Chat Assistant

Comprehensive data models for user preferences, application configuration,
and system settings management.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from enum import Enum
import uuid


class Theme(str, Enum):
    """UI theme options"""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class Language(str, Enum):
    """Supported languages"""
    EN = "en"
    ES = "es"
    FR = "fr"
    DE = "de"
    IT = "it"
    PT = "pt"
    RU = "ru"
    JA = "ja"
    KO = "ko"
    ZH = "zh"


class MessageDisplayMode(str, Enum):
    """How messages are displayed in conversations"""
    COMPACT = "compact"
    COMFORTABLE = "comfortable"
    BUBBLES = "bubbles"


class NotificationLevel(str, Enum):
    """Notification preference levels"""
    ALL = "all"
    IMPORTANT = "important"
    NONE = "none"


class ExportFormat(str, Enum):
    """Supported export formats"""
    JSON = "json"
    PDF = "pdf"
    TXT = "txt"
    HTML = "html"
    MD = "markdown"


class UserPreferences(BaseModel):
    """User interface and experience preferences"""
    theme: Theme = Field(default=Theme.SYSTEM, description="UI theme preference")
    language: Language = Field(default=Language.EN, description="Interface language")
    message_display_mode: MessageDisplayMode = Field(
        default=MessageDisplayMode.COMFORTABLE,
        description="How messages are displayed"
    )
    font_size: int = Field(default=14, ge=10, le=24, description="Font size in pixels")
    auto_save: bool = Field(default=True, description="Auto-save conversations")
    auto_save_interval: int = Field(default=30, ge=5, le=300, description="Auto-save interval in seconds")
    show_timestamps: bool = Field(default=True, description="Show message timestamps")
    show_typing_indicators: bool = Field(default=True, description="Show typing indicators")
    sound_enabled: bool = Field(default=True, description="Enable notification sounds")
    notification_level: NotificationLevel = Field(
        default=NotificationLevel.ALL,
        description="Notification preference level"
    )
    max_conversation_history: int = Field(
        default=1000,
        ge=10,
        le=10000,
        description="Maximum messages to keep in conversation history"
    )
    default_export_format: ExportFormat = Field(
        default=ExportFormat.JSON,
        description="Default format for exporting conversations"
    )

    model_config = ConfigDict(from_attributes=True)


class AIModelSettings(BaseModel):
    """AI model configuration settings"""
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Model temperature")
    max_tokens: int = Field(default=2048, ge=1, le=32768, description="Maximum tokens per response")
    top_p: float = Field(default=1.0, ge=0.0, le=1.0, description="Top-p sampling parameter")
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0, description="Frequency penalty")
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0, description="Presence penalty")
    system_prompt: Optional[str] = Field(
        default=None,
        max_length=10000,
        description="Custom system prompt"
    )
    context_window_size: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Number of previous messages to include in context"
    )

    @field_validator('system_prompt')
    @classmethod
    def validate_system_prompt(cls, v):
        if v and len(v.strip()) == 0:
            return None
        return v


class APIProviderSettings(BaseModel):
    """Settings for AI API providers"""
    provider_name: str = Field(..., description="Provider name (e.g., 'openai', 'anthropic')")
    api_key: Optional[str] = Field(default=None, description="API key for the provider")
    base_url: Optional[str] = Field(default=None, description="Custom base URL for API calls")
    timeout: int = Field(default=60, ge=10, le=300, description="Request timeout in seconds")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum retry attempts")
    rate_limit_requests: int = Field(
        default=60,
        ge=1,
        le=1000,
        description="Requests per minute rate limit"
    )
    rate_limit_window: int = Field(
        default=60,
        ge=1,
        le=3600,
        description="Rate limit window in seconds"
    )
    enabled: bool = Field(default=True, description="Whether this provider is enabled")
    priority: int = Field(default=1, ge=1, le=10, description="Provider priority (lower = higher priority)")

    model_config = ConfigDict(from_attributes=True)


class FileProcessingSettings(BaseModel):
    """Settings for file processing and management"""
    max_file_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        ge=1024,
        le=100 * 1024 * 1024,  # 100MB
        description="Maximum file size in bytes"
    )
    allowed_extensions: List[str] = Field(
        default_factory=lambda: [
            ".txt", ".md", ".pdf", ".docx", ".doc", ".rtf",
            ".jpg", ".jpeg", ".png", ".gif", ".webp",
            ".mp3", ".wav", ".mp4", ".avi", ".mov",
            ".json", ".csv", ".xml", ".yaml", ".yml"
        ],
        description="Allowed file extensions"
    )
    auto_process_files: bool = Field(
        default=True,
        description="Automatically process uploaded files"
    )
    enable_ocr: bool = Field(
        default=False,
        description="Enable OCR for image files"
    )
    max_concurrent_processes: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum concurrent file processing operations"
    )
    processing_timeout: int = Field(
        default=300,
        ge=30,
        le=1800,
        description="File processing timeout in seconds"
    )


class PrivacySettings(BaseModel):
    """Privacy and data protection settings"""
    enable_analytics: bool = Field(
        default=False,
        description="Enable anonymous usage analytics"
    )
    enable_error_reporting: bool = Field(
        default=True,
        description="Enable automatic error reporting"
    )
    data_retention_days: int = Field(
        default=365,
        ge=30,
        le=3650,
        description="Days to retain conversation data"
    )
    auto_delete_old_conversations: bool = Field(
        default=False,
        description="Automatically delete old conversations"
    )
    encrypt_sensitive_data: bool = Field(
        default=True,
        description="Encrypt sensitive data at rest"
    )
    allow_data_export: bool = Field(
        default=True,
        description="Allow users to export their data"
    )


class SystemSettings(BaseModel):
    """System-level configuration settings"""
    log_level: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Logging level"
    )
    enable_debug_mode: bool = Field(
        default=False,
        description="Enable debug mode for development"
    )
    backup_enabled: bool = Field(
        default=True,
        description="Enable automatic backups"
    )
    backup_interval_hours: int = Field(
        default=24,
        ge=1,
        le=168,
        description="Backup interval in hours"
    )
    max_backup_count: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of backups to keep"
    )
    enable_performance_monitoring: bool = Field(
        default=False,
        description="Enable performance monitoring"
    )
    cache_enabled: bool = Field(
        default=True,
        description="Enable response caching"
    )
    cache_ttl_seconds: int = Field(
        default=3600,
        ge=60,
        le=86400,
        description="Cache time-to-live in seconds"
    )


class Settings(BaseModel):
    """Complete settings configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Settings identifier")
    user_id: Optional[str] = Field(default=None, description="User identifier (None for global settings)")
    name: str = Field(default="Default Settings", description="Settings profile name")
    description: Optional[str] = Field(default=None, description="Settings description")

    # Settings categories
    user_preferences: UserPreferences = Field(default_factory=UserPreferences)
    ai_model_settings: AIModelSettings = Field(default_factory=AIModelSettings)
    api_providers: List[APIProviderSettings] = Field(default_factory=list)
    file_processing: FileProcessingSettings = Field(default_factory=FileProcessingSettings)
    privacy: PrivacySettings = Field(default_factory=PrivacySettings)
    system: SystemSettings = Field(default_factory=SystemSettings)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: str = Field(default="1.0.0", description="Settings schema version")
    is_active: bool = Field(default=True, description="Whether these settings are active")

    model_config = ConfigDict(from_attributes=True)


class SettingsCreate(BaseModel):
    """Model for creating new settings"""
    user_id: Optional[str] = None
    name: str = "Default Settings"
    description: Optional[str] = None
    user_preferences: Optional[UserPreferences] = None
    ai_model_settings: Optional[AIModelSettings] = None
    api_providers: Optional[List[APIProviderSettings]] = None
    file_processing: Optional[FileProcessingSettings] = None
    privacy: Optional[PrivacySettings] = None
    system: Optional[SystemSettings] = None


class SettingsUpdate(BaseModel):
    """Model for updating existing settings"""
    name: Optional[str] = None
    description: Optional[str] = None
    user_preferences: Optional[UserPreferences] = None
    ai_model_settings: Optional[AIModelSettings] = None
    api_providers: Optional[List[APIProviderSettings]] = None
    file_processing: Optional[FileProcessingSettings] = None
    privacy: Optional[PrivacySettings] = None
    system: Optional[SystemSettings] = None
    is_active: Optional[bool] = None


class SettingsSummary(BaseModel):
    """Summary view of settings for listings"""
    id: str
    user_id: Optional[str]
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SettingsValidationResult(BaseModel):
    """Result of settings validation"""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class SettingsExport(BaseModel):
    """Settings export format"""
    settings: Settings
    exported_at: datetime = Field(default_factory=datetime.now)
    export_version: str = "1.0.0"
    checksum: Optional[str] = None


class SettingsImport(BaseModel):
    """Settings import format"""
    settings: Dict[str, Any]
    import_version: str
    overwrite_existing: bool = False
    validate_only: bool = False


class SettingsBackup(BaseModel):
    """Settings backup information"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    settings_id: str
    backup_data: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.now)
    reason: Optional[str] = None  # e.g., "auto", "manual", "before_import"