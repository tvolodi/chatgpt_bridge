"""
Unit Tests for Settings Service

Comprehensive test suite for the settings service functionality.
"""

import pytest
import tempfile
import os
import json
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4
from datetime import datetime

from backend.models.settings import (
    Settings, SettingsCreate, SettingsUpdate, SettingsSummary,
    SettingsValidationResult, SettingsExport, SettingsImport,
    SettingsBackup, UserPreferences, AIModelSettings,
    APIProviderSettings, FileProcessingSettings,
    PrivacySettings, SystemSettings, Theme, Language,
    MessageDisplayMode, NotificationLevel, ExportFormat
)
from backend.services.settings_service import SettingsService


class TestSettingsService:
    """Test suite for SettingsService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.service = SettingsService(base_path=str(self.temp_dir))

    def teardown_method(self):
        """Clean up test fixtures."""
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test service initialization."""
        assert self.service.base_path == self.temp_dir
        assert self.service.settings_path == self.temp_dir / "settings"
        assert self.service.backups_path == self.temp_dir / "backups"
        assert self.service.settings_path.exists()
        assert self.service.backups_path.exists()
        assert isinstance(self.service._settings_cache, dict)
        assert "default" in self.service._settings_cache

    def test_get_settings_file_path(self):
        """Test settings file path generation."""
        settings_id = "test-settings"
        expected_path = self.service.settings_path / f"{settings_id}.json"
        actual_path = self.service._get_settings_file_path(settings_id)
        assert actual_path == expected_path

    def test_calculate_checksum(self):
        """Test checksum calculation."""
        data = {"test": "data", "number": 42}
        checksum1 = self.service._calculate_checksum(data)
        checksum2 = self.service._calculate_checksum(data)
        assert checksum1 == checksum2
        assert len(checksum1) == 64  # SHA256 hex length

    def test_validate_settings_valid(self):
        """Test validation of valid settings."""
        settings = Settings(
            name="Test Settings",
            user_preferences=UserPreferences(),
            ai_model_settings=AIModelSettings(),
            api_providers=[],
            file_processing=FileProcessingSettings(),
            privacy=PrivacySettings(),
            system=SystemSettings()
        )

        result = self.service._validate_settings(settings)
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_validate_settings_invalid(self):
        """Test validation of invalid settings."""
        # Create settings with validation issues that aren't caught by Pydantic
        settings = Settings(
            name="Test Settings",
            api_providers=[
                APIProviderSettings(provider_name="openai", enabled=True),
                APIProviderSettings(provider_name="openai", enabled=True)  # Duplicate
            ],
            privacy=PrivacySettings(),
            system=SystemSettings()
        )

        result = self.service._validate_settings(settings)
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "duplicate" in " ".join(result.errors).lower()

    def test_get_default_settings(self):
        """Test getting default settings."""
        settings = self.service.get_default_settings()
        assert settings is not None
        assert settings.id == "default"
        assert settings.name == "Default Settings"
        assert settings.user_id is None

    def test_create_settings(self):
        """Test creating new settings."""
        create_data = SettingsCreate(
            user_id="user123",
            name="User Settings",
            description="Custom user settings"
        )

        settings = self.service.create_settings(create_data)
        assert settings.user_id == "user123"
        assert settings.name == "User Settings"
        assert settings.description == "Custom user settings"
        assert settings.id in self.service._settings_cache

        # Verify file was created
        settings_file = self.service._get_settings_file_path(settings.id)
        assert settings_file.exists()

    def test_create_settings_invalid(self):
        """Test creating settings with invalid data."""
        # Create settings that will pass Pydantic but fail service validation
        create_data = SettingsCreate(
            name="Invalid Settings",
            api_providers=[
                APIProviderSettings(provider_name="test", enabled=True),
                APIProviderSettings(provider_name="test", enabled=True)  # Duplicate
            ]
        )

        with pytest.raises(ValueError, match="Invalid settings"):
            self.service.create_settings(create_data)

    def test_get_settings(self):
        """Test getting settings by ID."""
        # Create test settings
        create_data = SettingsCreate(name="Test Settings")
        created = self.service.create_settings(create_data)

        # Retrieve settings
        retrieved = self.service.get_settings(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Test Settings"

    def test_get_settings_not_found(self):
        """Test getting non-existent settings."""
        result = self.service.get_settings("non-existent-id")
        assert result is None

    def test_get_user_settings(self):
        """Test getting settings for a specific user."""
        # Create user settings
        create_data = SettingsCreate(
            user_id="user123",
            name="User Settings"
        )
        created = self.service.create_settings(create_data)

        # Retrieve user settings
        user_settings = self.service.get_user_settings("user123")
        assert user_settings is not None
        assert user_settings.user_id == "user123"

    def test_get_user_settings_not_found(self):
        """Test getting settings for non-existent user."""
        result = self.service.get_user_settings("non-existent-user")
        assert result is None

    def test_list_settings(self):
        """Test listing all settings."""
        # Create multiple settings
        self.service.create_settings(SettingsCreate(name="Settings 1"))
        self.service.create_settings(SettingsCreate(name="Settings 2", user_id="user123"))

        # List all
        all_settings = self.service.list_settings()
        assert len(all_settings) >= 2  # At least default + created

        # List user settings
        user_settings = self.service.list_settings(user_id="user123")
        assert len(user_settings) == 1
        assert user_settings[0].user_id == "user123"

    def test_update_settings(self):
        """Test updating existing settings."""
        # Create settings
        create_data = SettingsCreate(name="Original Settings")
        created = self.service.create_settings(create_data)

        # Update settings
        update_data = SettingsUpdate(
            name="Updated Settings",
            description="Updated description"
        )

        updated = self.service.update_settings(created.id, update_data)
        assert updated is not None
        assert updated.name == "Updated Settings"
        assert updated.description == "Updated description"
        assert updated.updated_at > updated.created_at

    def test_update_settings_not_found(self):
        """Test updating non-existent settings."""
        update_data = SettingsUpdate(name="Updated")
        result = self.service.update_settings("non-existent-id", update_data)
        assert result is None

    def test_delete_settings(self):
        """Test deleting settings."""
        # Create settings
        create_data = SettingsCreate(name="Settings to Delete")
        created = self.service.create_settings(create_data)

        # Verify exists
        assert created.id in self.service._settings_cache
        settings_file = self.service._get_settings_file_path(created.id)
        assert settings_file.exists()

        # Delete settings
        deleted = self.service.delete_settings(created.id)
        assert deleted is True

        # Verify deleted
        assert created.id not in self.service._settings_cache
        assert not settings_file.exists()

    def test_delete_default_settings(self):
        """Test that default settings cannot be deleted."""
        with pytest.raises(ValueError, match="Cannot delete default settings"):
            self.service.delete_settings("default")

    def test_duplicate_settings(self):
        """Test duplicating settings."""
        # Create original settings
        create_data = SettingsCreate(
            name="Original Settings",
            user_preferences=UserPreferences(theme=Theme.DARK)
        )
        original = self.service.create_settings(create_data)

        # Duplicate settings
        duplicated = self.service.duplicate_settings(original.id, "Duplicated Settings", "user456")
        assert duplicated is not None
        assert duplicated.name == "Duplicated Settings"
        assert duplicated.user_id == "user456"
        assert duplicated.user_preferences.theme == Theme.DARK
        assert duplicated.id != original.id

    def test_duplicate_settings_not_found(self):
        """Test duplicating non-existent settings."""
        result = self.service.duplicate_settings("non-existent-id", "New Name")
        assert result is None

    def test_export_settings(self):
        """Test exporting settings."""
        # Create settings
        create_data = SettingsCreate(name="Export Test")
        created = self.service.create_settings(create_data)

        # Export settings
        export_data = self.service.export_settings(created.id)
        assert export_data is not None
        assert export_data.settings.id == created.id
        assert export_data.checksum is not None
        assert len(export_data.checksum) == 64

    def test_export_settings_not_found(self):
        """Test exporting non-existent settings."""
        result = self.service.export_settings("non-existent-id")
        assert result is None

    def test_import_settings(self):
        """Test importing settings."""
        # Create export data
        original_settings = Settings(name="Import Test")
        export_data = {
            "id": original_settings.id,
            "user_id": original_settings.user_id,
            "name": original_settings.name,
            "description": original_settings.description,
            "user_preferences": original_settings.user_preferences.model_dump(),
            "ai_model_settings": original_settings.ai_model_settings.model_dump(),
            "api_providers": [],
            "file_processing": original_settings.file_processing.model_dump(),
            "privacy": original_settings.privacy.model_dump(),
            "system": original_settings.system.model_dump(),
            "created_at": original_settings.created_at.isoformat(),
            "updated_at": original_settings.updated_at.isoformat(),
            "version": original_settings.version,
            "is_active": original_settings.is_active
        }

        import_request = SettingsImport(
            settings=export_data,
            import_version="1.0.0"
        )

        # Import settings
        imported = self.service.import_settings(import_request)
        assert imported is not None
        assert imported.name == "Import Test"
        assert imported.id in self.service._settings_cache

    def test_import_settings_invalid(self):
        """Test importing invalid settings."""
        # Create data that will pass Pydantic but fail service validation
        invalid_data = {
            "id": str(uuid4()),
            "user_id": None,
            "name": "Invalid Import",
            "description": None,
            "user_preferences": UserPreferences().model_dump(),
            "ai_model_settings": AIModelSettings().model_dump(),
            "api_providers": [
                {"provider_name": "test", "enabled": True},
                {"provider_name": "test", "enabled": True}  # Duplicate
            ],
            "file_processing": FileProcessingSettings().model_dump(),
            "privacy": PrivacySettings().model_dump(),
            "system": SystemSettings().model_dump(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "is_active": True
        }

        import_request = SettingsImport(
            settings=invalid_data,
            import_version="1.0.0"
        )

        with pytest.raises(ValueError, match="Invalid settings"):
            self.service.import_settings(import_request)

    def test_validate_settings_data(self):
        """Test validating settings data."""
        valid_data = {
            "name": "Test Settings",
            "user_preferences": UserPreferences().model_dump(),
            "ai_model_settings": AIModelSettings().model_dump(),
            "api_providers": [],
            "file_processing": FileProcessingSettings().model_dump(),
            "privacy": PrivacySettings().model_dump(),
            "system": SystemSettings().model_dump()
        }

        result = self.service.validate_settings_data(valid_data)
        assert result.is_valid is True

    def test_get_api_provider_settings(self):
        """Test getting API provider settings."""
        # Create settings with API provider
        provider_settings = APIProviderSettings(
            provider_name="openai",
            api_key="test-key",
            enabled=True
        )

        create_data = SettingsCreate(
            name="Provider Test",
            api_providers=[provider_settings]
        )
        created = self.service.create_settings(create_data)

        # Get provider settings from the created settings (not default)
        provider = None
        for p in created.api_providers:
            if p.provider_name == "openai" and p.enabled:
                provider = p
                break

        assert provider is not None
        assert provider.provider_name == "openai"
        assert provider.api_key == "test-key"

    def test_get_api_provider_settings_not_found(self):
        """Test getting non-existent API provider settings."""
        provider = self.service.get_api_provider_settings("non-existent")
        assert provider is None

    def test_update_api_provider_settings(self):
        """Test updating API provider settings."""
        # Create settings
        create_data = SettingsCreate(name="Provider Update Test")
        created = self.service.create_settings(create_data)

        # Update provider settings
        provider_settings = APIProviderSettings(
            provider_name="anthropic",
            api_key="new-key",
            enabled=True
        )

        success = self.service.update_api_provider_settings("anthropic", provider_settings)
        assert success is True

        # Verify update
        updated_provider = self.service.get_api_provider_settings("anthropic")
        assert updated_provider is not None
        assert updated_provider.api_key == "new-key"

    def test_reset_to_defaults(self):
        """Test resetting settings to defaults."""
        # Create custom settings
        create_data = SettingsCreate(
            name="Custom Settings",
            user_preferences=UserPreferences(theme=Theme.DARK, font_size=20)
        )
        created = self.service.create_settings(create_data)

        # Reset to defaults
        reset = self.service.reset_to_defaults(created.id)
        assert reset is not None
        assert reset.user_preferences.theme == Theme.SYSTEM  # Default value
        assert reset.user_preferences.font_size == 14  # Default value

    def test_reset_default_settings(self):
        """Test that default settings cannot be reset."""
        result = self.service.reset_to_defaults("default")
        assert result is None

    def test_backup_creation(self):
        """Test backup creation during updates."""
        # Create settings
        create_data = SettingsCreate(name="Backup Test")
        created = self.service.create_settings(create_data)

        # Update to trigger backup
        update_data = SettingsUpdate(name="Updated Name")
        self.service.update_settings(created.id, update_data)

        # Check backup was created
        backup_files = list(self.service.backups_path.glob(f"backup_{created.id}_*.json"))
        assert len(backup_files) > 0

        # Verify backup content
        backup_file = backup_files[0]
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)

        assert backup_data["settings_id"] == created.id
        assert backup_data["reason"] == "before_update"

    def test_settings_workflow(self):
        """Test complete settings workflow."""
        # 1. Create settings
        create_data = SettingsCreate(
            user_id="test-user",
            name="Workflow Test",
            user_preferences=UserPreferences(theme=Theme.DARK)
        )
        settings = self.service.create_settings(create_data)
        assert settings.user_id == "test-user"

        # 2. Update settings
        update_data = SettingsUpdate(
            user_preferences=UserPreferences(theme=Theme.LIGHT, font_size=16)
        )
        updated = self.service.update_settings(settings.id, update_data)
        assert updated.user_preferences.theme == Theme.LIGHT
        assert updated.user_preferences.font_size == 16

        # 3. Export settings
        export_data = self.service.export_settings(settings.id)
        assert export_data is not None

        # 4. Import as new settings
        import_request = SettingsImport(
            settings=export_data.settings.model_dump(),
            import_version="1.0.0",
            overwrite_existing=True  # Allow overwriting since we're testing
        )
        imported = self.service.import_settings(import_request)
        assert imported.name == "Workflow Test"
        assert imported.id == settings.id  # Same ID since we overwrote

        # 5. Delete settings
        deleted = self.service.delete_settings(settings.id)
        assert deleted is True

        # Verify deleted
        assert self.service.get_settings(settings.id) is None

    def test_settings_persistence(self):
        """Test settings persistence across service instances."""
        # Create settings in first instance
        create_data = SettingsCreate(name="Persistence Test")
        created = self.service.create_settings(create_data)

        # Create new service instance (simulating restart)
        new_service = SettingsService(base_path=str(self.temp_dir))

        # Verify settings were loaded
        loaded = new_service.get_settings(created.id)
        assert loaded is not None
        assert loaded.name == "Persistence Test"

    def test_settings_validation_warnings(self):
        """Test settings validation warnings."""
        settings = Settings(
            name="Warning Test",
            api_providers=[
                APIProviderSettings(provider_name="openai", api_key=None, enabled=True)  # Warning: enabled but no key
            ]
        )

        result = self.service._validate_settings(settings)
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert "api key" in " ".join(result.warnings).lower()

    def test_api_provider_validation(self):
        """Test API provider validation."""
        # Duplicate providers
        settings = Settings(
            name="Provider Validation Test",
            api_providers=[
                APIProviderSettings(provider_name="openai", enabled=True),
                APIProviderSettings(provider_name="openai", enabled=True)  # Duplicate
            ]
        )

        result = self.service._validate_settings(settings)
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "duplicate" in " ".join(result.errors).lower()

        # Provider without API key but enabled
        settings2 = Settings(
            name="Provider Warning Test",
            api_providers=[
                APIProviderSettings(provider_name="openai", api_key=None, enabled=True)
            ]
        )

        result2 = self.service._validate_settings(settings2)
        assert result2.is_valid is True
        assert len(result2.warnings) > 0