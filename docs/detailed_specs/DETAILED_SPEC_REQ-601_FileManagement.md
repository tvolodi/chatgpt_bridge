# REQ-601: File Management and Upload

**Registry Entry:** See `docs/01_requirements_registry.md` (Line 128)  
**Functionality Reference:** `specifications/functionality.md` Section 6  
**Document Version:** 1.0  
**Last Updated:** November 15, 2025  
**Status:** implemented  

---

## 1. Overview

### 1.1 Brief Description
Enable users to upload and manage files within projects and sessions, with automatic type detection, metadata tracking, size limits, and integration into AI context for analysis.

### 1.2 Business Value
- **Context Enhancement:** AI can analyze uploaded documents
- **Knowledge Base:** Store reference materials with projects
- **Analysis:** Support for code, PDFs, docs, spreadsheets
- **Organization:** Files scoped to project or session level

---

## 2. Functional Requirements

### 2.1 Core Requirements

#### REQ-601-A: File Upload with Metadata
- **Description:** Upload files with automatic type detection
- **Supported Types:** Text, Code, Images, PDFs, Office docs, Markdown
- **Metadata Tracked:**
  - filename, file_type, mime_type, size_bytes
  - checksum (MD5), upload_date, uploader
  - For text: language, word_count, character_count
  - For code: language detected, line_count
  - For PDFs: page_count
- **Storage:** Files in `data/projects/{id}/files/` or `data/chat_sessions/{id}/files/`
- **Metadata:** Stored in parent's metadata.json
- **Acceptance Criteria:**
  - ✓ File uploaded successfully
  - ✓ Type detected correctly
  - ✓ Metadata complete
  - ✓ File accessible immediately

#### REQ-601-B: File Size Limits
- **Description:** Enforce storage quotas
- **Per-File Limit:** 50MB maximum
- **Per-Project Limit:** 500MB total
- **Per-Session Limit:** 100MB total
- **Enforcement:**
  - Check before upload
  - Reject if exceeds limit
  - Show remaining quota to user
- **Error Handling:** Clear message: "Project storage full. Delete unused files to upload more."
- **Acceptance Criteria:**
  - ✓ Limits enforced
  - ✓ User warned before reaching limit
  - ✓ Graceful rejection if exceeded

#### REQ-601-C: File Listing and Organization
- **Description:** List files in project/session with filtering
- **Features:**
  - Sort by: name, date, size, type
  - Filter by: type (code, documents, images)
  - Search by: filename
  - Group by: type
- **API:** GET `/api/files/projects/{id}?filter={type}&sort={field}`
- **Response:** `[{ id, name, type, size, uploadDate, previewUrl }]`
- **Acceptance Criteria:**
  - ✓ Files listed with metadata
  - ✓ Can filter and sort
  - ✓ Preview URLs available
  - ✓ Performance good even with many files

#### REQ-601-D: File Download
- **Description:** Download files with correct MIME type
- **API:** GET `/api/files/{file_id}/download`
- **Response:** Raw file content with Content-Disposition header
- **MIME Types:** Detected and set correctly
- **Acceptance Criteria:**
  - ✓ File downloads with correct name
  - ✓ MIME type correct
  - ✓ Browser handles correctly (opens or saves)
  - ✓ Large files stream efficiently

#### REQ-601-E: File Deletion
- **Description:** Delete files with user confirmation
- **Implementation:**
  - File removed from storage
  - Metadata removed from parent
  - Project/session storage quota updated
  - Cannot be undone
- **Confirmation:** "Are you sure? This file will be permanently deleted."
- **API:** DELETE `/api/files/{file_id}`
- **Acceptance Criteria:**
  - ✓ File removed from disk
  - ✓ Metadata cleaned up
  - ✓ Storage quota updated
  - ✓ User warned first

#### REQ-601-F: Multiple File Type Support
- **Description:** Handle diverse file formats
- **Text Files:**
  - .txt, .md, .csv, .json, .xml
  - Extract full content
  - Line count and character count
- **Code Files:**
  - .py, .js, .ts, .java, .cpp, .go
  - Language detection
  - Syntax highlighting in UI
  - Line count tracked
- **Images:**
  - .jpg, .png, .gif, .svg
  - Generate thumbnail (100x100px)
  - Store dimensions
- **Documents:**
  - .pdf, .doc, .docx, .xlsx
  - Extract text for analysis
  - Page/sheet count
- **Archives:**
  - .zip support (future)
- **Validation:** MIME type checked, file signature verified
- **Acceptance Criteria:**
  - ✓ Common types supported
  - ✓ Content extracted where applicable
  - ✓ Metadata detected
  - ✓ Invalid files rejected

