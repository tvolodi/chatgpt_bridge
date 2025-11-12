import json
import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from backend.models.project import (
    Project, ProjectCreate, ProjectUpdate,
    ProjectTree, ProjectSummary, ProjectStats
)


class ProjectService:
    """Service for managing projects, nested hierarchies, and workspaces"""

    def __init__(self, base_path: str = None, data_dir: str = None):
        """
        Initialize project service

        Args:
            base_path: Base directory for storing projects. Defaults to user's home directory.
            data_dir: Alias for base_path for backwards compatibility. If provided, overrides base_path.
        """
        # Support both base_path and data_dir parameter names for backwards compatibility
        if data_dir is not None:
            base_path = data_dir
        if base_path is None:
            base_path = os.path.join(os.path.expanduser("~"), "AI_Chat_Assistant_Projects")
        self.base_path = Path(base_path)
        self.projects_path = self.base_path / "projects"
        self.metadata_path = self.base_path / "metadata"

        # Ensure directories exist
        self.projects_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path.mkdir(parents=True, exist_ok=True)

        # Initialize default project if it doesn't exist
        self._ensure_default_project()

    def _ensure_default_project(self):
        """Ensure the default project exists"""
        default_project_path = self.projects_path / "default"
        default_metadata_path = self.metadata_path / "default.json"

        if not default_metadata_path.exists():
            default_project = Project(
                id="default",
                name="Default Project",
                description="Default project for general conversations",
                parent_id=None,
                path=str(default_project_path),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            # Create project directory
            default_project_path.mkdir(exist_ok=True)

            # Save metadata
            self._save_project_metadata(default_project)

    def _get_project_metadata_path(self, project_id: str) -> Path:
        """Get path to project metadata file"""
        return self.metadata_path / f"{project_id}.json"

    def _save_project_metadata(self, project: Project):
        """Save project metadata to JSON file"""
        metadata_path = self._get_project_metadata_path(project.id)
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(project.model_dump(), f, indent=2, default=str)

    def _load_project_metadata(self, project_id: str) -> Optional[Project]:
        """Load project metadata from JSON file"""
        metadata_path = self._get_project_metadata_path(project_id)
        if not metadata_path.exists():
            return None

        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Project(**data)
        except (json.JSONDecodeError, KeyError):
            return None

    def _get_project_directory(self, project_id: str) -> Path:
        """Get project directory path"""
        return self.projects_path / project_id

    def _validate_project_name(self, name: str) -> bool:
        """Validate project name"""
        if not name or len(name.strip()) == 0:
            return False
        if len(name) > 100:
            return False
        # Check for invalid characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        return not any(char in name for char in invalid_chars)

    def _validate_parent_project(self, parent_id: str) -> bool:
        """Validate that parent project exists"""
        if parent_id is None:
            return True
        return self._load_project_metadata(parent_id) is not None

    def _check_circular_reference(self, project_id: str, parent_id: str) -> bool:
        """Check for circular references in project hierarchy"""
        if parent_id is None:
            return False

        current_id = parent_id
        visited = set([project_id])

        while current_id:
            if current_id in visited:
                return True  # Circular reference detected
            visited.add(current_id)

            parent_project = self._load_project_metadata(current_id)
            if not parent_project:
                break
            current_id = parent_project.parent_id

        return False

    def create_project(self, project_data: ProjectCreate) -> Project:
        """
        Create a new project

        Args:
            project_data: Project creation data

        Returns:
            Created project

        Raises:
            ValueError: If validation fails
        """
        # Validate name
        if not self._validate_project_name(project_data.name):
            raise ValueError("Invalid project name")

        # Validate parent project
        if not self._validate_parent_project(project_data.parent_id):
            raise ValueError("Parent project does not exist")

        # Generate unique ID
        project_id = str(uuid.uuid4())

        # Check for circular reference (in case of updates)
        if self._check_circular_reference(project_id, project_data.parent_id):
            raise ValueError("Circular reference detected in project hierarchy")

        # Create project directory
        project_dir = self._get_project_directory(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)

        # Create project object
        project = Project(
            id=project_id,
            name=project_data.name.strip(),
            description=project_data.description,
            parent_id=project_data.parent_id,
            path=str(project_dir)
        )

        # Save metadata
        self._save_project_metadata(project)

        return project

    def get_project(self, project_id: str) -> Optional[Project]:
        """
        Get project by ID

        Args:
            project_id: Project identifier

        Returns:
            Project if found, None otherwise
        """
        return self._load_project_metadata(project_id)

    def list_projects(self, parent_id: Optional[str] = None) -> List[ProjectSummary]:
        """
        List all projects, optionally filtered by parent

        Args:
            parent_id: Filter by parent project ID, None for all projects

        Returns:
            List of project summaries
        """
        projects = []

        for metadata_file in self.metadata_path.glob("*.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                project = Project(**data)

                # Filter by parent if specified
                if parent_id is not None and project.parent_id != parent_id:
                    continue

                # Get children count
                children_count = len(self._get_child_projects(project.id))

                summary = ProjectSummary(
                    id=project.id,
                    name=project.name,
                    description=project.description,
                    parent_id=project.parent_id,
                    created_at=project.created_at,
                    updated_at=project.updated_at,
                    has_children=children_count > 0,
                    children_count=children_count
                )

                projects.append(summary)

            except (json.JSONDecodeError, KeyError):
                continue

        # Sort by creation date (newest first)
        projects.sort(key=lambda p: p.created_at, reverse=True)
        return projects

    def update_project(self, project_id: str, update_data: ProjectUpdate) -> Optional[Project]:
        """
        Update project information

        Args:
            project_id: Project identifier
            update_data: Update data

        Returns:
            Updated project if found, None otherwise

        Raises:
            ValueError: If validation fails
        """
        project = self._load_project_metadata(project_id)
        if not project:
            return None

        # Validate name if provided
        if update_data.name is not None:
            if not self._validate_project_name(update_data.name):
                raise ValueError("Invalid project name")
            project.name = update_data.name.strip()

        # Validate parent if provided
        if update_data.parent_id is not None:
            if not self._validate_parent_project(update_data.parent_id):
                raise ValueError("Parent project does not exist")

            # Check for circular reference
            if self._check_circular_reference(project_id, update_data.parent_id):
                raise ValueError("Circular reference detected in project hierarchy")

            project.parent_id = update_data.parent_id

        # Update other fields
        if update_data.description is not None:
            project.description = update_data.description

        project.updated_at = datetime.now()

        # Save updated metadata
        self._save_project_metadata(project)

        return project

    def delete_project(self, project_id: str, force: bool = False) -> bool:
        """
        Delete a project and all its contents

        Args:
            project_id: Project identifier
            force: Force deletion even if project has children

        Returns:
            True if deleted, False if not found

        Raises:
            ValueError: If project has children and force=False
        """
        if project_id == "default":
            raise ValueError("Cannot delete default project")

        project = self._load_project_metadata(project_id)
        if not project:
            return False

        # Check for child projects
        child_projects = self._get_child_projects(project_id)
        if child_projects and not force:
            raise ValueError(f"Project has {len(child_projects)} child projects. Use force=True to delete.")

        # Delete child projects recursively
        for child_id in child_projects:
            self.delete_project(child_id, force=True)

        # Delete project directory
        project_dir = self._get_project_directory(project_id)
        if project_dir.exists():
            shutil.rmtree(project_dir)

        # Delete metadata file
        metadata_path = self._get_project_metadata_path(project_id)
        if metadata_path.exists():
            metadata_path.unlink()

        return True

    def get_project_tree(self, root_project_id: Optional[str] = None) -> List[ProjectTree]:
        """
        Get project hierarchy as a tree structure

        Args:
            root_project_id: Root project ID, None for all roots

        Returns:
            List of project trees
        """
        def build_tree(project_id: str) -> ProjectTree:
            project = self._load_project_metadata(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")

            children = []
            for child_id in self._get_child_projects(project_id):
                children.append(build_tree(child_id))

            return ProjectTree(project=project, children=children)

        if root_project_id:
            return [build_tree(root_project_id)]
        else:
            # Get all root projects (no parent)
            roots = []
            for summary in self.list_projects():
                if summary.parent_id is None:
                    roots.append(build_tree(summary.id))
            return roots

    def _get_child_projects(self, parent_id: str) -> List[str]:
        """Get list of child project IDs for a given parent"""
        children = []
        for metadata_file in self.metadata_path.glob("*.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if data.get('parent_id') == parent_id:
                    children.append(data['id'])

            except (json.JSONDecodeError, KeyError):
                continue

        return children

    def get_project_stats(self) -> ProjectStats:
        """
        Get overall project statistics

        Returns:
            Project statistics
        """
        total_projects = 0
        total_sessions = 0
        total_messages = 0
        total_files = 0
        storage_size = 0

        # Count projects
        for metadata_file in self.metadata_path.glob("*.json"):
            total_projects += 1

        # Calculate storage size (simplified - just count files and directories)
        try:
            for path in self.base_path.rglob('*'):
                if path.is_file():
                    total_files += 1
                    storage_size += path.stat().st_size
        except (OSError, PermissionError):
            pass

        return ProjectStats(
            total_projects=total_projects,
            total_sessions=total_sessions,  # Will be updated when session service is implemented
            total_messages=total_messages,  # Will be updated when conversation service is implemented
            total_files=total_files,
            storage_size=storage_size
        )