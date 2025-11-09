"""
Unit Tests for File Management Service

Comprehensive test suite for the file management service functionality.
"""

import pytest
import tempfile
import os
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4
from datetime import datetime

from backend.models.file_management import (
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
    ConversationContextWithFiles,
    FileStats,
    FileProcessingResult,
    FileError
)
from backend.services.file_management_service import FileManagementService


class TestFileManagementService:
    """Test suite for FileManagementService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.service = FileManagementService(
            storage_dir=self.temp_dir / "files",
            temp_dir=self.temp_dir / "temp"
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test service initialization."""
        assert self.service.storage_dir == self.temp_dir / "files"
        assert self.service.temp_dir == self.temp_dir / "temp"
        assert self.service.storage_dir.exists()
        assert self.service.temp_dir.exists()
        assert isinstance(self.service._files, dict)
        assert isinstance(self.service._file_contents, dict)

    def test_get_file_path(self):
        """Test file path generation."""
        file_id = uuid4()
        filename = "test.txt"

        path = self.service._get_file_path(file_id, filename)

        expected_path = self.service.storage_dir / str(file_id)[:2] / f"{file_id}_{filename}"
        assert path == expected_path

    def test_calculate_checksum(self):
        """Test checksum calculation."""
        # Create a test file
        test_file = self.temp_dir / "test.txt"
        test_content = b"Hello, World!"
        test_file.write_bytes(test_content)

        checksum = self.service._calculate_checksum(test_file)

        # SHA256 of "Hello, World!"
        expected = "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"
        assert checksum == expected

    def test_detect_file_type(self):
        """Test file type detection."""
        test_cases = [
            ("document.txt", "text/plain", FileType.TEXT),
            ("document.pdf", "application/pdf", FileType.PDF),
            ("document.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", FileType.DOCX),
            ("data.json", "application/json", FileType.JSON),
            ("data.csv", "text/csv", FileType.CSV),
            ("image.jpg", "image/jpeg", FileType.IMAGE),
            ("unknown.xyz", "application/octet-stream", FileType.OTHER),
        ]

        for filename, mime_type, expected in test_cases:
            result = self.service._detect_file_type(filename, mime_type)
            assert result == expected

    def test_extract_text_content_text_file(self):
        """Test text content extraction for text files."""
        # Create a test text file
        test_file = self.temp_dir / "test.txt"
        test_content = "Hello, World!\nThis is a test."
        test_file.write_text(test_content)

        extracted = self.service._extract_text_content(test_file, FileType.TEXT)

        assert extracted == test_content

    def test_extract_text_content_binary_file(self):
        """Test text content extraction for binary files."""
        # Create a test binary file
        test_file = self.temp_dir / "test.pdf"
        test_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
        test_file.write_bytes(test_content)

        extracted = self.service._extract_text_content(test_file, FileType.PDF)

        # Should return placeholder for unsupported formats
        assert extracted == "[PDF content extraction not implemented]"

    def test_upload_file_success(self):
        """Test successful file upload."""
        # Create test file data
        file_data = BytesIO(b"Hello, World!")
        filename = "test.txt"

        upload_request = FileUploadRequest(
            project_id=uuid4(),
            session_id=uuid4(),
            tags=["test", "document"],
            is_public=False,
            auto_process=True
        )

        result = self.service.upload_file(file_data, filename, upload_request)

        assert isinstance(result, FileUploadResponse)
        assert result.file.filename == filename
        assert result.file.metadata.file_type == FileType.TEXT
        assert result.file.metadata.size_bytes == 13  # "Hello, World!" is 13 characters
        assert result.file.project_id == upload_request.project_id
        assert result.file.session_id == upload_request.session_id
        assert result.file.tags == upload_request.tags
        assert result.file.status == FileStatus.PROCESSED  # Auto-processed
        assert result.processing_status == "processing"

        # Check file was saved
        assert Path(result.file.file_path).exists()

        # Check file is in memory storage
        assert result.file.id in self.service._files

    def test_upload_file_too_large(self):
        """Test upload rejection for files that are too large."""
        # Create service with small limit
        small_service = FileManagementService(
            storage_dir=self.temp_dir / "files2",
            max_file_size=10  # 10 bytes
        )

        # Create file larger than limit
        file_data = BytesIO(b"This is a very long file that exceeds the size limit")
        filename = "large.txt"

        upload_request = FileUploadRequest()

        result = small_service.upload_file(file_data, filename, upload_request)

        assert isinstance(result, FileError)
        assert result.type == "file_too_large"
        assert "exceeds maximum" in result.message

    def test_upload_file_invalid_type(self):
        """Test upload rejection for invalid file types."""
        # Create service with restricted extensions
        restricted_service = FileManagementService(
            storage_dir=self.temp_dir / "files3",
            allowed_extensions=[".txt", ".pdf"]
        )

        file_data = BytesIO(b"test content")
        filename = "test.exe"  # Not allowed

        upload_request = FileUploadRequest()

        result = restricted_service.upload_file(file_data, filename, upload_request)

        assert isinstance(result, FileError)
        assert result.type == "invalid_file_type"
        assert "not allowed" in result.message

    def test_get_file(self):
        """Test getting file metadata."""
        # First upload a file
        file_data = BytesIO(b"test content")
        filename = "test.txt"
        upload_request = FileUploadRequest()

        upload_result = self.service.upload_file(file_data, filename, upload_request)
        file_id = upload_result.file.id

        # Now get it back
        retrieved = self.service.get_file(file_id)

        assert retrieved is not None
        assert retrieved.id == file_id
        assert retrieved.filename == filename

    def test_get_file_not_found(self):
        """Test getting non-existent file."""
        file_id = uuid4()

        result = self.service.get_file(file_id)

        assert result is None

    def test_get_file_content(self):
        """Test getting file content."""
        # Upload and process a text file
        file_data = BytesIO(b"Hello, World!")
        filename = "test.txt"
        upload_request = FileUploadRequest(auto_process=True)

        upload_result = self.service.upload_file(file_data, filename, upload_request)
        file_id = upload_result.file.id

        # Process the file
        self.service.process_file(file_id)

        # Get content
        content = self.service.get_file_content(file_id)

        assert content is not None
        assert content.file.id == file_id
        assert content.content == "Hello, World!"
        assert content.content_type == "text/plain"
        assert content.encoding == "utf-8"

    def test_get_file_content_not_found(self):
        """Test getting content for non-existent file."""
        file_id = uuid4()

        content = self.service.get_file_content(file_id)

        assert content is None

    def test_update_file(self):
        """Test updating file metadata."""
        # Upload a file
        file_data = BytesIO(b"test content")
        filename = "test.txt"
        upload_request = FileUploadRequest()

        upload_result = self.service.upload_file(file_data, filename, upload_request)
        file_id = upload_result.file.id

        # Update it
        update_request = FileUpdateRequest(
            filename="updated.txt",
            tags=["updated"],
            is_public=True
        )

        updated = self.service.update_file(file_id, update_request)

        assert updated is not None
        assert updated.filename == "updated.txt"
        assert updated.tags == ["updated"]
        assert updated.is_public is True
        assert updated.updated_at > updated.created_at

    def test_update_file_not_found(self):
        """Test updating non-existent file."""
        file_id = uuid4()
        update_request = FileUpdateRequest(filename="test.txt")

        result = self.service.update_file(file_id, update_request)

        assert result is None

    def test_delete_file(self):
        """Test deleting a file."""
        # Upload a file
        file_data = BytesIO(b"test content")
        filename = "test.txt"
        upload_request = FileUploadRequest()

        upload_result = self.service.upload_file(file_data, filename, upload_request)
        file_id = upload_result.file.id
        file_path = Path(upload_result.file.file_path)

        # Verify file exists
        assert file_path.exists()
        assert file_id in self.service._files

        # Delete it
        deleted = self.service.delete_file(file_id)

        assert deleted is True
        assert not file_path.exists()
        assert file_id not in self.service._files

    def test_delete_file_not_found(self):
        """Test deleting non-existent file."""
        file_id = uuid4()

        deleted = self.service.delete_file(file_id)

        assert deleted is False

    def test_process_file_text(self):
        """Test processing a text file."""
        # Upload a text file
        file_data = BytesIO(b"Hello, World!\nThis is a test file.")
        filename = "test.txt"
        upload_request = FileUploadRequest(auto_process=False)

        upload_result = self.service.upload_file(file_data, filename, upload_request)
        file_id = upload_result.file.id

        # Process it
        result = self.service.process_file(file_id)

        assert result.success is True
        assert result.extracted_text == "Hello, World!\nThis is a test file."
        assert result.metadata_updates["word_count"] == 7  # Hello, World! This is a test file.
        assert result.metadata_updates["character_count"] == 34

        # Check file was updated
        file_obj = self.service.get_file(file_id)
        assert file_obj.status == FileStatus.PROCESSED
        assert file_obj.processed_at is not None

    def test_process_file_binary(self):
        """Test processing a binary file."""
        # Upload a PDF file (simulated)
        file_data = BytesIO(b"%PDF-1.4 fake content")
        filename = "test.pdf"
        upload_request = FileUploadRequest(auto_process=False)

        upload_result = self.service.upload_file(file_data, filename, upload_request)
        file_id = upload_result.file.id

        # Process it
        result = self.service.process_file(file_id)

        assert result.success is True
        assert result.extracted_text == "[PDF content extraction not implemented]"

    def test_search_files_by_filename(self):
        """Test searching files by filename."""
        # Upload multiple files
        files_data = [
            ("document1.txt", b"content 1"),
            ("document2.txt", b"content 2"),
            ("image.jpg", b"fake image data")
        ]

        file_ids = []
        for filename, content in files_data:
            upload_result = self.service.upload_file(
                BytesIO(content), filename, FileUploadRequest()
            )
            file_ids.append(upload_result.file.id)

        # Search for "document"
        search_request = FileSearchRequest(query="document")

        results = self.service.search_files(search_request)

        assert len(results) == 2
        assert all("document" in r.filename for r in results)

    def test_search_files_by_type(self):
        """Test searching files by type."""
        # Upload files of different types
        self.service.upload_file(BytesIO(b"text"), "test.txt", FileUploadRequest())
        self.service.upload_file(BytesIO(b"fake pdf"), "test.pdf", FileUploadRequest())

        # Search for text files
        search_request = FileSearchRequest(file_type=FileType.TEXT)

        results = self.service.search_files(search_request)

        assert len(results) == 1
        assert results[0].file_type == FileType.TEXT

    def test_search_files_with_pagination(self):
        """Test search results pagination."""
        # Upload multiple files
        for i in range(5):
            self.service.upload_file(
                BytesIO(f"content {i}".encode()),
                f"file{i}.txt",
                FileUploadRequest()
            )

        # Get first 2 results
        search_request = FileSearchRequest(limit=2, offset=0)
        results1 = self.service.search_files(search_request)

        # Get next 2 results
        search_request = FileSearchRequest(limit=2, offset=2)
        results2 = self.service.search_files(search_request)

        assert len(results1) == 2
        assert len(results2) == 2
        assert results1[0].filename != results2[0].filename

    def test_get_conversation_context(self):
        """Test getting conversation context with files."""
        # Upload and process files
        file1_result = self.service.upload_file(
            BytesIO(b"File 1 content"), "file1.txt", FileUploadRequest()
        )
        file2_result = self.service.upload_file(
            BytesIO(b"File 2 content"), "file2.txt", FileUploadRequest()
        )

        # Process files
        self.service.process_file(file1_result.file.id)
        self.service.process_file(file2_result.file.id)

        # Get context
        context_request = FileContextRequest(
            session_id=uuid4(),
            file_ids=[file1_result.file.id, file2_result.file.id]
        )

        context = self.service.get_conversation_context(context_request)

        assert isinstance(context, ConversationContextWithFiles)
        assert len(context.file_contexts) == 2
        assert context.total_tokens > 0
        assert not context.truncated

    def test_get_file_stats(self):
        """Test getting file statistics."""
        # Upload files of different types
        self.service.upload_file(BytesIO(b"text1"), "file1.txt", FileUploadRequest())
        self.service.upload_file(BytesIO(b"text2"), "file2.txt", FileUploadRequest())
        self.service.upload_file(BytesIO(b"pdf"), "file.pdf", FileUploadRequest())

        stats = self.service.get_file_stats()

        assert isinstance(stats, FileStats)
        assert stats.total_files == 3
        assert stats.files_by_type["text"] == 2
        assert stats.files_by_type["pdf"] == 1
        assert stats.total_size_bytes > 0

    def test_file_workflow(self):
        """Test complete file workflow."""
        # 1. Upload
        file_data = BytesIO(b"This is a test document for AI processing.")
        upload_result = self.service.upload_file(
            file_data, "test.txt", FileUploadRequest(auto_process=True)
        )

        assert upload_result.file.status == FileStatus.PROCESSED  # Auto-processed

        # 2. Process
        process_result = self.service.process_file(upload_result.file.id)
        assert process_result.success

        # 3. Get content
        content = self.service.get_file_content(upload_result.file.id)
        assert content.content == "This is a test document for AI processing."

        # 4. Update metadata
        update_result = self.service.update_file(
            upload_result.file.id,
            FileUpdateRequest(tags=["test", "ai", "processed"])
        )
        assert update_result.tags == ["test", "ai", "processed"]

        # 5. Search
        search_results = self.service.search_files(
            FileSearchRequest(query="test", tags=["ai"])
        )
        assert len(search_results) == 1

        # 6. Delete
        delete_result = self.service.delete_file(upload_result.file.id)
        assert delete_result

        # Verify deleted
        assert self.service.get_file(upload_result.file.id) is None