#### REQ-601-G: File Integration with AI Context
- **Description:** Include files in AI conversations
- **Process:**
  1. When sending message, retrieve project + session files
  2. Extract text content (up to 5MB total)
  3. Include in system context or user message
  4. AI can analyze and discuss files
- **Limitations:**
  - Max 5MB of file content per request
  - Binary files have content extracted to text
  - Large files summarized
- **User Reference:** User can mention "in my Python file" and AI understands
- **Acceptance Criteria:**
  - ✓ Files retrieved for context
  - ✓ Content included in AI calls
  - ✓ AI can analyze and discuss
  - ✓ Size limits respected
  - ✓ Performance acceptable

#### REQ-601-H: File Metadata and Checksums
- **Description:** Track file integrity and metadata
- **Checksum:** MD5 hash calculated and stored
- **Verification:** Can verify file integrity
- **Metadata Structure:**
  ```python
  {
    "id": "file-uuid",
    "filename": "analysis.py",
    "file_type": "code",
    "mime_type": "text/x-python",
    "size_bytes": 2456,
    "checksum": "5d41402abc4b2a76b9719d911017c592",
    "upload_date": "2025-11-15T10:30:45Z",
    "uploader": "system",
    "language": "python",
    "line_count": 87,
    "character_count": 2456,
    "encoding": "utf-8"
  }
  ```
- **Storage:** In parent's metadata.json in files array
- **Acceptance Criteria:**
  - ✓ Metadata complete and accurate
  - ✓ Checksum calculated
  - ✓ Stored in metadata
  - ✓ Can verify integrity

### 2.2 Technical Constraints

- **Max File Size:** 50MB per file
- **Max Project Storage:** 500MB
- **Max Session Storage:** 100MB
- **Supported Types:** 15+ file types
- **Extraction:** Text extraction for first 10MB of files
- **Timeout:** 60s max for file operations

---

## 3. Implementation Details

### 3.1 Backend Services

**FileManagementService** (backend/services/file_management_service.py)

**Key Methods:**
- `upload_file(file_data, filename, project_id|session_id)` - Upload and store
- `download_file(file_id)` - Retrieve file content
- `delete_file(file_id)` - Remove file
- `list_files(project_id|session_id)` - List with metadata
- `_extract_text(file)` - Extract text from file
- `_detect_file_type(filename, mime_type)` - Detect type
- `_calculate_checksum(file_path)` - MD5 hash
- `_get_file_context(files)` - Prepare for AI inclusion

**Storage Structure:**
- `data/projects/{id}/files/{file_id}_{filename}`
- `data/chat_sessions/{id}/files/{file_id}_{filename}`
- Naming prevents collisions

### 3.2 Frontend Components

**FileUpload.tsx** - Upload interface with:
- Drag-and-drop zone
- File input button
- Progress bar
- Error display

**FileList.tsx** - Display files with:
- Table/list view
- Sort and filter controls
- Download buttons
- Delete with confirmation
- Size display
- Type icons

### 3.3 API Endpoints

- **POST** `/api/files/upload` - Upload file
- **GET** `/api/files/{id}/download` - Download
- **DELETE** `/api/files/{id}` - Delete
- **GET** `/api/files/projects/{id}` - List project files
- **GET** `/api/files/sessions/{id}` - List session files

---

## 4. Testing Strategy

**Test File:** `tests/unit/test_file_management.py`

- `test_file_upload`: Upload file successfully
- `test_file_size_limit`: Reject oversized files
- `test_file_type_detection`: Detect types correctly
- `test_file_extraction`: Extract text from documents
- `test_checksum_calculation`: Calculate correct MD5
- `test_file_deletion`: Delete and clean up
- `test_storage_quota`: Track and enforce quotas

---

## 5. Dependencies & Relationships

### 5.1 Depends On

| REQ-ID | Title | Reason |
|--------|-------|--------|
| REQ-101 | File persistence | Files stored persistently |
| REQ-209 | Project CRUD | Files organized in projects |
| REQ-213 | Session CRUD | Files organized in sessions |

### 5.2 Enables / Unblocks

| REQ-ID | Title | How |
|--------|-------|-----|
| REQ-411 | Project files in context | Files available for AI |
| REQ-412 | Session files in context | Files available for AI |

---

## 6. Acceptance Checklist

- [x] Upload functionality works
- [x] Size limits enforced
- [x] File types detected
- [x] Metadata tracked
- [x] Download works
- [x] Deletion works
- [x] AI can use files
- [x] Tests passing

---

## Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-15 | Development Team | Initial specification |

---

**Status:** Ready for team use
