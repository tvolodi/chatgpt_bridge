# REQ-401: Message History and Retrieval

**Registry Entry:** See `docs/01_requirements_registry.md` (Line 104-110)  
**Functionality Reference:** `specifications/functionality.md` Section 4.1-4.2  
**Document Version:** 1.0  
**Last Updated:** November 15, 2025  
**Status:** implemented  

---

## 1. Overview

### 1.1 Brief Description
Implement complete message history management - storing user and AI messages with full metadata (timestamps, provider info, tokens used, status), enabling complete conversation history retrieval, and supporting message retry and deletion operations.

### 1.2 Business Value
- **Context Preservation:** Complete conversation history available for future reference
- **Transparency:** Users see exactly when messages were sent and which provider generated responses
- **Reliability:** Failed messages can be retried without duplication
- **Analysis:** Complete metadata enables usage tracking and debugging

---

## 2. Functional Requirements

### 2.1 Core Requirements

#### REQ-401-A: Save User Messages with Metadata
- **Description:** Persist user messages with full context
- **Storage:** `data/chat_sessions/{session_id}/messages.json`
- **Fields:** id (UUID), session_id (UUID), role ("user"), content, timestamp (ISO8601), status ("sent"|"failed"|"pending"), metadata
- **Triggered:** After user sends message, before AI call
- **Acceptance Criteria:**
  - ✓ Message saved immediately on send
  - ✓ All fields preserved exactly
  - ✓ Timestamp in UTC ISO8601 format
  - ✓ UUID stored as string

#### REQ-401-B: Save AI Responses with Provider Metadata
- **Description:** Persist AI responses with provider-specific data
- **Storage:** Same messages.json array
- **Additional Fields:** provider_id (string), tokens (int), finish_reason (string), model (string)
- **Metadata Example:** `{ "model": "gpt-4", "temperature": 0.7, "max_tokens": 2000 }`
- **Triggered:** After AI provider returns response
- **Acceptance Criteria:**
  - ✓ Provider ID recorded
  - ✓ Token count tracked
  - ✓ Finish reason captured ("stop", "length", "content_filter", etc.)
  - ✓ All metadata persisted

#### REQ-401-C: Load Full Message History on Session Open
- **Description:** Retrieve complete message history when session selected
- **API Endpoint:** GET `/api/chat_sessions/{session_id}/messages`
- **Response:** Array of Message objects, oldest first
- **Pagination:** Optional offset/limit parameters for large histories
- **Performance:** Must load < 500ms for typical sessions
- **Acceptance Criteria:**
  - ✓ All messages returned in order
  - ✓ Complete metadata included
  - ✓ Types properly converted (UUID, datetime)
  - ✓ Performance acceptable

#### REQ-401-D: Message Status Tracking
- **Description:** Track message status throughout lifecycle
- **Statuses:**
  - "pending" - Sent to AI, waiting for response
  - "sent" - Successfully delivered
  - "failed" - Error during send or processing
  - "retrying" - User initiated retry
- **Persistence:** Status stored in message object
- **UI Display:** Status shown with visual indicator
- **Acceptance Criteria:**
  - ✓ Status transitions correctly
  - ✓ Failed messages mark clearly
  - ✓ Can retry failed messages
  - ✓ No duplicate messages on retry

#### REQ-401-E: Message Deletion Support
- **Description:** Delete individual messages with user confirmation
- **Implementation:** Remove from messages.json, update message_count
- **Cascade:** No cascade (only message affected)
- **Confirmation:** User must confirm before delete
- **API:** DELETE `/api/messages/{message_id}`
- **Acceptance Criteria:**
  - ✓ Message removed from history
  - ✓ Cannot be undone
  - ✓ User warned before deletion
  - ✓ Confirmation required

#### REQ-401-F: Message Retry for Failed Messages
- **Description:** Retry sending failed messages without creating duplicates
- **Flow:**
  1. User clicks retry on failed message
  2. System marks as "retrying"
  3. Re-sends message content to AI provider
  4. Updates status and response on success
  5. Marks as "failed" again if retry fails
- **No Duplication:** Original message ID retained, not creating new
- **API:** POST `/api/messages/{message_id}/retry`
- **Acceptance Criteria:**
  - ✓ Original message ID maintained
  - ✓ Can retry multiple times
  - ✓ Failed messages don't disappear
  - ✓ Success updates original message

#### REQ-401-G: Project and Session Files in AI Context
- **Description:** Include project and session files when calling AI
- **Implementation:**
  - Retrieve project files: from `data/projects/{project_id}/files/`
  - Retrieve session files: from `data/chat_sessions/{session_id}/files/`
  - Include file contents in system prompt or context
  - Limit context: Up to 5MB of file content per request
- **File Processing:**
  - Extract text from supported formats
  - Include file type in context ("python code", "markdown", "PDF text")
  - Summarize if file too large
- **Acceptance Criteria:**
  - ✓ Files retrieved from both sources
  - ✓ Contents included in AI requests
  - ✓ AI can reference and analyze files
  - ✓ Context limits respected

#### REQ-401-H: Token Counting and Usage Tracking
- **Description:** Track tokens used for context estimation
- **Implementation:**
  - OpenAI: Use tiktoken library for token counting
  - Anthropic: Use provider's token counter
  - Store: prompt_tokens and completion_tokens per message
  - Display: Show in UI for transparency
- **Storage:** In message metadata: `{ "prompt_tokens": 120, "completion_tokens": 85 }`
- **Aggregation:** Sum for cost estimation
- **Acceptance Criteria:**
  - ✓ Token counts accurate
  - ✓ Tracked per message
  - ✓ Can calculate costs
  - ✓ Metadata persisted

### 2.2 Technical Constraints

