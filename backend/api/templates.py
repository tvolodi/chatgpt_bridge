from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from backend.services.message_template_service import MessageTemplateService
from backend.models.message_template import (
    MessageTemplate, MessageTemplateCreate, MessageTemplateUpdate,
    MessageTemplateSummary, TemplateCategory
)

# Create router
router = APIRouter(prefix="/api/templates", tags=["templates"])

# Dependency to get template service
def get_template_service() -> MessageTemplateService:
    """Dependency to get template service instance"""
    return MessageTemplateService()


@router.get("/", response_model=List[MessageTemplateSummary])
async def list_templates(
    project_id: Optional[str] = None,
    category: Optional[str] = None,
    template_service: MessageTemplateService = Depends(get_template_service)
):
    """
    List all templates, optionally filtered by project or category.

    - **project_id**: Filter by project ID (optional)
    - **category**: Filter by category (optional)
    - Returns list of template summaries
    """
    try:
        return template_service.list_templates(project_id, category)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list templates: {str(e)}")


@router.post("/", response_model=MessageTemplate)
async def create_template(
    template: MessageTemplateCreate,
    template_service: MessageTemplateService = Depends(get_template_service)
):
    """
    Create a new message template.

    - **name**: Template name (required, 1-100 characters)
    - **content**: Template content with optional placeholders (required, 1-10000 characters)
    - **category**: Template category (optional, defaults to 'general')
    - **project_id**: Associated project ID for project-specific templates (optional)
    - **description**: Template description (optional)
    - Returns created template
    """
    try:
        return template_service.create_template(template)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")


@router.get("/{template_id}", response_model=MessageTemplate)
async def get_template(
    template_id: str,
    template_service: MessageTemplateService = Depends(get_template_service)
):
    """
    Get a specific template by ID.

    - **template_id**: Template identifier
    - Returns template details
    """
    try:
        template = template_service.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get template: {str(e)}")


@router.put("/{template_id}", response_model=MessageTemplate)
async def update_template(
    template_id: str,
    template_update: MessageTemplateUpdate,
    template_service: MessageTemplateService = Depends(get_template_service)
):
    """
    Update an existing template.

    - **template_id**: Template identifier
    - **name**: Template name (optional)
    - **content**: Template content (optional)
    - **category**: Template category (optional)
    - **project_id**: Associated project ID (optional)
    - **description**: Template description (optional)
    - Returns updated template
    """
    try:
        updated_template = template_service.update_template(template_id, template_update)
        if not updated_template:
            raise HTTPException(status_code=404, detail="Template not found")
        return updated_template
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update template: {str(e)}")


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    template_service: MessageTemplateService = Depends(get_template_service)
):
    """
    Delete a template.

    - **template_id**: Template identifier
    - Returns success message
    """
    try:
        deleted = template_service.delete_template(template_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Template not found")
        return {"message": "Template deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete template: {str(e)}")


@router.get("/categories/", response_model=List[TemplateCategory])
async def get_template_categories(
    template_service: MessageTemplateService = Depends(get_template_service)
):
    """
    Get all template categories with template counts.

    - Returns list of categories with counts
    """
    try:
        return template_service.get_categories()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")


@router.post("/{template_id}/substitute")
async def substitute_template_parameters(
    template_id: str,
    parameters: Dict[str, str],
    template_service: MessageTemplateService = Depends(get_template_service)
):
    """
    Substitute parameters in a template and return the result.

    - **template_id**: Template identifier
    - **parameters**: Dictionary of parameter names to values
    - Returns substituted content
    """
    try:
        template = template_service.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        substituted_content = template_service.substitute_parameters(template.content, parameters)
        return {
            "template_id": template_id,
            "original_content": template.content,
            "substituted_content": substituted_content,
            "placeholders_found": template_service.get_template_placeholders(template.content)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to substitute parameters: {str(e)}")


@router.get("/{template_id}/placeholders")
async def get_template_placeholders(
    template_id: str,
    template_service: MessageTemplateService = Depends(get_template_service)
):
    """
    Get all placeholders found in a template.

    - **template_id**: Template identifier
    - Returns list of placeholder names
    """
    try:
        template = template_service.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        placeholders = template_service.get_template_placeholders(template.content)
        return {
            "template_id": template_id,
            "placeholders": placeholders
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get placeholders: {str(e)}")