# DOCUMENT_TYPE: TEST_CATALOG
# VERSION: 1.0

## 1. Test Case Template (Generic)

### TC-ID: TC-<TYPE>-<NNN>
- Type: unit | functional | e2e
- Related Requirements:
  - REQ-XXX
- Related Modules:
  - MOD-FE-XXX, MOD-BE-YYY
- Pre-Conditions:
  - 
- Test Steps:
  1. 
  2. 
- Expected Result:
  - 
- Status: proposed | implemented | automated | flaky | disabled
- Automation Location:
  - File:
  - Framework:
- Notes:

## 2. Backend Tests - Foundation & Architecture (REQ-101 to REQ-112)

### TC-ID: TC-UNIT-101
- Type: unit
- Related Requirements:
  - REQ-101
- Related Modules:
  - MOD-BE-Core
- Pre-Conditions:
  - Python environment configured.
  - Pydantic v2 installed.
- Test Steps:
  1. Create a test entity (e.g., Project).
  2. Serialize to JSON.
  3. Deserialize from JSON.
  4. Verify data integrity.
- Expected Result:
  - Object serializes/deserializes without data loss.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_persistence.py\`
  - Framework: pytest
- Notes: Covers file-based persistence with JSON serialization

### TC-ID: TC-UNIT-102
- Type: unit
- Related Requirements:
  - REQ-102
- Related Modules:
  - MOD-BE-Core
- Pre-Conditions:
  - Data directory structure exists.
- Test Steps:
  1. Create data/projects/{project-id}/ hierarchy.
  2. Create data/chat_sessions/{session-id}/ hierarchy.
  3. Verify directory structure is created.
  4. Verify metadata.json files are created.
- Expected Result:
  - Directory hierarchy is created correctly with all required subdirectories.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_directory_hierarchy.py\`
  - Framework: pytest
- Notes: Tests data directory hierarchy with metadata

### TC-ID: TC-UNIT-103
- Type: unit
- Related Requirements:
  - REQ-103
- Related Modules:
  - MOD-BE-Core
- Pre-Conditions:
  - Project metadata file exists.
- Test Steps:
  1. Create a project metadata.
  2. Record \`created_at\` timestamp.
  3. Update project.
  4. Verify \`updated_at\` is newer than \`created_at\`.
  5. Verify version information is incremented.
- Expected Result:
  - Timestamps are properly managed; version control works.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_metadata_versioning.py\`
  - Framework: pytest
- Notes: Tests metadata version control with timestamps

### TC-ID: TC-UNIT-104
- Type: unit
- Related Requirements:
  - REQ-104
- Related Modules:
  - MOD-BE-Core
- Pre-Conditions:
  - Chat session exists.
  - messages.json file exists.
- Test Steps:
  1. Add 5 messages to a session.
  2. Persist to messages.json.
  3. Reload session from file.
  4. Verify all 5 messages are loaded.
- Expected Result:
  - Message history persists correctly to disk and loads on retrieval.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_message_persistence.py\`
  - Framework: pytest
- Notes: Tests message history persistence

### TC-ID: TC-UNIT-105
- Type: unit
- Related Requirements:
  - REQ-105
- Related Modules:
  - MOD-BE-Core
- Pre-Conditions:
  - Environment variables configured.
  - .env file exists.
- Test Steps:
  1. Load API key from environment variable.
  2. Verify API key is loaded correctly.
  3. Verify API key is not exposed in logs.
- Expected Result:
  - API keys are read from environment variables securely.
- Status: implemented
- Automation Location:
  - File: \`tests/test_env_config.py\`
  - Framework: pytest
- Notes: Tests API key environment variable management

### TC-ID: TC-UNIT-106
- Type: unit
- Related Requirements:
  - REQ-106
- Related Modules:
  - MOD-BE-Core, MOD-BE-Settings
- Pre-Conditions:
  - .env file exists in project root.
- Test Steps:
  1. Update .env file with new API key.
  2. Reload settings.
  3. Verify new API key is loaded.
  4. Verify old API key is replaced.
- Expected Result:
  - .env file changes are reflected in settings without restart.
- Status: implemented
- Automation Location:
  - File: \`tests/test_env_config.py\`
  - Framework: pytest
- Notes: Tests .env file persistence and hot-reload

### TC-ID: TC-UNIT-111
- Type: unit
- Related Requirements:
  - REQ-111
- Related Modules:
  - MOD-BE-Core
- Pre-Conditions:
  - Logger configured.
- Test Steps:
  1. Perform an operation that triggers an error (e.g., missing file).
  2. Verify error is caught and logged.
  3. Verify API returns proper HTTP status code (404, 500, etc.).
  4. Verify error response has meaningful message.
- Expected Result:
  - Errors are handled gracefully with proper logging and HTTP responses.
- Status: implemented
- Automation Location:
  - File: \`tests/test_error_handling_logging.py\`
  - Framework: pytest
- Notes: Tests error handling and logging

## 3. Backend Tests - Workspace Organization (REQ-201 to REQ-214)

### TC-ID: TC-UNIT-201
- Type: unit
- Related Requirements:
  - REQ-202
- Related Modules:
  - MOD-BE-Core, MOD-BE-Projects
- Pre-Conditions:
  - Fresh application startup.
  - No projects exist.
- Test Steps:
  1. Start application.
  2. Call \`GET /api/projects\`.
  3. Verify default project is created automatically.
  4. Verify default project has name like "Default" or "My First Project".
- Expected Result:
  - A default project is auto-created on first startup.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_default_project_creation.py\`
  - Framework: pytest
- Notes: Tests default project auto-creation

### TC-ID: TC-UNIT-209
- Type: unit
- Related Requirements:
  - REQ-209
- Related Modules:
  - MOD-BE-Core, MOD-BE-Projects
- Pre-Conditions:
  - ProjectService initialized.
  - Data directory exists.
- Test Steps:
  1. **Create:** POST /api/projects with name and description.
  2. **Read:** GET /api/projects/{project_id}.
  3. **Update:** PUT /api/projects/{project_id} with new name.
  4. **Delete:** DELETE /api/projects/{project_id}.
  5. Verify operations succeeded and data is correct.
- Expected Result:
  - All CRUD operations work correctly; data persists and updates.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_project_crud.py\`
  - Framework: pytest
- Notes: Tests Project CRUD operations

### TC-ID: TC-UNIT-210
- Type: unit
- Related Requirements:
  - REQ-205
- Related Modules:
  - MOD-BE-Core, MOD-BE-Projects
- Pre-Conditions:
  - Two projects exist.
- Test Steps:
  1. Create parent project "Parent".
  2. Create child project "Child" with parent_id.
  3. Call GET /api/projects/tree/all.
  4. Verify tree shows hierarchical structure.
  5. Verify Child is nested under Parent.
- Expected Result:
  - Project hierarchy is created and retrieved correctly.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_project_hierarchy.py\`
  - Framework: pytest
- Notes: Tests nested project structure

### TC-ID: TC-UNIT-213
- Type: unit
- Related Requirements:
  - REQ-213
- Related Modules:
  - MOD-BE-Core, MOD-BE-ChatSessions
- Pre-Conditions:
  - ProjectService and ChatSessionService initialized.
  - A project exists.
- Test Steps:
  1. **Create:** POST /api/chat_sessions with name and project_id.
  2. **Read:** GET /api/chat_sessions/{session_id}.
  3. **Update:** PUT /api/chat_sessions/{session_id} with new name.
  4. **Delete:** DELETE /api/chat_sessions/{session_id}.
  5. Verify operations succeeded and data persists.
- Expected Result:
  - All chat session CRUD operations work correctly.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_session_crud.py\`
  - Framework: pytest
- Notes: Tests ChatSession CRUD operations

### TC-ID: TC-UNIT-214
- Type: unit
- Related Requirements:
  - REQ-214
- Related Modules:
  - MOD-BE-Core, MOD-BE-ChatSessions
- Pre-Conditions:
  - Two chat sessions exist.
  - Both sessions have messages.
- Test Steps:
  1. Add 5 messages to Session A.
  2. Add 3 messages to Session B.
  3. Load messages for Session A.
  4. Verify only Session A's 5 messages are loaded.
  5. Load messages for Session B.
  6. Verify only Session B's 3 messages are loaded.
- Expected Result:
  - Message history is isolated per session.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_message_isolation.py\`
  - Framework: pytest
- Notes: Tests message history isolation per session

## 4. Backend Tests - Chat & Messaging (REQ-401 to REQ-418)

### TC-ID: TC-UNIT-401
- Type: unit
- Related Requirements:
  - REQ-401
- Related Modules:
  - MOD-BE-Core, MOD-BE-Conversations
- Pre-Conditions:
  - ConversationService initialized.
  - A chat session exists.
- Test Steps:
  1. Create a user message object with role='user', content='Hello'.
  2. Call \`save_message(session_id, user_message)\`.
  3. Verify message has id, timestamp, status='sent'.
  4. Reload session and verify message persists.
- Expected Result:
  - User message is created with all required metadata and persists.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_user_message_persistence.py\`
  - Framework: pytest
- Notes: Tests user message metadata persistence

### TC-ID: TC-UNIT-402
- Type: unit
- Related Requirements:
  - REQ-402
- Related Modules:
  - MOD-BE-Core, MOD-BE-Conversations
- Pre-Conditions:
  - ConversationService initialized.
  - A chat session exists with a user message.
- Test Steps:
  1. Create an AI response message with provider_id='openai', tokens={...}.
  2. Call \`save_message(session_id, ai_response)\`.
  3. Verify message has role='assistant', provider_id, tokens, finish_reason.
  4. Reload and verify all AI metadata persists.
- Expected Result:
  - AI response metadata (provider, tokens, finish_reason) persists correctly.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_ai_response_persistence.py\`
  - Framework: pytest
- Notes: Tests AI response metadata persistence

### TC-ID: TC-UNIT-403
- Type: unit
- Related Requirements:
  - REQ-403
- Related Modules:
  - MOD-BE-Core, MOD-BE-Conversations
- Pre-Conditions:
  - ChatSessionService initialized.
  - Multiple messages exist in a session.
- Test Steps:
  1. Add 10 messages to a session.
  2. Call \`_save_messages(session_id, messages)\`.
  3. Verify messages.json is written to disk.
  4. Manually read messages.json and verify all 10 messages are present.
- Expected Result:
  - All messages persist correctly to messages.json file.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_message_file_persistence.py\`
  - Framework: pytest
- Notes: Tests message persistence to disk

### TC-ID: TC-UNIT-405
- Type: unit
- Related Requirements:
  - REQ-405
- Related Modules:
  - MOD-BE-Core, MOD-BE-Conversations
- Pre-Conditions:
  - ConversationService initialized.
- Test Steps:
  1. Create a message with status='pending'.
  2. Simulate sending to API (mock).
  3. Update message status to 'sent'.
  4. Simulate API failure.
  5. Update message status to 'failed'.
  6. Verify all status transitions are saved.
- Expected Result:
  - Message status can be tracked (pending → sent or failed).
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_message_status_tracking.py\`
  - Framework: pytest
- Notes: Tests message status tracking

### TC-ID: TC-UNIT-409
- Type: unit
- Related Requirements:
  - REQ-409
- Related Modules:
  - MOD-BE-Core, MOD-BE-Conversations
- Pre-Conditions:
  - A session has 50 messages.
- Test Steps:
  1. Call \`get_messages(session_id)\`.
  2. Verify all 50 messages are returned.
  3. Verify messages are in chronological order.
  4. Verify each message has complete metadata.
- Expected Result:
  - Full message history can be loaded and is ordered chronologically.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_full_message_history.py\`
  - Framework: pytest
- Notes: Tests full message history loading

### TC-ID: TC-UNIT-411
- Type: unit
- Related Requirements:
  - REQ-411
- Related Modules:
  - MOD-BE-Core, MOD-BE-Conversations, MOD-BE-Files
- Pre-Conditions:
  - A project has files uploaded.
  - A session exists under that project.
- Test Steps:
  1. Call \`build_context(session_id, include_files=True)\`.
  2. Verify context includes project files.
  3. Verify file content is readable.
  4. Verify file content is properly formatted for AI.
- Expected Result:
  - Project files are included in AI context.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_project_files_in_context.py\`
  - Framework: pytest
- Notes: Tests project files in AI context

### TC-ID: TC-UNIT-412
- Type: unit
- Related Requirements:
  - REQ-412
- Related Modules:
  - MOD-BE-Core, MOD-BE-Conversations, MOD-BE-Files
- Pre-Conditions:
  - A session has files uploaded.
- Test Steps:
  1. Call \`build_context(session_id, include_files=True)\`.
  2. Verify context includes session-specific files.
  3. Verify only session files are included, not project files.
- Expected Result:
  - Session files are included in AI context; file isolation maintained.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_session_files_in_context.py\`
  - Framework: pytest
- Notes: Tests session files in AI context

### TC-ID: TC-UNIT-413
- Type: unit
- Related Requirements:
  - REQ-413
- Related Modules:
  - MOD-BE-Core, MOD-BE-Conversations
- Pre-Conditions:
  - Message history exists with multiple messages.
- Test Steps:
  1. Call token counting logic for message history.
  2. Verify total tokens = prompt tokens + completion tokens.
  3. Verify token count is within expected range.
  4. Verify token estimation is used for context building.
- Expected Result:
  - Token counting for context estimation works correctly.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_token_counting.py\`
  - Framework: pytest
- Notes: Tests token counting for context estimation

### TC-ID: TC-UNIT-414
- Type: unit
- Related Requirements:
  - REQ-414
- Related Modules:
  - MOD-BE-Core, MOD-BE-Templates
- Pre-Conditions:
  - MessageTemplateService initialized.
  - No templates exist yet.
- Test Steps:
  1. Create a template with title="Code Review", content="Review this code: {{code}}".
  2. Call \`create_template(...)\`.
  3. Verify template is stored with id and created_at.
  4. Call \`get_template(template_id)\`.
  5. Verify template is retrieved correctly.
- Expected Result:
  - Templates can be created and retrieved.
- Status: implemented
- Automation Location:
  - File: \`tests/test_message_templates.py\`
  - Framework: pytest
- Notes: Tests template creation and management

### TC-ID: TC-UNIT-417
- Type: unit
- Related Requirements:
  - REQ-417
- Related Modules:
  - MOD-BE-Core, MOD-BE-Templates
- Pre-Conditions:
  - A template exists.
- Test Steps:
  1. **Create:** POST /api/templates with title, content, category.
  2. **Read:** GET /api/templates/{template_id}.
  3. **Update:** PUT /api/templates/{template_id} with new content.
  4. **Delete:** DELETE /api/templates/{template_id}.
  5. Verify all operations succeeded.
- Expected Result:
  - Full template CRUD operations work.
- Status: implemented
- Automation Location:
  - File: \`tests/test_message_templates.py\`
  - Framework: pytest
- Notes: Tests template CRUD operations

### TC-ID: TC-UNIT-418
- Type: unit
- Related Requirements:
  - REQ-418
- Related Modules:
  - MOD-BE-Core, MOD-BE-Templates
- Pre-Conditions:
  - A template with placeholders exists: "Review {{language}} code: {{code}}".
- Test Steps:
  1. Call \`substitute_parameters(template_id, {"language": "Python", "code": "x = 1"})\`.
  2. Verify {{language}} is replaced with "Python".
  3. Verify {{code}} is replaced with "x = 1".
  4. Verify result is: "Review Python code: x = 1".
- Expected Result:
  - Template parameter substitution works with regex-based replacement.
- Status: implemented
- Automation Location:
  - File: \`tests/test_message_templates.py\`
  - Framework: pytest
- Notes: Tests template parameter substitution with regex

## 5. Backend Tests - AI Provider Integration (REQ-501 to REQ-524)

### TC-ID: TC-UNIT-501
- Type: unit
- Related Requirements:
  - REQ-501
- Related Modules:
  - MOD-BE-Core, MOD-BE-Providers
- Pre-Conditions:
  - AIProviderService initialized.
  - Multiple provider API keys configured in .env.
- Test Steps:
  1. Call \`get_providers()\`.
  2. Verify OpenAI provider is in list.
  3. Verify Anthropic provider is in list.
  4. Verify each provider has unique api_key_env_var.
- Expected Result:
  - Multiple providers are supported and listed.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_multiple_provider_support.py\`
  - Framework: pytest
- Notes: Tests multiple provider support

### TC-ID: TC-UNIT-502
- Type: unit
- Related Requirements:
  - REQ-502
- Related Modules:
  - MOD-BE-Core, MOD-BE-Providers
- Pre-Conditions:
  - Two providers configured with different API keys.
- Test Steps:
  1. Verify OpenAI has OPENAI_API_KEY set.
  2. Verify Anthropic has ANTHROPIC_API_KEY set.
  3. Verify API keys are different.
  4. Verify each provider can authenticate independently.
- Expected Result:
  - Each provider has unique authentication.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_provider_authentication.py\`
  - Framework: pytest
- Notes: Tests unique provider authentication

### TC-ID: TC-UNIT-503
- Type: unit
- Related Requirements:
  - REQ-503
- Related Modules:
  - MOD-BE-Core, MOD-BE-Providers
- Pre-Conditions:
  - AIProviderService initialized.
- Test Steps:
  1. Get OpenAI provider config.
  2. Verify temperature parameter is set.
  3. Verify max_tokens parameter is set.
  4. Verify base_url is set for provider.
  5. Verify model list is populated.
- Expected Result:
  - Provider-specific parameters are configured correctly.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_provider_parameters.py\`
  - Framework: pytest
- Notes: Tests provider-specific parameters

### TC-ID: TC-UNIT-504
- Type: unit
- Related Requirements:
  - REQ-504
- Related Modules:
  - MOD-BE-Core, MOD-BE-Providers, MOD-BE-Settings
- Pre-Conditions:
  - .env file contains provider configurations.
- Test Steps:
  1. Read provider config from .env.
  2. Verify each provider section is loaded.
  3. Verify api_key, base_url, model fields are present.
  4. Verify configuration is applied to AIProviderService.
- Expected Result:
  - Provider configurations are loaded from .env file.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_provider_env_config.py\`
  - Framework: pytest
- Notes: Tests provider config in .env

### TC-ID: TC-UNIT-505
- Type: unit
- Related Requirements:
  - REQ-505
- Related Modules:
  - MOD-BE-Core, MOD-BE-Providers
- Pre-Conditions:
  - One provider has API key configured, one doesn't.
- Test Steps:
  1. Call \`get_available_providers()\`.
  2. Verify only configured provider is in list.
  3. Verify unconfigured provider is not in list.
  4. Set API key for second provider.
  5. Call \`get_available_providers()\` again.
  6. Verify second provider now appears.
- Expected Result:
  - Provider availability is dynamic based on API key presence.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_dynamic_provider_availability.py\`
  - Framework: pytest
- Notes: Tests dynamic provider availability

### TC-ID: TC-UNIT-515
- Type: unit
- Related Requirements:
  - REQ-515
- Related Modules:
  - MOD-BE-Core, MOD-BE-Providers
- Pre-Conditions:
  - ConversationService with message history exists.
- Test Steps:
  1. Format message list for OpenAI provider.
  2. Verify format includes system role format.
  3. Verify format for Anthropic is different (uses Human/Assistant).
  4. Verify each provider formats correctly.
- Expected Result:
  - Messages are formatted correctly for each provider's API.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_provider_message_formatting.py\`
  - Framework: pytest
- Notes: Tests provider-specific message formatting

### TC-ID: TC-UNIT-516
- Type: unit
- Related Requirements:
  - REQ-516
- Related Modules:
  - MOD-BE-Core, MOD-BE-Providers, MOD-BE-Conversations
- Pre-Conditions:
  - Message formatting logic exists.
- Test Steps:
  1. Create message list for OpenAI.
  2. Verify first message is role='system' with system prompt.
  3. Verify system prompt is not user-created.
  4. Verify subsequent messages are user/assistant pairs.
- Expected Result:
  - System prompt is included at the start of formatted messages.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_system_prompt_inclusion.py\`
  - Framework: pytest
- Notes: Tests system prompt inclusion

### TC-ID: TC-UNIT-517
- Type: unit
- Related Requirements:
  - REQ-517
- Related Modules:
  - MOD-BE-Core, MOD-BE-Conversations
- Pre-Conditions:
  - A session with 20 messages exists.
- Test Steps:
  1. Call \`build_context(session_id)\`.
  2. Verify context includes all message history.
  3. Verify messages are in chronological order.
  4. Verify each message is properly formatted for AI.
- Expected Result:
  - Message history is included as context for AI requests.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_message_history_context.py\`
  - Framework: pytest
- Notes: Tests message history as context

### TC-ID: TC-UNIT-518
- Type: unit
- Related Requirements:
  - REQ-518
- Related Modules:
  - MOD-BE-Core, MOD-BE-Providers
- Pre-Conditions:
  - Provider configuration with temperature=0.7, max_tokens=2000 exists.
- Test Steps:
  1. Prepare API request for OpenAI.
  2. Verify temperature is set to 0.7 in request.
  3. Verify max_tokens is set to 2000 in request.
  4. Verify config is applied correctly before sending to API.
- Expected Result:
  - Provider configuration parameters are applied to API requests.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_provider_config_application.py\`
  - Framework: pytest
- Notes: Tests provider configuration application

### TC-ID: TC-UNIT-519
- Type: unit
- Related Requirements:
  - REQ-519
- Related Modules:
  - MOD-BE-Core, MOD-BE-Providers
- Pre-Conditions:
  - Mock response from OpenAI API exists.
- Test Steps:
  1. Call \`parse_response(provider_id='openai', response=mock_response)\`.
  2. Verify text is extracted.
  3. Verify tokens dict is parsed.
  4. Verify finish_reason is extracted.
- Expected Result:
  - Provider responses are parsed correctly to extract relevant data.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_provider_response_parsing.py\`
  - Framework: pytest
- Notes: Tests provider response parsing

### TC-ID: TC-UNIT-520
- Type: unit
- Related Requirements:
  - REQ-520
- Related Modules:
  - MOD-BE-Core, MOD-BE-Providers
- Pre-Conditions:
  - Mock OpenAI response with choices[0].message.content exists.
- Test Steps:
  1. Extract text from OpenAI response.
  2. Verify text is exactly as returned by API.
  3. Extract text from Anthropic response.
  4. Verify format is different but text is correct.
- Expected Result:
  - Text is correctly extracted from provider-specific response formats.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_text_extraction.py\`
  - Framework: pytest
- Notes: Tests text extraction from response

### TC-ID: TC-UNIT-521
- Type: unit
- Related Requirements:
  - REQ-521
- Related Modules:
  - MOD-BE-Core, MOD-BE-Providers
- Pre-Conditions:
  - Mock response with usage.prompt_tokens and usage.completion_tokens.
- Test Steps:
  1. Extract token usage from OpenAI response.
  2. Verify prompt_tokens is extracted.
  3. Verify completion_tokens is extracted.
  4. Verify total_tokens = prompt + completion.
- Expected Result:
  - Token usage is correctly extracted from responses.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_token_usage_extraction.py\`
  - Framework: pytest
- Notes: Tests token usage extraction

### TC-ID: TC-UNIT-524
- Type: unit
- Related Requirements:
  - REQ-524
- Related Modules:
  - MOD-BE-Core, MOD-BE-Conversations
- Pre-Conditions:
  - AI response with tokens and finish_reason exists.
- Test Steps:
  1. Create Message object with provider_id, tokens, finish_reason.
  2. Save message to session.
  3. Reload session.
  4. Verify all metadata is persisted.
- Expected Result:
  - Response metadata (provider, tokens, finish_reason) persists correctly.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_response_metadata_persistence.py\`
  - Framework: pytest
- Notes: Tests response metadata persistence

## 6. Backend Tests - File Management (REQ-601 to REQ-614)

### TC-ID: TC-UNIT-601
- Type: unit
- Related Requirements:
  - REQ-601
- Related Modules:
  - MOD-BE-Core, MOD-BE-Files
- Pre-Conditions:
  - FileManagementService initialized.
  - A project exists.
- Test Steps:
  1. Create a test file (e.g., test.txt).
  2. Call \`upload_file(file, scope='project', scope_id=project_id)\`.
  3. Verify file is stored in data/projects/{project-id}/files/.
  4. Verify File object is returned with id, name, size, type.
  5. Verify metadata is recorded.
- Expected Result:
  - Files are uploaded with complete metadata.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_file_upload.py\`
  - Framework: pytest
- Notes: Tests file upload with metadata

### TC-ID: TC-UNIT-602
- Type: unit
- Related Requirements:
  - REQ-602
- Related Modules:
  - MOD-BE-Core, MOD-BE-Files
- Pre-Conditions:
  - A file is uploaded to a project.
- Test Steps:
  1. Call \`get_project_files(project_id)\`.
  2. Verify returned list includes uploaded file.
  3. Verify file metadata is complete.
  4. Verify no other projects' files are included.
- Expected Result:
  - Project files are accessible and isolated.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_project_file_accessibility.py\`
  - Framework: pytest
- Notes: Tests project file accessibility

### TC-ID: TC-UNIT-606
- Type: unit
- Related Requirements:
  - REQ-606
- Related Modules:
  - MOD-BE-Core, MOD-BE-Files
- Pre-Conditions:
  - A file is uploaded.
- Test Steps:
  1. Verify file metadata in parent metadata.json includes: id, name, path, size, type, uploaded_at, uploader.
  2. Verify all fields are populated correctly.
- Expected Result:
  - File metadata is stored completely.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_file_metadata_storage.py\`
  - Framework: pytest
- Notes: Tests file metadata storage

### TC-ID: TC-UNIT-607
- Type: unit
- Related Requirements:
  - REQ-607
- Related Modules:
  - MOD-BE-Core, MOD-BE-Files
- Pre-Conditions:
  - FileManagementService initialized.
- Test Steps:
  1. Upload file of type .txt.
  2. Upload file of type .pdf.
  3. Upload file of type .json.
  4. Verify each is stored correctly.
  5. Verify MIME types are recorded correctly.
- Expected Result:
  - Multiple file types are supported.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_multiple_file_types.py\`
  - Framework: pytest
- Notes: Tests multiple file type support

### TC-ID: TC-UNIT-608
- Type: unit
- Related Requirements:
  - REQ-608
- Related Modules:
  - MOD-BE-Core, MOD-BE-Files
- Pre-Conditions:
  - File size limits are configured (50MB per file, 500MB per project).
- Test Steps:
  1. Try to upload a 60MB file.
  2. Verify upload fails with proper error message.
  3. Upload a 40MB file.
  4. Verify upload succeeds.
  5. Try to upload another 400MB file.
  6. Verify project size limit is enforced.
- Expected Result:
  - File size limits are enforced correctly.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_file_size_limits.py\`
  - Framework: pytest
- Notes: Tests file size limits enforcement

### TC-ID: TC-UNIT-609
- Type: unit
- Related Requirements:
  - REQ-609
- Related Modules:
  - MOD-BE-Core, MOD-BE-Files, MOD-BE-ChatSessions
- Pre-Conditions:
  - A chat session exists.
  - FileManagementService initialized.
- Test Steps:
  1. Call \`upload_file(file, scope='session', scope_id=session_id)\`.
  2. Verify file is stored in data/chat_sessions/{session-id}/files/.
  3. Verify file is accessible via \`get_session_files(session_id)\`.
- Expected Result:
  - Files can be uploaded to chat sessions.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_session_file_upload.py\`
  - Framework: pytest
- Notes: Tests session-specific file upload

### TC-ID: TC-UNIT-610
- Type: unit
- Related Requirements:
  - REQ-610
- Related Modules:
  - MOD-BE-Core, MOD-BE-Files, MOD-BE-ChatSessions
- Pre-Conditions:
  - Two sessions exist, each with files.
- Test Steps:
  1. Call \`get_session_files(session_id_1)\`.
  2. Verify only Session 1 files are returned.
  3. Call \`get_session_files(session_id_2)\`.
  4. Verify only Session 2 files are returned.
- Expected Result:
  - Session files are isolated per session.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_session_file_isolation.py\`
  - Framework: pytest
- Notes: Tests session file isolation

### TC-ID: TC-UNIT-614
- Type: unit
- Related Requirements:
  - REQ-614
- Related Modules:
  - MOD-BE-Core, MOD-BE-Files
- Pre-Conditions:
  - A session-specific file is uploaded.
- Test Steps:
  1. Verify session file metadata includes: id, name, path, size, type, uploaded_at, uploader.
  2. Verify all fields are populated correctly.
  3. Verify metadata is stored in session metadata.json.
- Expected Result:
  - Session file metadata is stored completely.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_session_file_metadata.py\`
  - Framework: pytest
- Notes: Tests session file metadata

## 7. Backend Tests - Settings & Configuration (REQ-705 to REQ-710)

### TC-ID: TC-UNIT-705
- Type: unit
- Related Requirements:
  - REQ-705
- Related Modules:
  - MOD-BE-Core, MOD-BE-Settings
- Pre-Conditions:
  - SettingsService initialized.
- Test Steps:
  1. Attempt to set invalid API key format for OpenAI (e.g., "invalid").
  2. Verify validation fails.
  3. Set valid API key format (e.g., "sk-...").
  4. Verify validation passes.
- Expected Result:
  - API key format is validated correctly.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_api_key_validation.py\`
  - Framework: pytest
- Notes: Tests API key format validation

### TC-ID: TC-UNIT-706
- Type: unit
- Related Requirements:
  - REQ-706
- Related Modules:
  - MOD-BE-Core, MOD-BE-Settings
- Pre-Conditions:
  - SettingsService initialized.
  - Mock API exists to test connection.
- Test Steps:
  1. Call \`test_api_key(provider='openai', api_key='valid_key')\`.
  2. Verify API call is made (mocked).
  3. Verify valid result is returned.
  4. Call \`test_api_key(provider='openai', api_key='invalid_key')\`.
  5. Verify invalid result is returned.
- Expected Result:
  - API keys can be tested for validity.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_api_key_testing.py\`
  - Framework: pytest
- Notes: Tests API key testing

### TC-ID: TC-UNIT-708
- Type: unit
- Related Requirements:
  - REQ-708
- Related Modules:
  - MOD-BE-Core, MOD-BE-Settings
- Pre-Conditions:
  - SettingsService initialized.
- Test Steps:
  1. Call \`update_settings({"api_providers": {"openai": {"api_key": "new_key"}}})\`.
  2. Call \`save_env_vars({"OPENAI_API_KEY": "new_key"})\`.
  3. Read .env file manually.
  4. Verify "OPENAI_API_KEY=new_key" is in .env.
- Expected Result:
  - API keys are saved to .env file.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_api_keys_env_save.py\`
  - Framework: pytest
- Notes: Tests API keys saved to .env

### TC-ID: TC-UNIT-709
- Type: unit
- Related Requirements:
  - REQ-709
- Related Modules:
  - MOD-BE-Core, MOD-BE-Settings
- Pre-Conditions:
  - Application is running with old API key.
  - .env file can be edited.
- Test Steps:
  1. Get current settings (should have old API key).
  2. Manually edit .env file with new API key.
  3. Reload SettingsService or trigger reload endpoint.
  4. Get settings again.
  5. Verify new API key is loaded without restart.
- Expected Result:
  - .env updates are loaded without application restart.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_env_hot_reload.py\`
  - Framework: pytest
- Notes: Tests .env hot-reload

### TC-ID: TC-UNIT-710
- Type: unit
- Related Requirements:
  - REQ-710
- Related Modules:
  - MOD-BE-Core, MOD-BE-Settings
- Pre-Conditions:
  - API keys are configured.
- Test Steps:
  1. Verify API keys are NOT printed in debug logs.
  2. Verify API keys are NOT exposed in API responses (only presence).
  3. Verify API keys are stored securely in .env (read-only on server).
  4. Attempt to access .env from API endpoint (should fail).
- Expected Result:
  - API keys are stored and handled securely server-side only.
- Status: proposed
- Automation Location:
  - File: \`tests/unit/test_secure_api_key_storage.py\`
  - Framework: pytest
- Notes: Tests secure API key storage

## 8. Backend Tests - Search Functionality (REQ-306)

### TC-ID: TC-FUNC-306
- Type: functional
- Related Requirements:
  - REQ-306
- Related Modules:
  - MOD-BE-Core, MOD-BE-Search
- Pre-Conditions:
  - Multiple sessions with messages exist.
  - SearchService initialized.
- Test Steps:
  1. Add messages with keywords "python", "code", "review".
  2. Call \`search_messages(query='python', scope='project', scope_id=project_id)\`.
  3. Verify messages containing "python" are returned.
  4. Search for "code".
  5. Verify matching messages are returned.
  6. Verify regex-based search works.
- Expected Result:
  - Messages can be searched by keyword within project scope.
- Status: proposed
- Automation Location:
  - File: \`tests/functional/test_message_search.py\`
  - Framework: pytest
- Notes: Tests regex-based message search

## 9. Backend Functional & Integration Tests

### TC-ID: TC-FUNC-404
- Type: functional
- Related Requirements:
  - REQ-404
- Related Modules:
  - MOD-BE-Core, MOD-BE-Conversations
- Pre-Conditions:
  - A session with message history exists.
  - ConversationService initialized.
- Test Steps:
  1. Call \`GET /api/conversations/history/{session_id}\`.
  2. Verify response includes all messages.
  3. Verify messages are in chronological order.
  4. Verify response structure is correct.
- Expected Result:
  - Message history can be retrieved via API endpoint.
- Status: implemented
- Automation Location:
  - File: \`tests/test_api_endpoints.py\`
  - Framework: pytest
- Notes: Tests message history API retrieval

### TC-ID: TC-FUNC-406
- Type: functional
- Related Requirements:
  - REQ-406
- Related Modules:
  - MOD-BE-Core, MOD-BE-Conversations
- Pre-Conditions:
  - AI provider API is mocked to fail.
- Test Steps:
  1. Call \`POST /api/conversations/send\` with message.
  2. Mock API returns error.
  3. Verify error message is returned to client.
  4. Verify message status is set to 'failed'.
- Expected Result:
  - Error messages from failed API calls are handled and returned.
- Status: implemented
- Automation Location:
  - File: \`tests/test_api_endpoints.py\`
  - Framework: pytest
- Notes: Tests error message handling

### TC-ID: TC-FUNC-407
- Type: functional
- Related Requirements:
  - REQ-407
- Related Modules:
  - MOD-BE-Core, MOD-BE-Conversations
- Pre-Conditions:
  - A message with status='failed' exists.
- Test Steps:
  1. Call \`POST /api/conversations/send\` again with same message content.
  2. Verify message is resent.
  3. Verify new message gets new id and timestamp.
- Expected Result:
  - Failed messages can be retried.
- Status: implemented
- Automation Location:
  - File: \`tests/test_api_endpoints.py\`
  - Framework: pytest
- Notes: Tests message retry functionality

### TC-ID: TC-FUNC-603
- Type: functional
- Related Requirements:
  - REQ-603
- Related Modules:
  - MOD-BE-Core, MOD-BE-Files
- Pre-Conditions:
  - Multiple files are uploaded to a project.
- Test Steps:
  1. Call \`GET /api/files/projects/{project_id}\`.
  2. Verify response includes all files with metadata.
  3. Verify each file has id, name, size, type, uploaded_at.
- Expected Result:
  - Project files can be listed via API.
- Status: implemented
- Automation Location:
  - File: \`tests/test_api_endpoints.py\`
  - Framework: pytest
- Notes: Tests project files listing

### TC-ID: TC-FUNC-604
- Type: functional
- Related Requirements:
  - REQ-604
- Related Modules:
  - MOD-BE-Core, MOD-BE-Files
- Pre-Conditions:
  - A file is uploaded to a project.
- Test Steps:
  1. Call \`GET /api/files/{file_id}/download\`.
  2. Verify file content is returned.
  3. Verify content-type header is correct.
  4. Verify file can be saved locally.
- Expected Result:
  - Files can be downloaded via API.
- Status: implemented
- Automation Location:
  - File: \`tests/test_api_endpoints.py\`
  - Framework: pytest
- Notes: Tests file download

### TC-ID: TC-FUNC-611
- Type: functional
- Related Requirements:
  - REQ-611
- Related Modules:
  - MOD-BE-Core, MOD-BE-Files, MOD-BE-ChatSessions
- Pre-Conditions:
  - Files are uploaded to a session.
- Test Steps:
  1. Call \`GET /api/files/sessions/{session_id}\` (if endpoint exists).
  2. Verify session files are listed.
  3. Verify only session-scoped files are returned.
- Expected Result:
  - Session files can be listed.
- Status: implemented
- Automation Location:
  - File: \`tests/test_api_endpoints.py\`
  - Framework: pytest
- Notes: Tests session files listing

### TC-ID: TC-FUNC-706
- Type: functional
- Related Requirements:
  - REQ-706
- Related Modules:
  - MOD-BE-Core, MOD-BE-Settings
- Pre-Conditions:
  - SettingsService initialized.
  - Mock API exists.
- Test Steps:
  1. Call \`POST /api/settings/test-api-key\` with provider and key.
  2. Verify valid key returns success response.
  3. Verify invalid key returns error response.
  4. Verify HTTP status codes are correct (200 vs 400/401).
- Expected Result:
  - API key can be tested via endpoint.
- Status: implemented
- Automation Location:
  - File: \`tests/test_api_endpoints.py\`
  - Framework: pytest
- Notes: Tests API key test endpoint

## 10. Backend E2E Tests (Optional)

### TC-ID: TC-E2E-001
- Type: e2e
- Related Requirements:
  - REQ-201, REQ-213, REQ-401, REQ-501
- Related Modules:
  - MOD-BE-Core, MOD-BE-Projects, MOD-BE-ChatSessions, MOD-BE-Conversations, MOD-BE-Providers
- Pre-Conditions:
  - Full application is running.
  - OpenAI API key is configured (or mocked).
- Test Steps:
  1. Create a new project.
  2. Create a chat session under that project.
  3. Send a message to AI.
  4. Receive AI response.
  5. Verify complete message flow is persisted.
  6. Reload application.
  7. Verify all data is still present.
- Expected Result:
  - Complete chat workflow works end-to-end.
- Status: implemented
- Automation Location:
  - File: \`tests/test_e2e_workflows.py\`
  - Framework: pytest
- Notes: Tests complete chat workflow (project → session → message → response → persistence)

### TC-ID: TC-E2E-002
- Type: e2e
- Related Requirements:
  - REQ-501, REQ-505, REQ-514, REQ-524
- Related Modules:
  - MOD-BE-Core, MOD-BE-Providers, MOD-BE-Conversations
- Pre-Conditions:
  - OpenAI and Anthropic API keys configured (or mocked).
- Test Steps:
  1. Send a message with provider='openai'.
  2. Verify response is from OpenAI.
  3. Send another message with provider='anthropic'.
  4. Verify response is from Anthropic.
  5. Verify both responses are stored with correct provider_id.
  6. Verify can switch providers mid-session.
- Expected Result:
  - Multi-provider switching within a session works.
- Status: implemented
- Automation Location:
  - File: \`tests/test_e2e_workflows.py\`
  - Framework: pytest
- Notes: Tests multi-provider switching

### TC-ID: TC-E2E-003
- Type: e2e
- Related Requirements:
  - REQ-601, REQ-609, REQ-411, REQ-412, REQ-514
- Related Modules:
  - MOD-BE-Core, MOD-BE-Files, MOD-BE-Conversations, MOD-BE-Providers
- Pre-Conditions:
  - FileManagementService initialized.
  - Project has uploaded files.
- Test Steps:
  1. Upload a file to project.
  2. Send a message requesting analysis of the file.
  3. Verify file is included in AI context.
  4. Verify AI response references the file.
  5. Verify message persists with file reference.
- Expected Result:
  - File upload and context inclusion in AI request works end-to-end.
- Status: implemented
- Automation Location:
  - File: \`tests/test_e2e_workflows.py\`
  - Framework: pytest
- Notes: Tests file upload and context inclusion

### TC-ID: TC-E2E-004
- Type: e2e
- Related Requirements:
  - REQ-414, REQ-418, REQ-401, REQ-403, REQ-409
- Related Modules:
  - MOD-BE-Core, MOD-BE-Templates, MOD-BE-Conversations
- Pre-Conditions:
  - MessageTemplateService initialized.
- Test Steps:
  1. Create a template "Code Review: {{code}}".
  2. Insert template into message with code="def foo(): pass".
  3. Send message to AI.
  4. Verify template substitution happened.
  5. Verify AI response is stored.
  6. Verify message history shows substituted content.
- Expected Result:
  - Template usage end-to-end (create → substitute → send → save) works.
- Status: implemented
- Automation Location:
  - File: \`tests/test_e2e_workflows.py\`
  - Framework: pytest
- Notes: Tests template usage end-to-end

### TC-ID: TC-E2E-005
- Type: e2e
- Related Requirements:
  - REQ-206, REQ-214, REQ-213
- Related Modules:
  - MOD-BE-Core, MOD-BE-ChatSessions, MOD-BE-Conversations
- Pre-Conditions:
  - Two sessions exist under same project.
  - Both have different message histories.
- Test Steps:
  1. Add 10 messages to Session A.
  2. Add 5 messages to Session B.
  3. Verify Session A has 10 messages.
  4. Verify Session B has 5 messages.
  5. Send message to Session A.
  6. Verify it doesn't affect Session B.
  7. Delete Session A.
  8. Verify Session B data is unaffected.
- Expected Result:
  - Cross-session data isolation is maintained.
- Status: implemented
- Automation Location:
  - File: \`tests/test_e2e_workflows.py\`
  - Framework: pytest
- Notes: Tests cross-session data isolation

## 11. Test Implementation Status Summary

| Test Category | Count | Status | Notes |
|---|---|---|---|
| Unit Tests (Foundation & Architecture) | 8 | proposed | REQ-101 to REQ-112 |
| Unit Tests (Workspace Organization) | 5 | proposed | REQ-201, REQ-209, REQ-210, REQ-213, REQ-214 |
| Unit Tests (Chat & Messaging) | 9 | proposed | REQ-401-405, REQ-409, REQ-411-413, REQ-414, REQ-417-418 |
| Unit Tests (AI Provider Integration) | 11 | proposed | REQ-501-505, REQ-515-521, REQ-524 |
| Unit Tests (File Management) | 8 | proposed | REQ-601-602, REQ-606-610, REQ-614 |
| Unit Tests (Settings & Configuration) | 6 | proposed | REQ-705-706, REQ-708-710 |
| Functional Tests (Search) | 1 | proposed | REQ-306 |
| Functional Tests (API Endpoints) | 7 | proposed | REQ-404, REQ-406-407, REQ-603-604, REQ-611, REQ-706 |
| E2E Tests | 5 | proposed | Complete workflows |
| **Total** | **60** | **proposed** | Full backend coverage |