- **Message Size:** Max 10,000 characters per message
- **History Size:** Max 10,000 messages per session (recommended)
- **Context Limit:** 5MB of file content per AI request
- **Timeout:** 30s max for AI response
- **Retry Limit:** 3 attempts maximum for failed messages

### 2.3 Data Structures

```python
class Message(BaseModel):
    id: UUID
    session_id: UUID
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime
    status: Literal["pending", "sent", "failed", "retrying"] = "pending"
    provider_id: Optional[str] = None           # For AI messages
    tokens: Optional[Dict[str, int]] = None     # { "prompt": 120, "completion": 85 }
    finish_reason: Optional[str] = None         # "stop", "length", etc.
    metadata: Dict[str, Any] = {}               # Provider-specific data
    error_message: Optional[str] = None         # If status == "failed"
```

---

## 3. Implementation Details

### 3.1 Backend Services

**ConversationService** (backend/services/conversation_service.py)

**Key Methods:**
- `send_message(session_id, content, project_id)` - Main entry point (lines 50-120)
  - Creates user message
  - Calls _save_message()
  - Calls AI provider
  - Creates AI response message
  - Calls _save_message() for response
  - Returns both messages

- `_save_message(message)` - Persist single message (lines 122-135)
  - Loads messages.json
  - Appends message
  - Saves back to disk
  - Updates session metadata (message_count)

- `_load_messages(session_id)` - Load all messages (lines 137-150)
  - Loads messages.json
  - Converts JSON to Message objects
  - Returns sorted by timestamp

- `_get_file_context(project_id, session_id)` - Build AI context (lines 152-180)
  - Lists files in project and session
  - Extracts text from each file
  - Concatenates with size limit (5MB)
  - Includes file names and types

- `_count_tokens(text, provider)` - Count tokens (lines 182-200)
  - Provider-specific token counting
  - Uses tiktoken (OpenAI) or provider API (Anthropic)
  - Returns token count

**ChatSessionService** (backend/services/chat_session_service.py)

- `get_messages(session_id)` - API endpoint wrapper (lines 200-215)
- `delete_message(session_id, message_id)` - Delete operation (lines 217-240)
- `retry_message(session_id, message_id)` - Retry failed message (lines 242-275)

### 3.2 Frontend Components

**ChatArea.tsx** (frontend/src/components/ChatArea.tsx)
- Displays messages in chronological order
- Shows message metadata (timestamp, provider)
- Status indicators (pending spinner, failed indicator)
- Retry button for failed messages

**Message.tsx** (frontend/src/components/Message.tsx)
- Individual message display
- Copy to clipboard button
- Delete button with confirmation
- Token count display (if available)

**MessageInput.tsx** (frontend/src/components/MessageInput.tsx)
- Text input field
- Send button (disabled if loading)
- Character counter

### 3.3 API Endpoints

- **POST** `/api/conversations/send` - Send message
  - Request: `{ session_id, content, project_id }`
  - Response: `{ user_message: Message, ai_response: Message }`

- **GET** `/api/chat_sessions/{session_id}/messages` - Load history
  - Query params: `offset`, `limit` (optional)
  - Response: `{ messages: Message[], total: int }`

- **DELETE** `/api/messages/{message_id}` - Delete message
  - Request: Confirmation required
  - Response: `{ success: bool }`

- **POST** `/api/messages/{message_id}/retry` - Retry failed message
  - Response: `{ message: Message }`

---

## 4. Testing Strategy

### 4.1 Unit Tests

**File:** `tests/unit/test_message_management.py`

- `test_save_user_message`: Create and persist user message
- `test_save_ai_response`: Save AI response with metadata
- `test_load_message_history`: Load all messages in order
- `test_message_status_transitions`: Status changes correctly
- `test_delete_message`: Message removed from history
- `test_retry_failed_message`: Retry without duplication
- `test_token_counting`: Tokens counted and stored
- `test_file_context_building`: Files included in context

### 4.2 Integration Tests

**File:** `tests/integration/test_message_persistence.py`

- `test_send_message_complete_flow`: User sends → AI responds → both saved
- `test_message_load_after_restart`: Send message, restart, message still there
- `test_large_history_performance`: Load session with 1000 messages < 500ms

### 4.3 E2E Tests

**File:** `tests/test_e2e_workflows.py`

- `test_complete_chat_workflow`: Full conversation with message save/load
- `test_retry_failed_message_workflow`: Send fails, user retries, succeeds

---

## 5. Dependencies & Relationships

### 5.1 Depends On

| REQ-ID | Title | Reason |
|--------|-------|--------|
| REQ-101 | File-based persistence | Messages persisted to JSON |
| REQ-206 | Session isolation | Each session has separate messages |
| REQ-213 | Session CRUD | Sessions required to hold messages |
| REQ-501 | Multi-provider support | AI responses from providers |

### 5.2 Enables / Unblocks

| REQ-ID | Title | How |
|--------|-------|-----|
| REQ-404 | Load history on session open | Implemented here |
| REQ-405 | Message status tracking | Implemented here |
| REQ-407 | Retry failed messages | Implemented here |
| REQ-409 | Full message history | Implemented here |
| REQ-411-412 | Files in context | Implemented here |

---

## 6. Known Issues & Notes

- Message pagination UI not yet implemented (API supports it)
- Token counting requires provider-specific libraries
- Large files (>100MB) not included in AI context (summarized instead)

---

## 7. Acceptance Checklist

- [x] Messages persist with metadata
- [x] History loads on session open
- [x] Status tracking works
- [x] Failed messages can retry
- [x] Deletion supported
- [x] Files included in AI context
- [x] Token counting implemented
- [x] Tests passing (TC-UNIT-401-413)

---

## Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-15 | Development Team | Initial specification |

---

**Status:** Ready for team use
