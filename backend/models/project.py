from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import os
from pathlib import Path


class ProjectBase(BaseModel):
    """Base project model with common fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    description: Optional[str] = Field(None, max_length=500, description="Project description")
    parent_id: Optional[str] = Field(None, description="Parent project ID for nested projects")


class ProjectCreate(ProjectBase):
    """Model for creating new projects"""
    pass


class ProjectUpdate(BaseModel):
    """Model for updating existing projects"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[str] = Field(None)


class Project(ProjectBase):
    """Full project model with metadata"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique project identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Project creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Project last update timestamp")
    path: str = Field(..., description="Absolute path to project directory")

    model_config = ConfigDict(from_attributes=True)


class ProjectTree(BaseModel):
    """Model for project hierarchy/tree representation"""
    project: Project
    children: List['ProjectTree'] = Field(default_factory=list, description="Nested child projects")


class ProjectSummary(BaseModel):
    """Summary view of project for listings"""
    id: str
    name: str
    description: Optional[str]
    parent_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    has_children: bool = Field(default=False, description="Whether project has child projects")
    children_count: int = Field(default=0, description="Number of direct child projects")


class ProjectStats(BaseModel):
    """Statistics for a project"""
    total_projects: int = Field(..., description="Total number of projects")
    total_sessions: int = Field(..., description="Total chat sessions across all projects")
    total_messages: int = Field(..., description="Total messages across all sessions")
    total_files: int = Field(..., description="Total files in project workspaces")
    storage_size: int = Field(..., description="Total storage size in bytes")