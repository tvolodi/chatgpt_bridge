"""
Settings Service for AI Chat Assistant

Service for managing user preferences, application configuration,
and system settings with persistence and validation.
"""

import json
import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import uuid
import hashlib
from dotenv import set_key, dotenv_values

from backend.models.settings import (
    Settings, SettingsCreate, SettingsUpdate, SettingsSummary,
    SettingsValidationResult, SettingsExport, SettingsImport,
    SettingsBackup, UserPreferences, AIModelSettings,
    APIProviderSettings, FileProcessingSettings,
    PrivacySettings, SystemSettings
)


class SettingsService:
    """Service for managing application settings and user preferences"""

    def __init__(self, base_path: str = None):
        """
        Initialize settings service

        Args:
            base_path: Base directory for storing settings. Defaults to user config directory.
        """
        if base_path is None:
            # Use platform-appropriate config directory
            if os.name == 'nt':  # Windows
                base_path = os.path.join(os.environ.get('APPDATA', ''), 'AI_Chat_Assistant')
            else:  # Unix-like systems
                base_path = os.path.join(os.path.expanduser('~'), '.config', 'ai_chat_assistant')

        self.base_path = Path(base_path)
        self.settings_path = self.base_path / "settings"
        self.backups_path = self.base_path / "backups"

        # Ensure directories exist
        self.settings_path.mkdir(parents=True, exist_ok=True)
        self.backups_path.mkdir(parents=True, exist_ok=True)

        # In-memory cache (must be initialized BEFORE _ensure_default_settings)
        self._settings_cache: Dict[str, Settings] = {}
        
        # Initialize default settings if they don't exist
        self._ensure_default_settings()

        # Load all settings into cache
        self._load_settings_cache()

    def _ensure_default_settings(self):
        """Ensure default settings exist and return them"""
        default_settings_path = self.settings_path / "default.json"

        if not default_settings_path.exists():
            default_settings = Settings(
                id="default",
                user_id=None,  # Global settings
                name="Default Settings",
                description="Default application settings",
                user_preferences=UserPreferences(),
                ai_model_settings=AIModelSettings(),
                api_providers=[],  # Will be populated by user
                file_processing=FileProcessingSettings(),
                privacy=PrivacySettings(),
                system=SystemSettings()
            )

            self._save_settings_to_file(default_settings, default_settings_path)
            self._settings_cache["default"] = default_settings
            return default_settings
        
        # Load from cache if available
        if "default" in self._settings_cache:
            return self._settings_cache["default"]
        
        # Load from file
        default_settings = self._load_settings_from_file(default_settings_path)
        if default_settings:
            self._settings_cache["default"] = default_settings
        return default_settings

    def _load_settings_cache(self):
        """Load all settings into memory cache"""
        self._settings_cache.clear()

        for settings_file in self.settings_path.glob("*.json"):
            try:
                settings_data = self._load_settings_from_file(settings_file)
                if settings_data:
                    self._settings_cache[settings_data.id] = settings_data
            except Exception:
                # Skip corrupted settings files
                continue

    def _get_settings_file_path(self, settings_id: str) -> Path:
        """Get file path for settings"""
        return self.settings_path / f"{settings_id}.json"

    def _load_settings_from_file(self, file_path: Path) -> Optional[Settings]:
        """Load settings from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Settings(**data)
        except Exception:
            return None

    def _save_settings_to_file(self, settings: Settings, file_path: Path):
        """Save settings to JSON file"""
        data = settings.model_dump()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate checksum for settings data"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _create_backup(self, settings: Settings, reason: str = "auto") -> SettingsBackup:
        """Create a backup of settings"""
        backup = SettingsBackup(
            settings_id=settings.id,
            backup_data=settings.model_dump(),
            reason=reason
        )

        # Create filename-safe timestamp (replace colons and other invalid chars)
        timestamp = datetime.now().isoformat().replace(':', '-').replace('.', '-')
        backup_file = self.backups_path / f"backup_{settings.id}_{timestamp}.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup.model_dump(), f, indent=2, default=str)

        # Clean up old backups (keep last 10)
        backup_files = sorted(self.backups_path.glob(f"backup_{settings.id}_*.json"))
        if len(backup_files) > 10:
            for old_backup in backup_files[:-10]:
                old_backup.unlink()

        return backup

    def _validate_settings(self, settings: Settings) -> SettingsValidationResult:
        """Validate settings configuration"""
        errors = []
        warnings = []

        # Validate API providers
        provider_names = set()
        for provider in settings.api_providers:
            if provider.provider_name in provider_names:
                errors.append(f"Duplicate API provider: {provider.provider_name}")
            provider_names.add(provider.provider_name)

            if provider.enabled and not provider.api_key:
                warnings.append(f"API provider '{provider.provider_name}' is enabled but has no API key")

        # Validate file processing settings
        if settings.file_processing.max_file_size < 1024:
            errors.append("Maximum file size must be at least 1KB")

        # Validate AI model settings
        if settings.ai_model_settings.temperature < 0 or settings.ai_model_settings.temperature > 2:
            errors.append("AI temperature must be between 0 and 2")

        # Validate system settings
        if settings.system.cache_ttl_seconds < 60:
            warnings.append("Cache TTL is very short (< 1 minute)")

        return SettingsValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def get_settings(self, settings_id: str) -> Optional[Settings]:
        """
        Get settings by ID

        Args:
            settings_id: Settings identifier

        Returns:
            Settings object if found
        """
        return self._settings_cache.get(settings_id)

    def get_default_settings(self) -> Settings:
        """
        Get default application settings

        Returns:
            Default settings
        """
        # Try to get from cache first
        if "default" in self._settings_cache:
            return self._settings_cache["default"]
        
        # If not in cache, ensure it exists and return it
        return self._ensure_default_settings()

    def get_user_settings(self, user_id: str) -> Optional[Settings]:
        """
        Get settings for a specific user

        Args:
            user_id: User identifier

        Returns:
            User settings if found, None otherwise
        """
        for settings in self._settings_cache.values():
            if settings.user_id == user_id and settings.is_active:
                return settings
        return None

    def list_settings(self, user_id: Optional[str] = None) -> List[SettingsSummary]:
        """
        List all settings, optionally filtered by user

        Args:
            user_id: Filter by user ID (optional)

        Returns:
            List of settings summaries
        """
        summaries = []

        for settings in self._settings_cache.values():
            if user_id is None or settings.user_id == user_id:
                summaries.append(SettingsSummary(
                    id=settings.id,
                    user_id=settings.user_id,
                    name=settings.name,
                    description=settings.description,
                    is_active=settings.is_active,
                    created_at=settings.created_at,
                    updated_at=settings.updated_at
                ))

        return sorted(summaries, key=lambda x: x.created_at, reverse=True)

    def create_settings(self, settings_create: SettingsCreate) -> Settings:
        """
        Create new settings

        Args:
            settings_create: Settings creation data

        Returns:
            Created settings
        """
        settings = Settings(
            user_id=settings_create.user_id,
            name=settings_create.name,
            description=settings_create.description,
            user_preferences=settings_create.user_preferences or UserPreferences(),
            ai_model_settings=settings_create.ai_model_settings or AIModelSettings(),
            api_providers=settings_create.api_providers or [],
            file_processing=settings_create.file_processing or FileProcessingSettings(),
            privacy=settings_create.privacy or PrivacySettings(),
            system=settings_create.system or SystemSettings()
        )

        # Validate settings
        validation = self._validate_settings(settings)
        if not validation.is_valid:
            raise ValueError(f"Invalid settings: {', '.join(validation.errors)}")

        # Save to file
        file_path = self._get_settings_file_path(settings.id)
        self._save_settings_to_file(settings, file_path)

        # Update cache
        self._settings_cache[settings.id] = settings

        return settings

    def update_settings(self, settings_id: str, settings_update: SettingsUpdate) -> Optional[Settings]:
        """
        Update existing settings

        Args:
            settings_id: Settings identifier
            settings_update: Update data

        Returns:
            Updated settings if found
        """
        settings = self._settings_cache.get(settings_id)
        if not settings:
            return None

        # Create backup before update
        self._create_backup(settings, "before_update")

        # Apply updates
        update_data = settings_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(settings, key):
                current_value = getattr(settings, key)
                if hasattr(current_value, 'model_copy'):
                    # It's a Pydantic model, update it properly
                    if isinstance(value, dict):
                        setattr(settings, key, current_value.model_copy(update=value))
                    else:
                        setattr(settings, key, value)
                else:
                    # Regular attribute
                    setattr(settings, key, value)

        settings.updated_at = datetime.now()

        # Validate updated settings
        validation = self._validate_settings(settings)
        if not validation.is_valid:
            raise ValueError(f"Invalid settings: {', '.join(validation.errors)}")

        # Save to file
        file_path = self._get_settings_file_path(settings_id)
        self._save_settings_to_file(settings, file_path)

        # Update cache
        self._settings_cache[settings_id] = settings

        return settings

    def delete_settings(self, settings_id: str) -> bool:
        """
        Delete settings

        Args:
            settings_id: Settings identifier

        Returns:
            True if deleted
        """
        if settings_id == "default":
            raise ValueError("Cannot delete default settings")

        settings = self._settings_cache.get(settings_id)
        if not settings:
            return False

        # Create backup before deletion
        self._create_backup(settings, "before_deletion")

        # Remove file
        file_path = self._get_settings_file_path(settings_id)
        if file_path.exists():
            file_path.unlink()

        # Remove from cache
        del self._settings_cache[settings_id]

        return True

    def duplicate_settings(self, settings_id: str, name: str, user_id: Optional[str] = None) -> Optional[Settings]:
        """
        Duplicate existing settings

        Args:
            settings_id: Source settings identifier
            name: Name for duplicated settings
            user_id: User ID for duplicated settings

        Returns:
            Duplicated settings if source found
        """
        source_settings = self._settings_cache.get(settings_id)
        if not source_settings:
            return None

        # Create duplicate
        duplicate = Settings(
            user_id=user_id,
            name=name,
            description=f"Copy of {source_settings.name}",
            user_preferences=source_settings.user_preferences.model_copy(),
            ai_model_settings=source_settings.ai_model_settings.model_copy(),
            api_providers=[p.model_copy() for p in source_settings.api_providers],
            file_processing=source_settings.file_processing.model_copy(),
            privacy=source_settings.privacy.model_copy(),
            system=source_settings.system.model_copy()
        )

        # Save duplicate
        file_path = self._get_settings_file_path(duplicate.id)
        self._save_settings_to_file(duplicate, file_path)

        # Update cache
        self._settings_cache[duplicate.id] = duplicate

        return duplicate

    def export_settings(self, settings_id: str) -> Optional[SettingsExport]:
        """
        Export settings to portable format

        Args:
            settings_id: Settings identifier

        Returns:
            Export data if settings found
        """
        settings = self._settings_cache.get(settings_id)
        if not settings:
            return None

        data = settings.model_dump()
        checksum = self._calculate_checksum(data)

        return SettingsExport(
            settings=settings,
            checksum=checksum
        )

    def import_settings(self, import_data: SettingsImport) -> Settings:
        """
        Import settings from export data

        Args:
            import_data: Import data

        Returns:
            Imported settings
        """
        # Validate import data
        try:
            settings_data = import_data.settings
            settings = Settings(**settings_data)
        except Exception as e:
            raise ValueError(f"Invalid import data: {str(e)}")

        # Check if settings already exist
        existing = self._settings_cache.get(settings.id)
        if existing and not import_data.overwrite_existing:
            raise ValueError(f"Settings with ID {settings.id} already exist")

        # Validate settings
        validation = self._validate_settings(settings)
        if not validation.is_valid:
            raise ValueError(f"Invalid settings: {', '.join(validation.errors)}")

        if import_data.validate_only:
            return settings

        # Save imported settings
        file_path = self._get_settings_file_path(settings.id)
        self._save_settings_to_file(settings, file_path)

        # Update cache
        self._settings_cache[settings.id] = settings

        return settings

    def validate_settings_data(self, settings_data: Dict[str, Any]) -> SettingsValidationResult:
        """
        Validate settings data without creating settings

        Args:
            settings_data: Settings data to validate

        Returns:
            Validation result
        """
        try:
            settings = Settings(**settings_data)
            return self._validate_settings(settings)
        except Exception as e:
            return SettingsValidationResult(
                is_valid=False,
                errors=[f"Invalid settings format: {str(e)}"]
            )

    def get_api_provider_settings(self, provider_name: str, user_id: Optional[str] = None) -> Optional[APIProviderSettings]:
        """
        Get API provider settings

        Args:
            provider_name: Provider name
            user_id: User ID (optional, uses default if not specified)

        Returns:
            Provider settings if found
        """
        settings = self.get_user_settings(user_id) if user_id else self.get_default_settings()

        for provider in settings.api_providers:
            if provider.provider_name == provider_name and provider.enabled:
                # Try to load API key from .env file for security
                # If a key is stored in .env, use that instead of the in-memory value
                api_key = self._load_api_key_from_env(provider_name)
                if api_key:
                    provider.api_key = api_key
                return provider

        return None

    def update_api_provider_settings(self, provider_name: str, provider_settings: APIProviderSettings, user_id: Optional[str] = None) -> bool:
        """
        Update API provider settings

        Args:
            provider_name: Provider name
            provider_settings: New provider settings
            user_id: User ID (optional, uses default if not specified)

        Returns:
            True if updated
        """
        settings = self.get_user_settings(user_id) if user_id else self.get_default_settings()
        if not settings:
            return False

        # Find and update provider
        for i, provider in enumerate(settings.api_providers):
            if provider.provider_name == provider_name:
                settings.api_providers[i] = provider_settings
                settings.updated_at = datetime.now()

                # Save and update cache
                file_path = self._get_settings_file_path(settings.id)
                self._save_settings_to_file(settings, file_path)
                self._settings_cache[settings.id] = settings
                
                # Save API key to .env file for secure storage
                if provider_settings.api_key:
                    self._save_api_key_to_env(provider_name, provider_settings.api_key)

                return True

        # Provider not found, add it
        settings.api_providers.append(provider_settings)
        settings.updated_at = datetime.now()

        # Save and update cache
        file_path = self._get_settings_file_path(settings.id)
        self._save_settings_to_file(settings, file_path)
        self._settings_cache[settings.id] = settings
        
        # Save API key to .env file for secure storage
        if provider_settings.api_key:
            self._save_api_key_to_env(provider_name, provider_settings.api_key)

        return True

    def _save_api_key_to_env(self, provider_name: str, api_key: str):
        """
        Save API key to .env file securely.
        
        Args:
            provider_name: Name of the provider (e.g., 'openai', 'anthropic')
            api_key: The API key to save
        """
        try:
            env_file_path = Path('.env')
            # Generate environment variable name: PROVIDER_API_KEY_<PROVIDER_NAME>
            env_var_name = f"PROVIDER_API_KEY_{provider_name.upper().replace(' ', '_').replace('-', '_')}"
            
            print(f"DEBUG: Saving API key to .env")
            print(f"DEBUG: env_file_path = {env_file_path}")
            print(f"DEBUG: env_var_name = {env_var_name}")
            print(f"DEBUG: api_key = {'*' * 10}")
            
            # Set the environment variable in the .env file
            set_key(str(env_file_path), env_var_name, api_key)
            print(f"DEBUG: Successfully saved API key to .env")
        except Exception as e:
            print(f"WARNING: Could not save API key to .env file: {e}")
            import traceback
            traceback.print_exc()

    def _load_api_key_from_env(self, provider_name: str) -> Optional[str]:
        """
        Load API key from .env file.
        
        Args:
            provider_name: Name of the provider (e.g., 'openai', 'anthropic')
            
        Returns:
            API key if found in .env file, None otherwise
        """
        try:
            env_file_path = Path('.env')
            if not env_file_path.exists():
                return None
                
            # Generate environment variable name: PROVIDER_API_KEY_<PROVIDER_NAME>
            env_var_name = f"PROVIDER_API_KEY_{provider_name.upper().replace(' ', '_').replace('-', '_')}"
            
            # Load environment variables from .env file
            env_values = dotenv_values(str(env_file_path))
            api_key = env_values.get(env_var_name)
            
            if api_key:
                print(f"DEBUG: Loaded API key from .env for {provider_name}")
            
            return api_key
        except Exception as e:
            print(f"WARNING: Could not load API key from .env file: {e}")
            return None

    def reset_to_defaults(self, settings_id: str) -> Optional[Settings]:
        """
        Reset settings to default values

        Args:
            settings_id: Settings identifier

        Returns:
            Reset settings if found
        """
        settings = self._settings_cache.get(settings_id)
        if not settings or settings_id == "default":
            return None

        # Create backup
        self._create_backup(settings, "before_reset")

        # Reset to defaults
        default_settings = self.get_default_settings()
        settings.user_preferences = default_settings.user_preferences.model_copy()
        settings.ai_model_settings = default_settings.ai_model_settings.model_copy()
        settings.file_processing = default_settings.file_processing.model_copy()
        settings.privacy = default_settings.privacy.model_copy()
        settings.system = default_settings.system.model_copy()
        settings.updated_at = datetime.now()

        # Save and update cache
        file_path = self._get_settings_file_path(settings_id)
        self._save_settings_to_file(settings, file_path)
        self._settings_cache[settings_id] = settings

        return settings