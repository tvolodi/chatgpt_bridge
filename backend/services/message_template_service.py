import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import re

from backend.models.message_template import (
    MessageTemplate, MessageTemplateCreate, MessageTemplateUpdate,
    MessageTemplateSummary, TemplateCategory
)


class MessageTemplateService:
    """Service for managing message templates with categorization and parameter substitution"""

    def __init__(self, base_path: str = None, data_dir: str = None):
        """
        Initialize message template service

        Args:
            base_path: Base directory for storing templates. Defaults to user's home directory.
            data_dir: Alias for base_path for backwards compatibility. If provided, overrides base_path.
        """
        # Support both base_path and data_dir parameter names for backwards compatibility
        if data_dir is not None:
            base_path = data_dir
        if base_path is None:
            base_path = os.path.join(os.path.expanduser("~"), "AI_Chat_Assistant_Projects")
        self.base_path = Path(base_path)
        self.templates_path = self.base_path / "templates"
        self.metadata_path = self.base_path / "template_metadata"

        # Ensure directories exist
        self.templates_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path.mkdir(parents=True, exist_ok=True)

    def _get_template_metadata_path(self, template_id: str) -> Path:
        """Get path to template metadata file"""
        return self.metadata_path / f"{template_id}.json"

    def _save_template_metadata(self, template: MessageTemplate):
        """Save template metadata to JSON file"""
        metadata_path = self._get_template_metadata_path(template.id)
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(template.model_dump(), f, indent=2, default=str)

    def _load_template_metadata(self, template_id: str) -> Optional[MessageTemplate]:
        """Load template metadata from JSON file"""
        metadata_path = self._get_template_metadata_path(template_id)
        if not metadata_path.exists():
            return None

        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return MessageTemplate(**data)
        except (json.JSONDecodeError, KeyError):
            return None

    def _validate_template_name(self, name: str) -> bool:
        """Validate template name"""
        if not name or len(name.strip()) == 0:
            return False
        if len(name) > 100:
            return False
        # Check for invalid characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '/']
        return not any(char in name for char in invalid_chars)

    def _validate_template_content(self, content: str) -> bool:
        """Validate template content"""
        if not content or len(content.strip()) == 0:
            return False
        if len(content) > 10000:
            return False
        return True

    def create_template(self, template_data: MessageTemplateCreate) -> MessageTemplate:
        """
        Create a new message template

        Args:
            template_data: Template creation data

        Returns:
            Created template

        Raises:
            ValueError: If validation fails
        """
        # Validate name
        if not self._validate_template_name(template_data.name):
            raise ValueError("Invalid template name")

        # Validate content
        if not self._validate_template_content(template_data.content):
            raise ValueError("Invalid template content")

        # Generate unique ID
        template_id = str(uuid.uuid4())

        # Create template object
        template = MessageTemplate(
            id=template_id,
            name=template_data.name.strip(),
            content=template_data.content.strip(),
            category=template_data.category,
            project_id=template_data.project_id,
            description=template_data.description
        )

        # Save metadata
        self._save_template_metadata(template)

        return template

    def get_template(self, template_id: str) -> Optional[MessageTemplate]:
        """
        Get template by ID

        Args:
            template_id: Template identifier

        Returns:
            Template if found, None otherwise
        """
        return self._load_template_metadata(template_id)

    def list_templates(self, project_id: Optional[str] = None, category: Optional[str] = None) -> List[MessageTemplateSummary]:
        """
        List all templates, optionally filtered by project or category

        Args:
            project_id: Filter by project ID, None for all templates
            category: Filter by category, None for all categories

        Returns:
            List of template summaries
        """
        templates = []

        for metadata_file in self.metadata_path.glob("*.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                template = MessageTemplate(**data)

                # Filter by project if specified
                if project_id is not None and template.project_id != project_id:
                    continue

                # Filter by category if specified
                if category is not None and template.category != category:
                    continue

                summary = MessageTemplateSummary(
                    id=template.id,
                    name=template.name,
                    category=template.category,
                    description=template.description,
                    project_id=template.project_id,
                    created_at=template.created_at,
                    updated_at=template.updated_at
                )

                templates.append(summary)

            except (json.JSONDecodeError, KeyError):
                continue

        # Sort by creation date (newest first)
        templates.sort(key=lambda t: t.created_at, reverse=True)
        return templates

    def update_template(self, template_id: str, update_data: MessageTemplateUpdate) -> Optional[MessageTemplate]:
        """
        Update template information

        Args:
            template_id: Template identifier
            update_data: Update data

        Returns:
            Updated template if found, None otherwise

        Raises:
            ValueError: If validation fails
        """
        template = self._load_template_metadata(template_id)
        if not template:
            return None

        # Validate name if provided
        if update_data.name is not None:
            if not self._validate_template_name(update_data.name):
                raise ValueError("Invalid template name")
            template.name = update_data.name.strip()

        # Validate content if provided
        if update_data.content is not None:
            if not self._validate_template_content(update_data.content):
                raise ValueError("Invalid template content")
            template.content = update_data.content.strip()

        # Update other fields
        if update_data.category is not None:
            template.category = update_data.category
        if update_data.project_id is not None:
            template.project_id = update_data.project_id
        if update_data.description is not None:
            template.description = update_data.description

        template.updated_at = datetime.now()

        # Save updated metadata
        self._save_template_metadata(template)

        return template

    def delete_template(self, template_id: str) -> bool:
        """
        Delete a template

        Args:
            template_id: Template identifier

        Returns:
            True if deleted, False if not found
        """
        template = self._load_template_metadata(template_id)
        if not template:
            return False

        # Delete metadata file
        metadata_path = self._get_template_metadata_path(template_id)
        if metadata_path.exists():
            metadata_path.unlink()

        return True

    def get_categories(self) -> List[TemplateCategory]:
        """
        Get all template categories with counts

        Returns:
            List of categories with template counts
        """
        category_counts = {}

        for metadata_file in self.metadata_path.glob("*.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                category = data.get('category', 'general')
                category_counts[category] = category_counts.get(category, 0) + 1

            except (json.JSONDecodeError, KeyError):
                continue

        categories = []
        for category_name, count in category_counts.items():
            categories.append(TemplateCategory(
                name=category_name,
                count=count,
                description=self._get_category_description(category_name)
            ))

        # Sort by count (most used first)
        categories.sort(key=lambda c: c.count, reverse=True)
        return categories

    def _get_category_description(self, category: str) -> str:
        """Get description for a category"""
        descriptions = {
            'general': 'General purpose templates',
            'coding': 'Programming and development templates',
            'writing': 'Writing and content creation templates',
            'analysis': 'Data analysis and research templates',
            'business': 'Business and professional templates',
            'education': 'Educational and learning templates'
        }
        return descriptions.get(category, f'{category} templates')

    def substitute_parameters(self, template_content: str, parameters: Dict[str, str]) -> str:
        """
        Substitute parameters in template content

        Args:
            template_content: Template content with placeholders like {{variable}}
            parameters: Dictionary of parameter names to values

        Returns:
            Content with parameters substituted
        """
        def replace_placeholder(match):
            param_name = match.group(1)
            return parameters.get(param_name, match.group(0))  # Keep original if not found

        # Replace {{variable}} patterns
        pattern = r'\{\{(\w+)\}\}'
        return re.sub(pattern, replace_placeholder, template_content)

    def get_template_placeholders(self, template_content: str) -> List[str]:
        """
        Extract placeholder names from template content

        Args:
            template_content: Template content

        Returns:
            List of placeholder names found in the template
        """
        pattern = r'\{\{(\w+)\}\}'
        matches = re.findall(pattern, template_content)
        return list(set(matches))  # Remove duplicates