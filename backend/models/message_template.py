from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class MessageTemplateBase(BaseModel):
    """Base message template model with common fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    content: str = Field(..., min_length=1, max_length=10000, description="Template content with optional placeholders")
    category: str = Field(default="general", min_length=1, max_length=50, description="Template category (general, coding, writing, etc.)")
    project_id: Optional[str] = Field(None, description="Associated project ID, None for global templates")
    description: Optional[str] = Field(None, max_length=500, description="Template description")


class MessageTemplateCreate(MessageTemplateBase):
    """Model for creating new message templates"""
    pass


class MessageTemplateUpdate(BaseModel):
    """Model for updating existing message templates"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = Field(None, min_length=1, max_length=10000)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    project_id: Optional[str] = Field(None)
    description: Optional[str] = Field(None, max_length=500)


class MessageTemplate(MessageTemplateBase):
    """Full message template model with metadata"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique template identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Template creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Template last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class MessageTemplateSummary(BaseModel):
    """Summary view of template for listings"""
    id: str
    name: str
    category: str
    description: Optional[str]
    project_id: Optional[str]
    created_at: datetime
    updated_at: datetime


class TemplateCategory(BaseModel):
    """Model for template categories"""
    name: str = Field(..., description="Category name")
    count: int = Field(default=0, description="Number of templates in this category")
    description: Optional[str] = Field(None, description="Category description")


class TemplateSubstitution(BaseModel):
    """Model for template parameter substitution"""
    placeholder: str = Field(..., description="Placeholder in template (e.g., {{name}})")
    value: str = Field(..., description="Value to substitute")
    description: Optional[str] = Field(None, description="Description of what this placeholder represents")