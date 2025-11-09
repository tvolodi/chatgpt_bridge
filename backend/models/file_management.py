"""
File Management Service Data Models

This module defines the Pydantic models for file management,
document handling, and context integration within the AI Chat Assistant.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class FileType(str, Enum):
    """Supported file types."""
    TEXT = "text"
    PDF = "pdf"
    DOCX = "docx"
    MARKDOWN = "markdown"
    JSON = "json"
    CSV = "csv"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    OTHER = "other"


class FileStatus(str, Enum):
    """File processing status."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    DELETED = "deleted"


class FileMetadata(BaseModel):
    """Metadata for uploaded files."""

    model_config = ConfigDict(from_attributes=True)

    filename: str = Field(..., description="Original filename")
    file_type: FileType = Field(..., description="Type of file")
    mime_type: str = Field(..., description="MIME type")
    size_bytes: int = Field(..., description="File size in bytes")
    encoding: Optional[str] = Field(None, description="Text encoding if applicable")
    language: Optional[str] = Field(None, description="Detected language")
    checksum: str = Field(..., description="File checksum for integrity")
    page_count: Optional[int] = Field(None, description="Number of pages (for PDFs, docs)")
    word_count: Optional[int] = Field(None, description="Word count (for text files)")
    character_count: Optional[int] = Field(None, description="Character count")
    extracted_text: Optional[str] = Field(None, description="Extracted text content")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL if applicable")
    additional_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional file-specific metadata")


class File(BaseModel):
    """Represents a file in the system."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the file")
    project_id: Optional[UUID] = Field(None, description="Associated project ID")
    session_id: Optional[UUID] = Field(None, description="Associated chat session ID")
    filename: str = Field(..., description="Original filename")
    file_path: str = Field(..., description="Internal file path")
    status: FileStatus = Field(default=FileStatus.UPLOADED, description="Processing status")
    metadata: FileMetadata = Field(..., description="File metadata")
    tags: List[str] = Field(default_factory=list, description="User-defined tags")
    is_public: bool = Field(default=False, description="Whether file is publicly accessible")
    created_at: datetime = Field(default_factory=datetime.now, description="When the file was uploaded")
    updated_at: datetime = Field(default_factory=datetime.now, description="When the file was last updated")
    processed_at: Optional[datetime] = Field(None, description="When the file was processed")
    expires_at: Optional[datetime] = Field(None, description="When the file expires")

    def __str__(self) -> str:
        return f"File(id={self.id}, filename={self.filename}, status={self.status})"


class FileUploadRequest(BaseModel):
    """Request model for file upload."""

    project_id: Optional[UUID] = Field(None, description="Project to associate file with")
    session_id: Optional[UUID] = Field(None, description="Chat session to associate file with")
    tags: List[str] = Field(default_factory=list, description="Tags for the file")
    is_public: bool = Field(default=False, description="Whether file should be public")
    auto_process: bool = Field(default=True, description="Whether to automatically process the file")


class FileUploadResponse(BaseModel):
    """Response model for file upload."""

    file: File = Field(..., description="Uploaded file information")
    upload_url: Optional[str] = Field(None, description="Upload URL for direct upload")
    processing_status: str = Field(..., description="Current processing status")


class FileUpdateRequest(BaseModel):
    """Request model for updating file metadata."""

    filename: Optional[str] = Field(None, description="New filename")
    tags: Optional[List[str]] = Field(None, description="Updated tags")
    is_public: Optional[bool] = Field(None, description="Updated public status")
    project_id: Optional[UUID] = Field(None, description="New project association")
    session_id: Optional[UUID] = Field(None, description="New session association")


class FileSearchRequest(BaseModel):
    """Request model for file search."""

    query: Optional[str] = Field(None, description="Search query")
    project_id: Optional[UUID] = Field(None, description="Filter by project")
    session_id: Optional[UUID] = Field(None, description="Filter by session")
    file_type: Optional[FileType] = Field(None, description="Filter by file type")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    status: Optional[FileStatus] = Field(None, description="Filter by status")
    date_from: Optional[datetime] = Field(None, description="Filter by creation date from")
    date_to: Optional[datetime] = Field(None, description="Filter by creation date to")
    limit: int = Field(default=50, ge=1, le=1000, description="Maximum results")
    offset: int = Field(default=0, ge=0, description="Results offset")


class FileSummary(BaseModel):
    """Summary representation of a file."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="File ID")
    filename: str = Field(..., description="Filename")
    file_type: FileType = Field(..., description="File type")
    size_bytes: int = Field(..., description="File size")
    status: FileStatus = Field(..., description="Processing status")
    project_id: Optional[UUID] = Field(None, description="Associated project")
    session_id: Optional[UUID] = Field(None, description="Associated session")
    tags: List[str] = Field(..., description="File tags")
    created_at: datetime = Field(..., description="Creation date")
    processed_at: Optional[datetime] = Field(None, description="Processing date")


class FileContent(BaseModel):
    """File content with metadata."""

    file: File = Field(..., description="File information")
    content: Optional[str] = Field(None, description="Extracted text content")
    content_type: str = Field(..., description="Content MIME type")
    encoding: Optional[str] = Field(None, description="Text encoding")


class FileContextRequest(BaseModel):
    """Request for file context in conversations."""

    session_id: UUID = Field(..., description="Chat session ID")
    file_ids: List[UUID] = Field(..., description="Files to include in context")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for context")
    include_metadata: bool = Field(default=True, description="Include file metadata")
    relevance_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Relevance threshold for content")


class FileContext(BaseModel):
    """File context for AI conversations."""

    file_id: UUID = Field(..., description="File ID")
    filename: str = Field(..., description="Filename")
    content: str = Field(..., description="Relevant content excerpt")
    relevance_score: float = Field(..., description="Relevance score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="File metadata")
    token_count: int = Field(..., description="Token count of content")


class ConversationContextWithFiles(BaseModel):
    """Conversation context including relevant files."""

    session_id: UUID = Field(..., description="Chat session ID")
    message_context: List[Dict[str, Any]] = Field(..., description="Message history")
    file_contexts: List[FileContext] = Field(..., description="Relevant file contexts")
    total_tokens: int = Field(..., description="Total token count")
    truncated: bool = Field(default=False, description="Whether context was truncated")


class FileStats(BaseModel):
    """Statistics for file management."""

    total_files: int = Field(..., description="Total number of files")
    total_size_bytes: int = Field(..., description="Total storage used")
    files_by_type: Dict[str, int] = Field(default_factory=dict, description="Files by type")
    files_by_status: Dict[str, int] = Field(default_factory=dict, description="Files by status")
    recent_uploads: int = Field(..., description="Files uploaded in last 24 hours")
    processing_queue: int = Field(..., description="Files waiting for processing")
    failed_files: int = Field(..., description="Files that failed processing")


class FileProcessingResult(BaseModel):
    """Result of file processing."""

    file_id: UUID = Field(..., description="Processed file ID")
    success: bool = Field(..., description="Whether processing succeeded")
    extracted_text: Optional[str] = Field(None, description="Extracted text content")
    metadata_updates: Dict[str, Any] = Field(default_factory=dict, description="Updated metadata")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    processing_time: float = Field(..., description="Processing time in seconds")


class FileError(BaseModel):
    """Error model for file operations."""

    type: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    file_id: Optional[UUID] = Field(None, description="File ID if applicable")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")