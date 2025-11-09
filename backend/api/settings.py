"""
Settings API for AI Chat Assistant

REST API endpoints for managing user preferences, application configuration,
and system settings.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List, Optional
from backend.services.settings_service import SettingsService
from backend.models.settings import (
    Settings, SettingsCreate, SettingsUpdate, SettingsSummary,
    SettingsValidationResult, SettingsExport, SettingsImport,
    APIProviderSettings
)

# Create router
router = APIRouter(prefix="/api/settings", tags=["settings"])

# Dependency to get settings service
def get_settings_service() -> SettingsService:
    """Dependency to get settings service instance"""
    return SettingsService()


@router.get("/", response_model=List[SettingsSummary])
async def list_settings(
    user_id: Optional[str] = None,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """
    List all settings profiles, optionally filtered by user.

    - **user_id**: Filter by user ID (optional)
    - Returns list of settings summaries
    """
    try:
        return settings_service.list_settings(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list settings: {str(e)}")


@router.get("/default", response_model=Settings)
async def get_default_settings(
    settings_service: SettingsService = Depends(get_settings_service)
):
    """
    Get default application settings.

    - Returns default settings configuration
    """
    try:
        return settings_service.get_default_settings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get default settings: {str(e)}")


@router.get("/user/{user_id}", response_model=Optional[Settings])
async def get_user_settings(
    user_id: str,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """
    Get settings for a specific user.

    - **user_id**: User identifier
    - Returns user settings if found
    """
    try:
        settings = settings_service.get_user_settings(user_id)
        if settings is None:
            raise HTTPException(status_code=404, detail="User settings not found")
        return settings
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user settings: {str(e)}")


@router.get("/{settings_id}", response_model=Settings)
async def get_settings(
    settings_id: str,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """
    Get settings by ID.

    - **settings_id**: Settings identifier
    - Returns settings configuration
    """
    try:
        settings = settings_service.get_settings(settings_id)
        if settings is None:
            raise HTTPException(status_code=404, detail="Settings not found")
        return settings
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get settings: {str(e)}")


@router.post("/", response_model=Settings)
async def create_settings(
    settings: SettingsCreate,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """
    Create new settings profile.

    - **settings**: Settings configuration
    - Returns created settings
    """
    try:
        return settings_service.create_settings(settings)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create settings: {str(e)}")


@router.put("/{settings_id}", response_model=Settings)
async def update_settings(
    settings_id: str,
    settings_update: SettingsUpdate,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """
    Update existing settings.

    - **settings_id**: Settings identifier
    - **settings_update**: Updated settings data
    - Returns updated settings
    """
    try:
        updated = settings_service.update_settings(settings_id, settings_update)
        if updated is None:
            raise HTTPException(status_code=404, detail="Settings not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")


@router.delete("/{settings_id}")
async def delete_settings(
    settings_id: str,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """
    Delete settings profile.

    - **settings_id**: Settings identifier
    - Returns success message
    """
    try:
        deleted = settings_service.delete_settings(settings_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Settings not found")
        return {"message": "Settings deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete settings: {str(e)}")


@router.post("/{settings_id}/duplicate", response_model=Settings)
async def duplicate_settings(
    settings_id: str,
    name: str,
    user_id: Optional[str] = None,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """
    Duplicate existing settings profile.

    - **settings_id**: Source settings identifier
    - **name**: Name for duplicated settings
    - **user_id**: User ID for duplicated settings (optional)
    - Returns duplicated settings
    """
    try:
        duplicated = settings_service.duplicate_settings(settings_id, name, user_id)
        if duplicated is None:
            raise HTTPException(status_code=404, detail="Source settings not found")
        return duplicated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to duplicate settings: {str(e)}")


@router.get("/{settings_id}/export", response_model=SettingsExport)
async def export_settings(
    settings_id: str,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """
    Export settings to portable format.

    - **settings_id**: Settings identifier
    - Returns export data
    """
    try:
        export_data = settings_service.export_settings(settings_id)
        if export_data is None:
            raise HTTPException(status_code=404, detail="Settings not found")
        return export_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export settings: {str(e)}")


@router.post("/import", response_model=Settings)
async def import_settings(
    import_data: SettingsImport,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """
    Import settings from export data.

    - **import_data**: Import configuration and data
    - Returns imported settings
    """
    try:
        return settings_service.import_settings(import_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import settings: {str(e)}")


@router.post("/validate", response_model=SettingsValidationResult)
async def validate_settings(
    settings_data: dict,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """
    Validate settings data without saving.

    - **settings_data**: Settings data to validate
    - Returns validation result
    """
    try:
        return settings_service.validate_settings_data(settings_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate settings: {str(e)}")


@router.get("/api-providers/{provider_name}", response_model=Optional[APIProviderSettings])
async def get_api_provider_settings(
    provider_name: str,
    user_id: Optional[str] = None,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """
    Get API provider settings.

    - **provider_name**: Provider name (e.g., 'openai', 'anthropic')
    - **user_id**: User ID (optional, uses default if not specified)
    - Returns provider settings if found
    """
    try:
        return settings_service.get_api_provider_settings(provider_name, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get API provider settings: {str(e)}")


@router.put("/api-providers/{provider_name}", response_model=dict)
async def update_api_provider_settings(
    provider_name: str,
    provider_settings: APIProviderSettings,
    user_id: Optional[str] = None,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """
    Update API provider settings.

    - **provider_name**: Provider name
    - **provider_settings**: New provider configuration
    - **user_id**: User ID (optional, uses default if not specified)
    - Returns success status
    """
    try:
        success = settings_service.update_api_provider_settings(provider_name, provider_settings, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Settings not found")
        return {"message": "API provider settings updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update API provider settings: {str(e)}")


@router.post("/{settings_id}/reset", response_model=Settings)
async def reset_settings_to_defaults(
    settings_id: str,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """
    Reset settings to default values.

    - **settings_id**: Settings identifier
    - Returns reset settings
    """
    try:
        reset = settings_service.reset_to_defaults(settings_id)
        if reset is None:
            raise HTTPException(status_code=404, detail="Settings not found or cannot reset default settings")
        return reset
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset settings: {str(e)}")


@router.get("/user/{user_id}/effective", response_model=Settings)
async def get_effective_user_settings(
    user_id: str,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """
    Get effective settings for a user (user settings merged with defaults).

    - **user_id**: User identifier
    - Returns effective settings configuration
    """
    try:
        user_settings = settings_service.get_user_settings(user_id)
        default_settings = settings_service.get_default_settings()

        if user_settings:
            # In a real implementation, you'd merge user settings with defaults
            # For now, just return user settings
            return user_settings
        else:
            # Return default settings if no user settings exist
            return default_settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get effective user settings: {str(e)}")


@router.get("/categories/{category}", response_model=dict)
async def get_settings_category(
    category: str,
    settings_id: Optional[str] = None,
    user_id: Optional[str] = None,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """
    Get specific settings category.

    - **category**: Settings category (user_preferences, ai_model_settings, etc.)
    - **settings_id**: Specific settings ID (optional)
    - **user_id**: User ID (optional)
    - Returns category settings
    """
    try:
        # Determine which settings to use
        settings = None
        if settings_id:
            settings = settings_service.get_settings(settings_id)
        elif user_id:
            settings = settings_service.get_user_settings(user_id)
        else:
            settings = settings_service.get_default_settings()

        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")

        # Get the requested category
        valid_categories = [
            "user_preferences", "ai_model_settings", "api_providers",
            "file_processing", "privacy", "system"
        ]

        if category not in valid_categories:
            raise HTTPException(status_code=400, detail=f"Invalid category. Valid categories: {', '.join(valid_categories)}")

        category_data = getattr(settings, category)
        return {category: category_data.model_dump()}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get settings category: {str(e)}")


@router.put("/categories/{category}", response_model=dict)
async def update_settings_category(
    category: str,
    category_data: dict,
    settings_id: Optional[str] = None,
    user_id: Optional[str] = None,
    settings_service: SettingsService = Depends(get_settings_service)
):
    """
    Update specific settings category.

    - **category**: Settings category to update
    - **category_data**: New category data
    - **settings_id**: Specific settings ID (optional)
    - **user_id**: User ID (optional)
    - Returns success status
    """
    try:
        # Determine which settings to update
        settings = None
        target_id = None

        if settings_id:
            settings = settings_service.get_settings(settings_id)
            target_id = settings_id
        elif user_id:
            settings = settings_service.get_user_settings(user_id)
            if settings:
                target_id = settings.id
        else:
            settings = settings_service.get_default_settings()
            target_id = settings.id

        if not settings or not target_id:
            raise HTTPException(status_code=404, detail="Settings not found")

        # Validate category
        valid_categories = [
            "user_preferences", "ai_model_settings", "api_providers",
            "file_processing", "privacy", "system"
        ]

        if category not in valid_categories:
            raise HTTPException(status_code=400, detail=f"Invalid category. Valid categories: {', '.join(valid_categories)}")

        # Create update object
        update_dict = {category: category_data}
        settings_update = SettingsUpdate(**update_dict)

        # Update settings
        updated = settings_service.update_settings(target_id, settings_update)
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update settings category")

        return {"message": f"{category} updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings category: {str(e)}")