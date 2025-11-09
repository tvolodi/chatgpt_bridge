"""
File Management Service

This module provides comprehensive file management capabilities including
upload, processing, storage, search, and context integration for AI conversations.
"""

import os
import hashlib
import mimetypes
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any, BinaryIO, Union
from uuid import UUID, uuid4

from ..models.file_management import (
    File,
    FileType,
    FileStatus,
    FileMetadata,
    FileUploadRequest,
    FileUploadResponse,
    FileUpdateRequest,
    FileSearchRequest,
    FileSummary,
    FileContent,
    FileContextRequest,
    FileContext,
    ConversationContextWithFiles,
    FileStats,
    FileProcessingResult,
    FileError
)


class FileManagementService:
    """
    Service for managing files, documents, and context integration.

    This service handles file uploads, processing, storage, search, and
    provides context integration for AI conversations.
    """

    def __init__(
        self,
        storage_dir: Path = Path("data/files"),
        temp_dir: Path = Path("data/temp"),
        max_file_size: int = 50 * 1024 * 1024,  # 50MB
        allowed_extensions: Optional[List[str]] = None
    ):
        """
        Initialize the file management service.

        Args:
            storage_dir: Directory for storing files
            temp_dir: Directory for temporary files
            max_file_size: Maximum file size in bytes
            allowed_extensions: List of allowed file extensions
        """
        self.storage_dir = storage_dir
        self.temp_dir = temp_dir
        self.max_file_size = max_file_size
        self.allowed_extensions = allowed_extensions or [
            '.txt', '.pdf', '.docx', '.md', '.json', '.csv',
            '.jpg', '.jpeg', '.png', '.gif', '.webp',
            '.mp3', '.wav', '.mp4', '.avi'
        ]

        # Create directories
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # In-memory storage (in production, use database)
        self._files: Dict[UUID, File] = {}
        self._file_contents: Dict[UUID, str] = {}

        # Load existing files
        self._load_files()

    def _get_file_path(self, file_id: UUID, filename: str) -> Path:
        """Get the storage path for a file."""
        # Create subdirectory based on first 2 chars of UUID for organization
        subdir = str(file_id)[:2]
        return self.storage_dir / subdir / f"{file_id}_{filename}"

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def _detect_file_type(self, filename: str, mime_type: str) -> FileType:
        """Detect file type from filename and MIME type."""
        ext = Path(filename).suffix.lower()

        type_map = {
            '.txt': FileType.TEXT,
            '.md': FileType.MARKDOWN,
            '.json': FileType.JSON,
            '.csv': FileType.CSV,
            '.pdf': FileType.PDF,
            '.docx': FileType.DOCX,
            '.jpg': FileType.IMAGE,
            '.jpeg': FileType.IMAGE,
            '.png': FileType.IMAGE,
            '.gif': FileType.IMAGE,
            '.webp': FileType.IMAGE,
            '.mp3': FileType.AUDIO,
            '.wav': FileType.AUDIO,
            '.mp4': FileType.VIDEO,
            '.avi': FileType.VIDEO,
        }

        return type_map.get(ext, FileType.OTHER)

    def _extract_text_content(self, file_path: Path, file_type: FileType) -> Optional[str]:
        """
        Extract text content from a file.

        This is a simplified implementation. In production, use libraries like:
        - PyPDF2 or pdfplumber for PDFs
        - python-docx for DOCX
        - PIL for images (OCR)
        - etc.
        """
        try:
            if file_type in [FileType.TEXT, FileType.MARKDOWN, FileType.JSON, FileType.CSV]:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif file_type == FileType.PDF:
                # Placeholder - would use pdfplumber or PyPDF2
                return "[PDF content extraction not implemented]"
            elif file_type == FileType.DOCX:
                # Placeholder - would use python-docx
                return "[DOCX content extraction not implemented]"
            else:
                return None
        except Exception:
            return None

    def _load_files(self):
        """Load file metadata from storage."""
        # In a real implementation, this would load from a database
        # For now, scan the storage directory
        if self.storage_dir.exists():
            for subdir in self.storage_dir.iterdir():
                if subdir.is_dir():
                    for file_path in subdir.glob("*"):
                        if file_path.is_file():
                            # Try to extract file ID from filename
                            filename = file_path.name
                            if '_' in filename:
                                file_id_str = filename.split('_')[0]
                                try:
                                    file_id = UUID(file_id_str)
                                    # In production, load metadata from database
                                    # For now, create basic metadata
                                    metadata = FileMetadata(
                                        filename=filename,
                                        file_type=self._detect_file_type(filename, mimetypes.guess_type(filename)[0] or ''),
                                        mime_type=mimetypes.guess_type(filename)[0] or 'application/octet-stream',
                                        size_bytes=file_path.stat().st_size,
                                        checksum=self._calculate_checksum(file_path)
                                    )
                                    file_obj = File(
                                        id=file_id,
                                        filename=filename,
                                        file_path=str(file_path),
                                        metadata=metadata,
                                        status=FileStatus.PROCESSED
                                    )
                                    self._files[file_id] = file_obj
                                except ValueError:
                                    continue

    def _save_file_metadata(self, file: File):
        """Save file metadata (in production, save to database)."""
        # In production, save to database
        # For now, just keep in memory
        pass

    def upload_file(
        self,
        file_data: BinaryIO,
        filename: str,
        upload_request: FileUploadRequest
    ) -> Union[FileUploadResponse, FileError]:
        """
        Upload a file to the system.

        Args:
            file_data: File data stream
            filename: Original filename
            upload_request: Upload configuration

        Returns:
            Upload response or error
        """
        try:
            # Validate file extension
            file_ext = Path(filename).suffix.lower()
            if file_ext not in self.allowed_extensions:
                return FileError(
                    type="invalid_file_type",
                    message=f"File type {file_ext} not allowed",
                    details={"allowed_extensions": self.allowed_extensions}
                )

            # Read file data
            content = file_data.read()
            if len(content) > self.max_file_size:
                return FileError(
                    type="file_too_large",
                    message=f"File size {len(content)} exceeds maximum {self.max_file_size}",
                    details={"max_size": self.max_file_size, "actual_size": len(content)}
                )

            # Create file record
            file_id = uuid4()
            file_path = self._get_file_path(file_id, filename)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Save file to disk
            with open(file_path, 'wb') as f:
                f.write(content)

            # Calculate checksum
            checksum = self._calculate_checksum(file_path)

            # Detect file type
            mime_type, _ = mimetypes.guess_type(filename)
            file_type = self._detect_file_type(filename, mime_type or '')

            # Create metadata
            metadata = FileMetadata(
                filename=filename,
                file_type=file_type,
                mime_type=mime_type or 'application/octet-stream',
                size_bytes=len(content),
                checksum=checksum
            )

            # Create file object
            file_obj = File(
                id=file_id,
                project_id=upload_request.project_id,
                session_id=upload_request.session_id,
                filename=filename,
                file_path=str(file_path),
                status=FileStatus.UPLOADED,
                metadata=metadata,
                tags=upload_request.tags,
                is_public=upload_request.is_public
            )

            # Store file
            self._files[file_id] = file_obj
            self._save_file_metadata(file_obj)

            # Process file if requested
            if upload_request.auto_process:
                self._process_file_async(file_id)

            return FileUploadResponse(
                file=file_obj,
                processing_status="processing" if upload_request.auto_process else "uploaded"
            )

        except Exception as e:
            return FileError(
                type="upload_failed",
                message=f"File upload failed: {str(e)}"
            )

    def _process_file_async(self, file_id: UUID):
        """Process a file asynchronously."""
        # In production, use a task queue like Celery
        # For now, process synchronously
        self.process_file(file_id)

    def process_file(self, file_id: UUID) -> FileProcessingResult:
        """
        Process a file to extract content and metadata.

        Args:
            file_id: File ID to process

        Returns:
            Processing result
        """
        start_time = datetime.now()
        file_obj = self._files.get(file_id)

        if not file_obj:
            return FileProcessingResult(
                file_id=file_id,
                success=False,
                error_message="File not found"
            )

        try:
            file_path = Path(file_obj.file_path)
            if not file_path.exists():
                return FileProcessingResult(
                    file_id=file_id,
                    success=False,
                    error_message="File not found on disk"
                )

            # Extract text content
            extracted_text = self._extract_text_content(file_path, file_obj.metadata.file_type)

            # Update metadata
            metadata_updates = {}

            if extracted_text:
                self._file_contents[file_id] = extracted_text
                metadata_updates["extracted_text"] = extracted_text[:1000]  # Store preview
                metadata_updates["word_count"] = len(extracted_text.split())
                metadata_updates["character_count"] = len(extracted_text)

            # Update file status
            file_obj.status = FileStatus.PROCESSED
            file_obj.processed_at = datetime.now()
            file_obj.metadata = file_obj.metadata.model_copy(update=metadata_updates)

            self._save_file_metadata(file_obj)

            processing_time = (datetime.now() - start_time).total_seconds()

            return FileProcessingResult(
                file_id=file_id,
                success=True,
                extracted_text=extracted_text,
                metadata_updates=metadata_updates,
                processing_time=processing_time
            )

        except Exception as e:
            file_obj.status = FileStatus.FAILED
            self._save_file_metadata(file_obj)

            processing_time = (datetime.now() - start_time).total_seconds()

            return FileProcessingResult(
                file_id=file_id,
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )

    def get_file(self, file_id: UUID) -> Optional[File]:
        """
        Get file metadata by ID.

        Args:
            file_id: File ID

        Returns:
            File object if found
        """
        return self._files.get(file_id)

    def get_file_content(self, file_id: UUID) -> Optional[FileContent]:
        """
        Get file content.

        Args:
            file_id: File ID

        Returns:
            File content if available
        """
        file_obj = self._files.get(file_id)
        if not file_obj:
            return None

        content = self._file_contents.get(file_id)
        return FileContent(
            file=file_obj,
            content=content,
            content_type=file_obj.metadata.mime_type,
            encoding="utf-8" if file_obj.metadata.file_type in [FileType.TEXT, FileType.MARKDOWN, FileType.JSON, FileType.CSV] else None
        )

    def update_file(self, file_id: UUID, update_request: FileUpdateRequest) -> Optional[File]:
        """
        Update file metadata.

        Args:
            file_id: File ID
            update_request: Update data

        Returns:
            Updated file if found
        """
        file_obj = self._files.get(file_id)
        if not file_obj:
            return None

        # Update fields
        update_data = update_request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field in ['filename', 'tags', 'is_public', 'project_id', 'session_id']:
                setattr(file_obj, field, value)

        file_obj.updated_at = datetime.now()
        self._save_file_metadata(file_obj)

        return file_obj

    def delete_file(self, file_id: UUID) -> bool:
        """
        Delete a file.

        Args:
            file_id: File ID to delete

        Returns:
            True if deleted
        """
        file_obj = self._files.get(file_id)
        if not file_obj:
            return False

        # Remove from storage
        file_path = Path(file_obj.file_path)
        if file_path.exists():
            file_path.unlink()

        # Remove from memory
        del self._files[file_id]
        self._file_contents.pop(file_id, None)

        # Mark as deleted (in production, update database)
        file_obj.status = FileStatus.DELETED

        return True

    def search_files(self, search_request: FileSearchRequest) -> List[FileSummary]:
        """
        Search files based on criteria.

        Args:
            search_request: Search criteria

        Returns:
            List of file summaries
        """
        results = []

        for file_obj in self._files.values():
            # Apply filters
            if search_request.project_id and file_obj.project_id != search_request.project_id:
                continue
            if search_request.session_id and file_obj.session_id != search_request.session_id:
                continue
            if search_request.file_type and file_obj.metadata.file_type != search_request.file_type:
                continue
            if search_request.status and file_obj.status != search_request.status:
                continue
            if search_request.tags and not any(tag in file_obj.tags for tag in search_request.tags):
                continue
            if search_request.date_from and file_obj.created_at < search_request.date_from:
                continue
            if search_request.date_to and file_obj.created_at > search_request.date_to:
                continue

            # Text search in filename and content
            if search_request.query:
                query_lower = search_request.query.lower()
                filename_match = query_lower in file_obj.filename.lower()
                content_match = False
                if file_obj.id in self._file_contents:
                    content_match = query_lower in self._file_contents[file_obj.id].lower()

                if not (filename_match or content_match):
                    continue

            # Create summary
            summary = FileSummary(
                id=file_obj.id,
                filename=file_obj.filename,
                file_type=file_obj.metadata.file_type,
                size_bytes=file_obj.metadata.size_bytes,
                status=file_obj.status,
                project_id=file_obj.project_id,
                session_id=file_obj.session_id,
                tags=file_obj.tags,
                created_at=file_obj.created_at,
                processed_at=file_obj.processed_at
            )
            results.append(summary)

        # Sort by creation date (newest first) and apply pagination
        results.sort(key=lambda x: x.created_at, reverse=True)
        start_idx = search_request.offset
        end_idx = start_idx + search_request.limit
        return results[start_idx:end_idx]

    def get_conversation_context(
        self,
        context_request: FileContextRequest
    ) -> ConversationContextWithFiles:
        """
        Get conversation context including relevant file content.

        Args:
            context_request: Context request

        Returns:
            Conversation context with files
        """
        # This is a simplified implementation
        # In production, use embeddings and semantic search

        file_contexts = []
        total_tokens = 0

        for file_id in context_request.file_ids:
            file_obj = self._files.get(file_id)
            if not file_obj or file_obj.status != FileStatus.PROCESSED:
                continue

            content = self._file_contents.get(file_id)
            if not content:
                continue

            # Simple relevance scoring (in production, use embeddings)
            # For now, just include all requested files
            relevance_score = 1.0

            # Truncate content if needed
            if context_request.max_tokens:
                # Rough token estimation (1 token ≈ 4 characters)
                max_chars = context_request.max_tokens * 4
                if len(content) > max_chars:
                    content = content[:max_chars] + "..."

            token_count = len(content) // 4  # Rough estimation

            file_context = FileContext(
                file_id=file_id,
                filename=file_obj.filename,
                content=content,
                relevance_score=relevance_score,
                metadata=file_obj.metadata.model_dump() if context_request.include_metadata else None,
                token_count=token_count
            )

            file_contexts.append(file_context)
            total_tokens += token_count

        return ConversationContextWithFiles(
            session_id=context_request.session_id,
            message_context=[],  # Would be populated by conversation service
            file_contexts=file_contexts,
            total_tokens=total_tokens,
            truncated=False
        )

    def get_file_stats(self) -> FileStats:
        """
        Get file management statistics.

        Returns:
            File statistics
        """
        total_files = len(self._files)
        total_size = sum(f.metadata.size_bytes for f in self._files.values())

        files_by_type = {}
        files_by_status = {}

        for file_obj in self._files.values():
            file_type = file_obj.metadata.file_type.value
            status = file_obj.status.value

            files_by_type[file_type] = files_by_type.get(file_type, 0) + 1
            files_by_status[status] = files_by_status.get(status, 0) + 1

        # Calculate recent uploads (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        recent_uploads = sum(1 for f in self._files.values() if f.created_at > yesterday)

        processing_queue = files_by_status.get(FileStatus.PROCESSING.value, 0)
        failed_files = files_by_status.get(FileStatus.FAILED.value, 0)

        return FileStats(
            total_files=total_files,
            total_size_bytes=total_size,
            files_by_type=files_by_type,
            files_by_status=files_by_status,
            recent_uploads=recent_uploads,
            processing_queue=processing_queue,
            failed_files=failed_files
        )