"""
File Management API Endpoints

This module provides REST API endpoints for file management,
document handling, and context integration within the AI Chat Assistant.
"""

import os
from typing import List, Optional
from uuid import UUID
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File as FastAPIFile, Depends, Query
from fastapi.responses import FileResponse

from ..models.file_management import (
    File as FileModel,  # Rename to avoid conflict with FastAPI File
    FileUploadRequest,
    FileUploadResponse,
    FileUpdateRequest,
    FileSearchRequest,
    FileSummary,
    FileContent,
    FileContextRequest,
    ConversationContextWithFiles,
    FileStats,
    FileProcessingResult,
    FileError
)
from ..services.file_management_service import FileManagementService

router = APIRouter()


def get_file_service() -> FileManagementService:
    """Dependency to get file management service instance."""
    return FileManagementService()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    project_id: Optional[UUID] = None,
    session_id: Optional[UUID] = None,
    tags: Optional[str] = None,  # Comma-separated
    is_public: bool = False,
    auto_process: bool = True,
    service: FileManagementService = Depends(get_file_service)
):
    """
    Upload a file to the system.

    Args:
        file: File to upload
        project_id: Optional project association
        session_id: Optional session association
        tags: Comma-separated tags
        is_public: Whether file is public
        auto_process: Whether to process file automatically
        service: File service instance

    Returns:
        Upload response
    """
    try:
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(',')] if tags else []

        # Create upload request
        upload_request = FileUploadRequest(
            project_id=project_id,
            session_id=session_id,
            tags=tag_list,
            is_public=is_public,
            auto_process=auto_process
        )

        # Upload file
        result = service.upload_file(
            file_data=file.file,
            filename=file.filename,
            upload_request=upload_request
        )

        if isinstance(result, FileError):
            status_code = 400
            if result.type == "file_too_large":
                status_code = 413
            elif result.type == "invalid_file_type":
                status_code = 415

            raise HTTPException(
                status_code=status_code,
                detail=result.message
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/{file_id}", response_model=FileModel)
async def get_file(
    file_id: UUID,
    service: FileManagementService = Depends(get_file_service)
):
    """
    Get file metadata.

    Args:
        file_id: File ID
        service: File service instance

    Returns:
        File metadata
    """
    file_obj = service.get_file(file_id)
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")

    return file_obj


@router.get("/{file_id}/download")
async def download_file(
    file_id: UUID,
    service: FileManagementService = Depends(get_file_service)
):
    """
    Download a file.

    Args:
        file_id: File ID
        service: File service instance

    Returns:
        File response
    """
    file_obj = service.get_file(file_id)
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = Path(file_obj.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=file_path,
        filename=file_obj.filename,
        media_type=file_obj.metadata.mime_type
    )


@router.get("/{file_id}/content", response_model=FileContent)
async def get_file_content(
    file_id: UUID,
    service: FileManagementService = Depends(get_file_service)
):
    """
    Get file content (text files only).

    Args:
        file_id: File ID
        service: File service instance

    Returns:
        File content
    """
    content = service.get_file_content(file_id)
    if not content:
        raise HTTPException(status_code=404, detail="File not found or no content available")

    return content


@router.put("/{file_id}", response_model=FileModel)
async def update_file(
    file_id: UUID,
    update_request: FileUpdateRequest,
    service: FileManagementService = Depends(get_file_service)
):
    """
    Update file metadata.

    Args:
        file_id: File ID
        update_request: Update data
        service: File service instance

    Returns:
        Updated file
    """
    updated_file = service.update_file(file_id, update_request)
    if not updated_file:
        raise HTTPException(status_code=404, detail="File not found")

    return updated_file


@router.delete("/{file_id}")
async def delete_file(
    file_id: UUID,
    service: FileManagementService = Depends(get_file_service)
):
    """
    Delete a file.

    Args:
        file_id: File ID
        service: File service instance

    Returns:
        Success status
    """
    deleted = service.delete_file(file_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="File not found")

    return {"status": "deleted", "file_id": str(file_id)}


@router.post("/search", response_model=List[FileSummary])
async def search_files(
    query: Optional[str] = None,
    project_id: Optional[UUID] = None,
    session_id: Optional[UUID] = None,
    file_type: Optional[str] = None,
    tags: Optional[str] = None,  # Comma-separated
    status: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: FileManagementService = Depends(get_file_service)
):
    """
    Search files based on criteria.

    Args:
        query: Search query
        project_id: Filter by project
        session_id: Filter by session
        file_type: Filter by file type
        tags: Comma-separated tags
        status: Filter by status
        limit: Maximum results
        offset: Results offset
        service: File service instance

    Returns:
        List of file summaries
    """
    try:
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(',')] if tags else None

        # Convert string to enum
        file_type_enum = None
        if file_type:
            try:
                from ..models.file_management import FileType
                file_type_enum = FileType(file_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid file type: {file_type}")

        status_enum = None
        if status:
            try:
                from ..models.file_management import FileStatus
                status_enum = FileStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

        search_request = FileSearchRequest(
            query=query,
            project_id=project_id,
            session_id=session_id,
            file_type=file_type_enum,
            tags=tag_list,
            status=status_enum,
            limit=limit,
            offset=offset
        )

        return service.search_files(search_request)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/{file_id}/process", response_model=FileProcessingResult)
async def process_file(
    file_id: UUID,
    service: FileManagementService = Depends(get_file_service)
):
    """
    Process a file to extract content.

    Args:
        file_id: File ID to process
        service: File service instance

    Returns:
        Processing result
    """
    result = service.process_file(file_id)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error_message or "Processing failed")

    return result


@router.post("/context", response_model=ConversationContextWithFiles)
async def get_conversation_context(
    context_request: FileContextRequest,
    service: FileManagementService = Depends(get_file_service)
):
    """
    Get conversation context including relevant file content.

    Args:
        context_request: Context request
        service: File service instance

    Returns:
        Conversation context with files
    """
    try:
        return service.get_conversation_context(context_request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context retrieval failed: {str(e)}")


@router.get("/stats", response_model=FileStats)
async def get_file_stats(
    service: FileManagementService = Depends(get_file_service)
):
    """
    Get file management statistics.

    Returns:
        File statistics
    """
    try:
        return service.get_file_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")


@router.get("/types/supported")
async def get_supported_file_types():
    """
    Get supported file types.

    Returns:
        List of supported file types
    """
    from ..models.file_management import FileType
    return {
        "file_types": [ft.value for ft in FileType],
        "extensions": [
            ".txt", ".pdf", ".docx", ".md", ".json", ".csv",
            ".jpg", ".jpeg", ".png", ".gif", ".webp",
            ".mp3", ".wav", ".mp4", ".avi"
        ]
    }