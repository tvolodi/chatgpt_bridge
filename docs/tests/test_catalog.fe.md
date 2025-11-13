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

## 2. Frontend Tests - Main Screen & Layout (REQ-301 to REQ-314)

### TC-ID: TC-UNIT-301
- Type: unit
- Related Requirements:
  - REQ-301
- Related Modules:
  - MOD-FE-Core, COM-HEADER
- Pre-Conditions:
  - React test environment configured.
  - Header component mounted.
- Test Steps:
  1. Render Header component.
  2. Verify header element has height ~80px.
  3. Verify header has fixed positioning.
  4. Verify all child elements are rendered.
- Expected Result:
  - Header renders at correct height with all elements present.
- Status: proposed
- Automation Location:
  - File: `src/test/components/Header.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests header bar rendering

### TC-ID: TC-UNIT-302
- Type: unit
- Related Requirements:
  - REQ-302
- Related Modules:
  - MOD-FE-Core, COM-STATUSBAR
- Pre-Conditions:
  - StatusBar component mounted.
  - Project and session data available.
- Test Steps:
  1. Render StatusBar component.
  2. Pass project name prop.
  3. Pass session name prop.
  4. Verify status bar displays project path.
  5. Verify status bar displays session name.
- Expected Result:
  - Status bar displays correct project and session information.
- Status: proposed
- Automation Location:
  - File: `src/test/components/StatusBar.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests status bar display

### TC-ID: TC-UNIT-303
- Type: unit
- Related Requirements:
  - REQ-303
- Related Modules:
  - MOD-FE-Core, COM-SIDEBAR
- Pre-Conditions:
  - Sidebar component mounted.
  - Toggle functionality implemented.
- Test Steps:
  1. Render Sidebar component.
  2. Click toggle button to collapse.
  3. Verify sidebar width becomes 0 or hidden.
  4. Click toggle button to expand.
  5. Verify sidebar width returns to ~280px.
- Expected Result:
  - Sidebar can be toggled between expanded and collapsed states.
- Status: proposed
- Automation Location:
  - File: `src/test/components/Sidebar.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests sidebar resizable toggle

### TC-ID: TC-UNIT-305
- Type: unit
- Related Requirements:
  - REQ-305
- Related Modules:
  - MOD-FE-Core, COM-HEADER
- Pre-Conditions:
  - Header component rendered.
- Test Steps:
  1. Render Header.
  2. Find element with text "AI Chat Assistant".
  3. Verify title is visible and correct.
  4. Verify title is in a prominent location (header).
- Expected Result:
  - Application title displays correctly in header.
- Status: proposed
- Automation Location:
  - File: `src/test/components/Header.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests app title display

### TC-ID: TC-UNIT-307
- Type: unit
- Related Requirements:
  - REQ-307
- Related Modules:
  - MOD-FE-Core, COM-PROVIDER-SEL
- Pre-Conditions:
  - ProviderSelector component rendered.
  - Mock providers available.
- Test Steps:
  1. Render ProviderSelector.
  2. Click dropdown to open.
  3. Verify list shows available providers.
  4. Verify current provider is highlighted.
  5. Click another provider.
  6. Verify selection changes.
- Expected Result:
  - Provider selector dropdown shows and switches providers.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ProviderSelector.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests provider selector dropdown

### TC-ID: TC-UNIT-308
- Type: unit
- Related Requirements:
  - REQ-308
- Related Modules:
  - MOD-FE-Core, COM-HEADER
- Pre-Conditions:
  - Header component rendered.
- Test Steps:
  1. Render Header.
  2. Find Settings button.
  3. Click Settings button.
  4. Verify navigation occurs or modal opens.
- Expected Result:
  - Settings button is present and functional.
- Status: proposed
- Automation Location:
  - File: `src/test/components/Header.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests settings button

### TC-ID: TC-UNIT-309
- Type: unit
- Related Requirements:
  - REQ-309
- Related Modules:
  - MOD-FE-Core, COM-USERMENU
- Pre-Conditions:
  - UserMenu component rendered.
- Test Steps:
  1. Render UserMenu.
  2. Click user profile icon.
  3. Verify dropdown menu opens.
  4. Verify logout option is present.
  5. Click logout.
  6. Verify logout is triggered.
- Expected Result:
  - User menu dropdown opens and logout works.
- Status: proposed
- Automation Location:
  - File: `src/test/components/UserMenu.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests user menu dropdown

### TC-ID: TC-UNIT-310
- Type: unit
- Related Requirements:
  - REQ-310
- Related Modules:
  - MOD-FE-Core, COM-PROJECTTREE
- Pre-Conditions:
  - ProjectTree component rendered.
  - Mock hierarchical project data provided.
- Test Steps:
  1. Render ProjectTree with nested projects.
  2. Verify parent projects display.
  3. Click expand icon on parent.
  4. Verify child projects appear.
  5. Verify hierarchy is visually correct.
- Expected Result:
  - Project tree renders hierarchically and expands/collapses.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ProjectTree.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests project tree hierarchical rendering

### TC-ID: TC-UNIT-311
- Type: unit
- Related Requirements:
  - REQ-311
- Related Modules:
  - MOD-FE-Core, COM-SIDEBAR
- Pre-Conditions:
  - Sidebar rendered.
  - Project selected.
  - Sessions under project exist.
- Test Steps:
  1. Select a project.
  2. Verify sessions list appears below project.
  3. Verify each session displays with name.
  4. Click a session.
  5. Verify session is highlighted.
- Expected Result:
  - Session list displays under current project.
- Status: proposed
- Automation Location:
  - File: `src/test/components/Sidebar.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests session list in sidebar

### TC-ID: TC-UNIT-313
- Type: unit
- Related Requirements:
  - REQ-313
- Related Modules:
  - MOD-FE-Core, COM-SIDEBAR
- Pre-Conditions:
  - Sidebar rendered.
- Test Steps:
  1. Locate "New Project" button in sidebar.
  2. Click button.
  3. Verify modal dialog opens.
  4. Verify form fields appear (name, description, etc.).
- Expected Result:
  - New Project button opens modal dialog.
- Status: proposed
- Automation Location:
  - File: `src/test/components/Sidebar.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests new project button

### TC-ID: TC-UNIT-314
- Type: unit
- Related Requirements:
  - REQ-314
- Related Modules:
  - MOD-FE-Core, COM-SIDEBAR
- Pre-Conditions:
  - Sidebar rendered.
  - Project selected.
- Test Steps:
  1. Locate "New Session" button in sidebar.
  2. Verify button is enabled only when project is selected.
  3. Click button.
  4. Verify session modal opens.
- Expected Result:
  - New Session button opens modal when project is selected.
- Status: proposed
- Automation Location:
  - File: `src/test/components/Sidebar.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests new session button

## 3. Frontend Tests - Chat Display & Input (REQ-315 to REQ-325)

### TC-ID: TC-UNIT-315
- Type: unit
- Related Requirements:
  - REQ-315
- Related Modules:
  - MOD-FE-Core, COM-CHATMESSAGE
- Pre-Conditions:
  - ChatMessage component rendered.
  - Message data provided.
- Test Steps:
  1. Render ChatMessage with user message.
  2. Verify message displays in bubble format.
  3. Render ChatMessage with AI message.
  4. Verify both render correctly.
- Expected Result:
  - Messages display in bubble format.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ChatMessage.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests message bubble rendering

### TC-ID: TC-UNIT-316
- Type: unit
- Related Requirements:
  - REQ-316
- Related Modules:
  - MOD-FE-Core, COM-CHATMESSAGE
- Pre-Conditions:
  - ChatMessage component rendered.
- Test Steps:
  1. Render message with role='user'.
  2. Verify message aligns to right.
  3. Render message with role='assistant'.
  4. Verify message aligns to left.
  5. Verify alignment is consistent across messages.
- Expected Result:
  - User messages align right, AI messages align left.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ChatMessage.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests message alignment per role

### TC-ID: TC-UNIT-317
- Type: unit
- Related Requirements:
  - REQ-317
- Related Modules:
  - MOD-FE-Core, COM-CHATMESSAGE
- Pre-Conditions:
  - ChatMessage with timestamp prop rendered.
- Test Steps:
  1. Render ChatMessage with timestamp.
  2. Extract timestamp text.
  3. Verify format is HH:MM or similar.
  4. Verify timestamp is readable.
- Expected Result:
  - Timestamp displays in correct format.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ChatMessage.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests timestamp display

### TC-ID: TC-UNIT-318
- Type: unit
- Related Requirements:
  - REQ-318
- Related Modules:
  - MOD-FE-Core, COM-CHATMESSAGE
- Pre-Conditions:
  - ChatMessage with AI response rendered.
  - Provider ID provided.
- Test Steps:
  1. Render ChatMessage with role='assistant' and provider_id='openai'.
  2. Verify provider name displays (e.g., "OpenAI").
  3. Render with provider_id='anthropic'.
  4. Verify provider name updates.
- Expected Result:
  - Provider name displays under AI messages.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ChatMessage.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests provider name display

### TC-ID: TC-UNIT-321
- Type: unit
- Related Requirements:
  - REQ-321
- Related Modules:
  - MOD-FE-Core, COM-CHATMESSAGE
- Pre-Conditions:
  - ChatMessage rendered with copy button.
  - Clipboard API mocked.
- Test Steps:
  1. Render ChatMessage.
  2. Find copy button.
  3. Click copy button.
  4. Verify clipboard.writeText is called.
  5. Verify success feedback is shown.
- Expected Result:
  - Copy to clipboard button works.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ChatMessage.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests copy message to clipboard

### TC-ID: TC-UNIT-322
- Type: unit
- Related Requirements:
  - REQ-322
- Related Modules:
  - MOD-FE-Core, COM-CHATAREA
- Pre-Conditions:
  - ChatArea component rendered.
  - Message is being sent to API.
- Test Steps:
  1. Render ChatArea.
  2. Send a message (trigger loading state).
  3. Verify loading spinner displays.
  4. Verify spinner is visible during wait.
  5. AI response arrives and spinner disappears.
- Expected Result:
  - Loading indicator shows during AI response wait.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ChatArea.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests loading spinner display

### TC-ID: TC-UNIT-323
- Type: unit
- Related Requirements:
  - REQ-323
- Related Modules:
  - MOD-FE-Core, COM-CHATINPUT
- Pre-Conditions:
  - ChatInput component rendered.
- Test Steps:
  1. Render ChatInput with textarea.
  2. Type single line "Hello".
  3. Verify textarea height is normal.
  4. Type multiple lines (10 lines).
  5. Verify textarea auto-expands.
  6. Verify scroll appears if needed.
- Expected Result:
  - Textarea auto-expands with content (multi-line support).
- Status: proposed
- Automation Location:
  - File: `src/test/components/ChatInput.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests auto-expanding textarea

### TC-ID: TC-UNIT-324
- Type: unit
- Related Requirements:
  - REQ-324
- Related Modules:
  - MOD-FE-Core, COM-CHATINPUT
- Pre-Conditions:
  - ChatInput component rendered.
- Test Steps:
  1. Render ChatInput.
  2. Verify Send button is disabled when input is empty.
  3. Type text in input.
  4. Verify Send button becomes enabled.
  5. Clear input.
  6. Verify Send button is disabled again.
- Expected Result:
  - Send button is disabled when input is empty.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ChatInput.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests send button disabled state

### TC-ID: TC-UNIT-325
- Type: unit
- Related Requirements:
  - REQ-325
- Related Modules:
  - MOD-FE-Core, COM-CHATINPUT
- Pre-Conditions:
  - ChatInput with max character limit (10000).
- Test Steps:
  1. Render ChatInput.
  2. Verify character counter displays "0 / 10000".
  3. Type 500 characters.
  4. Verify counter shows "500 / 10000".
  5. Type near limit (9500 chars).
  6. Verify counter shows in warning state.
- Expected Result:
  - Character counter displays current/max count.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ChatInput.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests character counter display

## 4. Frontend Tests - Chat Features & Templates (REQ-414 to REQ-418)

### TC-ID: TC-UNIT-414
- Type: unit
- Related Requirements:
  - REQ-414
- Related Modules:
  - MOD-FE-Core, COM-TEMPLATE-MGR
- Pre-Conditions:
  - TemplateManager component rendered.
- Test Steps:
  1. Render TemplateManager.
  2. Verify template list displays.
  3. Verify each template shows title and preview.
  4. Verify "New Template" button is present.
- Expected Result:
  - Template list displays with all templates.
- Status: proposed
- Automation Location:
  - File: `src/test/components/TemplateManager.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests template manager display

### TC-ID: TC-UNIT-417
- Type: unit
- Related Requirements:
  - REQ-417
- Related Modules:
  - MOD-FE-Core, COM-TEMPLATE-MGR
- Pre-Conditions:
  - TemplateManager rendered with templates.
- Test Steps:
  1. **Create:** Click "New Template", fill form, save.
  2. **Read:** Template appears in list.
  3. **Update:** Click edit on template, modify content, save.
  4. **Delete:** Click delete, confirm, template removed.
  5. Verify all operations succeeded.
- Expected Result:
  - Full template CRUD works in UI.
- Status: proposed
- Automation Location:
  - File: `src/test/components/TemplateManager.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests template CRUD operations

### TC-ID: TC-UNIT-418
- Type: unit
- Related Requirements:
  - REQ-418
- Related Modules:
  - MOD-FE-Core, COM-TEMPLATE-MGR
- Pre-Conditions:
  - Template with parameters "Review {{language}} code: {{code}}" exists.
- Test Steps:
  1. Open template in editor.
  2. Fill parameter fields: language="Python", code="x = 1".
  3. Click "Preview" or similar.
  4. Verify substitution shows "Review Python code: x = 1".
  5. Insert template into chat input.
  6. Verify substituted text appears in input.
- Expected Result:
  - Template parameter substitution displays correctly before insertion.
- Status: proposed
- Automation Location:
  - File: `src/test/components/TemplateManager.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests template parameter substitution

## 5. Frontend Tests - Main Screen Functional (REQ-210 to REQ-218)

### TC-ID: TC-FUNC-210
- Type: functional
- Related Requirements:
  - REQ-210
- Related Modules:
  - MOD-FE-Core, SCR-MAIN
- Pre-Conditions:
  - Main Chat Screen loaded.
  - Multiple projects exist.
  - Sessions exist under projects.
- Test Steps:
  1. Render ChatPage.
  2. Click on Project A in project tree.
  3. Verify Project A is highlighted.
  4. Verify session list refreshes to show Project A's sessions.
  5. Click on Project B.
  6. Verify session list updates.
- Expected Result:
  - Clicking project loads and displays its sessions.
- Status: proposed
- Automation Location:
  - File: `src/test/pages/ChatPage.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests project selection and session loading

### TC-ID: TC-FUNC-211
- Type: functional
- Related Requirements:
  - REQ-211
- Related Modules:
  - MOD-FE-Core, SCR-MAIN
- Pre-Conditions:
  - Project with files exists.
- Test Steps:
  1. Select a project.
  2. Verify project workspace loads.
  3. Verify project metadata displays (name, description, etc.).
  4. Verify files in project are accessible (if file list shown).
- Expected Result:
  - Project workspace loads with all associated data.
- Status: proposed
- Automation Location:
  - File: `src/test/pages/ChatPage.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests project workspace loading

### TC-ID: TC-FUNC-212
- Type: functional
- Related Requirements:
  - REQ-212
- Related Modules:
  - MOD-FE-Core, useProjectStore
- Pre-Conditions:
  - Browser localStorage available.
- Test Steps:
  1. Select Project A.
  2. Reload page.
  3. Verify Project A is still selected (persisted).
  4. Select Project B.
  5. Close and reopen app.
  6. Verify Project B is selected.
- Expected Result:
  - Last accessed project persists on reload.
- Status: proposed
- Automation Location:
  - File: `src/test/stores/projectStore.test.ts`
  - Framework: Vitest
- Notes: Tests project persistence in localStorage

### TC-ID: TC-FUNC-213
- Type: functional
- Related Requirements:
  - REQ-213
- Related Modules:
  - MOD-FE-Core, SCR-MAIN
- Pre-Conditions:
  - Project selected.
  - Multiple sessions exist.
- Test Steps:
  1. Click Session A.
  2. Verify messages for Session A load.
  3. Verify chat area populates with Session A's history.
  4. Click Session B.
  5. Verify chat area updates to Session B's messages.
- Expected Result:
  - Session selection loads and displays correct messages.
- Status: proposed
- Automation Location:
  - File: `src/test/pages/ChatPage.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests session selection and message loading

### TC-ID: TC-FUNC-216
- Type: functional
- Related Requirements:
  - REQ-216
- Related Modules:
  - MOD-FE-Core, useChatStore
- Pre-Conditions:
  - Session A with unsaved message in input.
  - Session B exists.
- Test Steps:
  1. Type message in Session A's input but don't send.
  2. Click Session B.
  3. Verify modal appears asking to save/discard.
  4. Click Save.
  5. Verify Session A's input is saved.
  6. Switch to Session B (which has different content).
- Expected Result:
  - Session auto-saves before switching.
- Status: proposed
- Automation Location:
  - File: `src/test/pages/ChatPage.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests session auto-save on switch

### TC-ID: TC-FUNC-217
- Type: functional
- Related Requirements:
  - REQ-217
- Related Modules:
  - MOD-FE-Core, COM-SIDEBAR
- Pre-Conditions:
  - Project selected.
- Test Steps:
  1. Look at sidebar.
  2. Verify session list displays under current project.
  3. Verify sessions show name and other metadata.
  4. Verify sessions are formatted consistently.
- Expected Result:
  - Session list displays under current project in sidebar.
- Status: proposed
- Automation Location:
  - File: `src/test/components/Sidebar.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests session list display

### TC-ID: TC-FUNC-218
- Type: functional
- Related Requirements:
  - REQ-218
- Related Modules:
  - MOD-FE-Core, useChatStore
- Pre-Conditions:
  - Browser localStorage available.
- Test Steps:
  1. Select Session A.
  2. Reload page.
  3. Verify Session A is still selected.
  4. Select Session B.
  5. Close and reopen app.
  6. Verify Session B is selected.
- Expected Result:
  - Last accessed session persists on reload.
- Status: proposed
- Automation Location:
  - File: `src/test/stores/chatStore.test.ts`
  - Framework: Vitest
- Notes: Tests session persistence in localStorage

## 6. Frontend Tests - Header & Navigation (REQ-301 to REQ-309)

### TC-ID: TC-FUNC-301
- Type: functional
- Related Requirements:
  - REQ-301
- Related Modules:
  - MOD-FE-Core, COM-HEADER
- Pre-Conditions:
  - ChatPage rendered.
- Test Steps:
  1. Measure header element height.
  2. Verify height is approximately 80px.
  3. Verify header is fixed at top.
  4. Verify content area is below header.
- Expected Result:
  - Header renders at ~80px height and is fixed.
- Status: proposed
- Automation Location:
  - File: `src/test/components/Header.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests header height and positioning

### TC-ID: TC-FUNC-302
- Type: functional
- Related Requirements:
  - REQ-302
- Related Modules:
  - MOD-FE-Core, COM-STATUSBAR
- Pre-Conditions:
  - ChatPage with project and session selected.
- Test Steps:
  1. Render ChatPage.
  2. Look at status bar below header.
  3. Verify project path displays (e.g., "Projects > My Project").
  4. Verify session name displays (e.g., "Session: Chat 1").
  5. Change project/session and verify status updates.
- Expected Result:
  - Status bar displays project path and session name.
- Status: proposed
- Automation Location:
  - File: `src/test/components/StatusBar.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests status bar information display

### TC-ID: TC-FUNC-303
- Type: functional
- Related Requirements:
  - REQ-303
- Related Modules:
  - MOD-FE-Core, COM-SIDEBAR
- Pre-Conditions:
  - ChatPage rendered.
  - Sidebar visible.
- Test Steps:
  1. Measure sidebar width (should be ~280px).
  2. Click toggle/collapse button.
  3. Verify sidebar collapses (width → 0 or hidden).
  4. Verify content area expands to fill space.
  5. Click toggle again.
  6. Verify sidebar expands back to ~280px.
- Expected Result:
  - Sidebar can be resized/toggled.
- Status: proposed
- Automation Location:
  - File: `src/test/components/Sidebar.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests sidebar resizing

### TC-ID: TC-FUNC-305
- Type: functional
- Related Requirements:
  - REQ-305
- Related Modules:
  - MOD-FE-Core, COM-HEADER
- Pre-Conditions:
  - ChatPage rendered.
- Test Steps:
  1. Look at header.
  2. Find application title text "AI Chat Assistant".
  3. Verify title is visible and readable.
  4. Verify title is in a prominent location.
- Expected Result:
  - Application title displays prominently in header.
- Status: proposed
- Automation Location:
  - File: `src/test/components/Header.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests app title visibility

### TC-ID: TC-FUNC-306
- Type: functional
- Related Requirements:
  - REQ-306
- Related Modules:
  - MOD-FE-Core, COM-SEARCH-BAR
- Pre-Conditions:
  - ChatPage rendered.
  - Messages exist with searchable content.
- Test Steps:
  1. Click search bar in header.
  2. Type search query (e.g., "python").
  3. Verify dropdown appears with results.
  4. Verify results are filtered correctly.
  5. Click a result.
  6. Verify result is navigated to (message highlighted).
- Expected Result:
  - Search bar opens and shows filtered results.
- Status: proposed
- Automation Location:
  - File: `src/test/components/SearchBar.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests search functionality

### TC-ID: TC-FUNC-307
- Type: functional
- Related Requirements:
  - REQ-307
- Related Modules:
  - MOD-FE-Core, COM-PROVIDER-SEL
- Pre-Conditions:
  - ChatPage rendered.
  - Multiple providers configured.
- Test Steps:
  1. Look at header for provider selector.
  2. Verify current provider is displayed (e.g., "OpenAI").
  3. Click dropdown.
  4. Verify list of available providers shows.
  5. Click another provider.
  6. Verify selection changes and persists.
- Expected Result:
  - Provider selector displays current and allows switching.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ProviderSelector.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests provider selector display and switching

### TC-ID: TC-FUNC-308
- Type: functional
- Related Requirements:
  - REQ-308
- Related Modules:
  - MOD-FE-Core, COM-HEADER
- Pre-Conditions:
  - ChatPage rendered.
- Test Steps:
  1. Look in header for Settings button (gear icon).
  2. Click Settings button.
  3. Verify navigation to SettingsPage or modal opens.
  4. Verify settings UI is visible.
- Expected Result:
  - Settings button navigates to settings.
- Status: proposed
- Automation Location:
  - File: `src/test/components/Header.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests settings button navigation

### TC-ID: TC-FUNC-309
- Type: functional
- Related Requirements:
  - REQ-309
- Related Modules:
  - MOD-FE-Core, COM-USERMENU
- Pre-Conditions:
  - ChatPage rendered.
- Test Steps:
  1. Click user profile icon in header.
  2. Verify dropdown menu appears.
  3. Verify menu has options (logout, etc.).
  4. Click logout.
  5. Verify logout action triggers.
- Expected Result:
  - User menu dropdown shows and logout works.
- Status: proposed
- Automation Location:
  - File: `src/test/components/UserMenu.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests user menu and logout

## 7. Frontend Tests - Project & Session Navigation (REQ-310 to REQ-314)

### TC-ID: TC-FUNC-310
- Type: functional
- Related Requirements:
  - REQ-310
- Related Modules:
  - MOD-FE-Core, COM-PROJECTTREE
- Pre-Conditions:
  - ChatPage rendered.
  - Nested projects exist.
- Test Steps:
  1. Look at project tree in sidebar.
  2. Verify parent projects display.
  3. Click expand icon on parent project.
  4. Verify child projects appear indented.
  5. Click collapse icon.
  6. Verify children hide.
- Expected Result:
  - Project tree expands and collapses correctly.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ProjectTree.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests project tree expand/collapse

### TC-ID: TC-FUNC-311
- Type: functional
- Related Requirements:
  - REQ-311
- Related Modules:
  - MOD-FE-Core, COM-SIDEBAR
- Pre-Conditions:
  - Project selected.
  - Sessions exist under project.
- Test Steps:
  1. Select a project in tree.
  2. Verify session list appears below project in sidebar.
  3. Verify each session shows name and metadata.
  4. Verify session count is correct.
- Expected Result:
  - Sessions display under expanded project.
- Status: proposed
- Automation Location:
  - File: `src/test/components/Sidebar.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests session list display under project

### TC-ID: TC-FUNC-313
- Type: functional
- Related Requirements:
  - REQ-313
- Related Modules:
  - MOD-FE-Core, COM-SIDEBAR
- Pre-Conditions:
  - ChatPage rendered.
- Test Steps:
  1. Click "New Project" button in sidebar.
  2. Verify project creation modal opens.
  3. Verify form fields are present (name, description, parent).
  4. Fill form and submit.
  5. Verify new project appears in tree.
- Expected Result:
  - New Project button opens modal and creates project.
- Status: proposed
- Automation Location:
  - File: `src/test/components/Sidebar.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests new project modal and creation

### TC-ID: TC-FUNC-314
- Type: functional
- Related Requirements:
  - REQ-314
- Related Modules:
  - MOD-FE-Core, COM-SIDEBAR
- Pre-Conditions:
  - Project selected.
- Test Steps:
  1. Verify "New Session" button is enabled (project selected).
  2. Click "New Session" button.
  3. Verify session creation modal opens.
  4. Verify form fields appear (name, etc.).
  5. Fill form and submit.
  6. Verify new session appears in list.
- Expected Result:
  - New Session button opens modal and creates session.
- Status: proposed
- Automation Location:
  - File: `src/test/components/Sidebar.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests new session modal and creation

## 8. Frontend Tests - Chat Display (REQ-315 to REQ-322)

### TC-ID: TC-FUNC-315
- Type: functional
- Related Requirements:
  - REQ-315
- Related Modules:
  - MOD-FE-Core, COM-CHATAREA
- Pre-Conditions:
  - ChatPage with message history rendered.
- Test Steps:
  1. Look at chat area.
  2. Verify messages display in bubble format.
  3. Verify each bubble contains message content.
  4. Verify bubbles have distinct styling per role.
- Expected Result:
  - Messages display in bubble format.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ChatArea.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests message bubble display

### TC-ID: TC-FUNC-316
- Type: functional
- Related Requirements:
  - REQ-316
- Related Modules:
  - MOD-FE-Core, COM-CHATAREA
- Pre-Conditions:
  - ChatPage with mixed role messages.
- Test Steps:
  1. Look at chat area.
  2. Verify user messages (role='user') align to right.
  3. Verify AI messages (role='assistant') align to left.
  4. Verify alignment is consistent throughout.
- Expected Result:
  - Message alignment follows role (user right, AI left).
- Status: proposed
- Automation Location:
  - File: `src/test/components/ChatArea.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests message alignment

### TC-ID: TC-FUNC-317
- Type: functional
- Related Requirements:
  - REQ-317
- Related Modules:
  - MOD-FE-Core, COM-CHATMESSAGE
- Pre-Conditions:
  - ChatPage with messages.
- Test Steps:
  1. Look at messages in chat area.
  2. Verify each message displays a timestamp.
  3. Verify timestamp format is readable (e.g., HH:MM).
  4. Verify timestamp is accurate.
- Expected Result:
  - Timestamps display correctly on messages.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ChatMessage.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests message timestamp display

### TC-ID: TC-FUNC-318
- Type: functional
- Related Requirements:
  - REQ-318
- Related Modules:
  - MOD-FE-Core, COM-CHATMESSAGE
- Pre-Conditions:
  - ChatPage with AI messages from different providers.
- Test Steps:
  1. Look at an AI message.
  2. Verify provider name displays (e.g., "OpenAI", "Anthropic").
  3. Switch to message from different provider.
  4. Verify provider name is correct.
- Expected Result:
  - Provider name displays under AI messages.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ChatMessage.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests provider name display on messages

### TC-ID: TC-FUNC-319
- Type: functional
- Related Requirements:
  - REQ-319
- Related Modules:
  - MOD-FE-Core, COM-CHATAREA
- Pre-Conditions:
  - ChatPage with scrolled-up message history.
- Test Steps:
  1. Send a new message.
  2. Verify chat area auto-scrolls to bottom.
  3. Verify new message is visible.
  4. Send another message.
  5. Verify scroll follows to latest message.
- Expected Result:
  - Chat auto-scrolls to latest message.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ChatArea.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests auto-scroll to latest message

### TC-ID: TC-FUNC-320
- Type: functional
- Related Requirements:
  - REQ-320
- Related Modules:
  - MOD-FE-Core, COM-CHATAREA
- Pre-Conditions:
  - ChatPage with large message history.
- Test Steps:
  1. Scroll up to middle of message history.
  2. Load more messages (pagination).
  3. Verify scroll position is maintained.
  4. Verify user doesn't unexpectedly scroll to bottom.
- Expected Result:
  - Scroll position is preserved when loading history.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ChatArea.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests scroll position preservation

### TC-ID: TC-FUNC-321
- Type: functional
- Related Requirements:
  - REQ-321
- Related Modules:
  - MOD-FE-Core, COM-CHATMESSAGE
- Pre-Conditions:
  - ChatPage with messages.
  - Clipboard API available.
- Test Steps:
  1. Hover over or find copy button on message.
  2. Click copy button.
  3. Verify message content is copied to clipboard.
  4. Paste elsewhere to verify content.
- Expected Result:
  - Copy button copies message to clipboard.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ChatMessage.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests copy message functionality

### TC-ID: TC-FUNC-322
- Type: functional
- Related Requirements:
  - REQ-322
- Related Modules:
  - MOD-FE-Core, COM-CHATAREA
- Pre-Conditions:
  - ChatPage rendered.
  - AI API mocked or real.
- Test Steps:
  1. Type and send a message.
  2. Verify loading spinner appears in chat.
  3. Verify spinner is visible during API wait.
  4. AI response arrives.
  5. Verify spinner disappears.
- Expected Result:
  - Loading indicator shows during AI response.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ChatArea.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests loading spinner display

## 9. Frontend Tests - Chat Input (REQ-323 to REQ-325)

### TC-ID: TC-FUNC-323
- Type: functional
- Related Requirements:
  - REQ-323
- Related Modules:
  - MOD-FE-Core, COM-CHATINPUT
- Pre-Conditions:
  - ChatPage rendered.
- Test Steps:
  1. Click in message input textarea.
  2. Type single-line message "Hello".
  3. Verify message appears on one line.
  4. Press Enter (without Shift) to send OR type multi-line.
  5. Hold Shift+Enter to create new line.
  6. Verify multi-line message is supported.
  7. Verify Enter sends (Shift+Enter creates line break).
- Expected Result:
  - Enter sends message; Shift+Enter creates new line.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ChatInput.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests input keyboard shortcuts

### TC-ID: TC-FUNC-324
- Type: functional
- Related Requirements:
  - REQ-324
- Related Modules:
  - MOD-FE-Core, COM-CHATINPUT
- Pre-Conditions:
  - ChatPage rendered.
- Test Steps:
  1. Look at Send button.
  2. Verify button is disabled when input is empty.
  3. Type text in input.
  4. Verify Send button is enabled.
  5. Clear input.
  6. Verify button is disabled again.
  7. Send message and verify disables during loading.
- Expected Result:
  - Send button state reflects input and loading state.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ChatInput.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests send button enable/disable logic

### TC-ID: TC-FUNC-325
- Type: functional
- Related Requirements:
  - REQ-325
- Related Modules:
  - MOD-FE-Core, COM-CHATINPUT
- Pre-Conditions:
  - ChatPage rendered.
  - Max character limit is 10000.
- Test Steps:
  1. Look at character counter near input.
  2. Verify counter shows "0 / 10000".
  3. Type 500 characters.
  4. Verify counter shows "500 / 10000".
  5. Type to near limit (9800 chars).
  6. Verify counter displays warning color.
  7. Verify input blocks at 10000 chars.
- Expected Result:
  - Character counter displays and enforces limit.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ChatInput.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests character counter and limit enforcement

## 10. Frontend Tests - Template Features (REQ-414 to REQ-418)

### TC-ID: TC-FUNC-414
- Type: functional
- Related Requirements:
  - REQ-414
- Related Modules:
  - MOD-FE-Core, COM-CHATINPUT, COM-TEMPLATE-MGR
- Pre-Conditions:
  - ChatPage rendered.
  - Templates exist.
- Test Steps:
  1. Look in chat input for template dropdown/button.
  2. Click template button/dropdown.
  3. Verify dropdown shows list of templates.
  4. Click a template.
  5. Verify template text is inserted into input.
- Expected Result:
  - Templates can be inserted into chat input.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ChatInput.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests template insertion into input

### TC-ID: TC-FUNC-415
- Type: functional
- Related Requirements:
  - REQ-415
- Related Modules:
  - MOD-FE-Core, COM-CHATINPUT
- Pre-Conditions:
  - ChatPage rendered.
- Test Steps:
  1. Click template button in chat input.
  2. Verify dropdown appears.
  3. Verify all templates are listed.
  4. Verify templates show category/title.
- Expected Result:
  - Template dropdown displays all templates.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ChatInput.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests template dropdown display

### TC-ID: TC-FUNC-416
- Type: functional
- Related Requirements:
  - REQ-416
- Related Modules:
  - MOD-FE-Core, COM-TEMPLATE-MGR
- Pre-Conditions:
  - TemplateManager opened.
  - Template selected.
- Test Steps:
  1. Click template.
  2. Verify preview modal/panel opens.
  3. Verify modal shows template content.
  4. Verify modal shows parameters and placeholders.
  5. Close modal.
- Expected Result:
  - Template preview modal displays correctly.
- Status: proposed
- Automation Location:
  - File: `src/test/components/TemplateManager.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests template preview modal

### TC-ID: TC-FUNC-417
- Type: functional
- Related Requirements:
  - REQ-417
- Related Modules:
  - MOD-FE-Core, COM-TEMPLATE-MGR
- Pre-Conditions:
  - TemplateManager opened.
- Test Steps:
  1. Edit a template (change content).
  2. Verify save button works.
  3. Delete a template.
  4. Verify confirmation dialog appears.
  5. Confirm deletion.
  6. Verify template is removed from list.
- Expected Result:
  - Templates can be edited and deleted.
- Status: proposed
- Automation Location:
  - File: `src/test/components/TemplateManager.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests template edit and delete operations

## 11. Frontend Tests - Settings & Configuration (REQ-706 to REQ-710)

### TC-ID: TC-FUNC-706
- Type: functional
- Related Requirements:
  - REQ-706
- Related Modules:
  - MOD-FE-Core, SCR-SETTINGS
- Pre-Conditions:
  - SettingsPage opened.
  - API endpoint mocked.
- Test Steps:
  1. Enter API key in settings form.
  2. Click "Test API Key" button.
  3. Verify API call is made to test endpoint.
  4. Verify result displays (✓ valid or ✗ invalid).
  5. Verify error message shows if invalid.
- Expected Result:
  - API key test button makes call and shows result.
- Status: proposed
- Automation Location:
  - File: `src/test/pages/SettingsPage.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests API key test functionality

### TC-ID: TC-FUNC-707
- Type: functional
- Related Requirements:
  - REQ-707
- Related Modules:
  - MOD-FE-Core, SCR-SETTINGS
- Pre-Conditions:
  - SettingsPage opened.
  - Changes made to settings.
- Test Steps:
  1. Update API key or settings.
  2. Click Save button.
  3. Verify save request is sent.
  4. Verify success toast/notification appears.
  5. Verify notification confirms settings saved.
- Expected Result:
  - Settings save shows success feedback.
- Status: proposed
- Automation Location:
  - File: `src/test/pages/SettingsPage.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests settings save success notification

### TC-ID: TC-FUNC-710
- Type: functional
- Related Requirements:
  - REQ-710
- Related Modules:
  - MOD-FE-Core, SCR-SETTINGS, useSettingsStore
- Pre-Conditions:
  - SettingsPage rendered.
  - Browser developer tools available.
- Test Steps:
  1. Enter API key in settings.
  2. Inspect localStorage.
  3. Verify API key is NOT stored in localStorage (on frontend).
  4. Verify API key is NOT logged to console.
  5. Verify API key is sent to backend only via HTTPS.
- Expected Result:
  - API keys are not stored in frontend localStorage.
- Status: proposed
- Automation Location:
  - File: `src/test/pages/SettingsPage.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests secure API key handling

## 12. Frontend Tests - Component Tests (Message Templates)

### TC-ID: TC-COMP-TMPL-001
- Type: unit
- Related Requirements:
  - REQ-414
- Related Modules:
  - MOD-FE-Core, COM-TEMPLATE-MGR
- Pre-Conditions:
  - TemplateManager component rendered.
  - Mock template data provided.
- Test Steps:
  1. Render TemplateManager.
  2. Verify list of templates displays.
  3. Verify each template shows in correct format.
- Expected Result:
  - Template list renders correctly.
- Status: proposed
- Automation Location:
  - File: `src/test/components/TemplateManager.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests template manager rendering

### TC-ID: TC-COMP-TMPL-002
- Type: unit
- Related Requirements:
  - REQ-414
- Related Modules:
  - MOD-FE-Core, COM-TEMPLATE-MGR
- Pre-Conditions:
  - Create template form rendered.
- Test Steps:
  1. Render form for creating new template.
  2. Leave fields empty.
  3. Click Create button.
  4. Verify validation error appears.
  5. Fill fields correctly.
  6. Verify Create button works.
- Expected Result:
  - Form validation works correctly.
- Status: proposed
- Automation Location:
  - File: `src/test/components/TemplateManager.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests template form validation

### TC-ID: TC-COMP-TMPL-003
- Type: unit
- Related Requirements:
  - REQ-417
- Related Modules:
  - MOD-FE-Core, COM-TEMPLATE-MGR
- Pre-Conditions:
  - Edit template form rendered.
  - Template data loaded.
- Test Steps:
  1. Render edit form with template data.
  2. Verify fields are pre-filled.
  3. Change a field (e.g., title).
  4. Click Update/Save.
  5. Verify change is saved.
- Expected Result:
  - Template edit form works and persists changes.
- Status: proposed
- Automation Location:
  - File: `src/test/components/TemplateManager.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests template editing

### TC-ID: TC-COMP-TMPL-004
- Type: unit
- Related Requirements:
  - REQ-417
- Related Modules:
  - MOD-FE-Core, COM-TEMPLATE-MGR
- Pre-Conditions:
  - TemplateManager with delete functionality.
- Test Steps:
  1. Click delete button on template.
  2. Verify confirmation dialog appears.
  3. Click Cancel - template should remain.
  4. Click delete again.
  5. Click Confirm.
  6. Verify template is removed.
- Expected Result:
  - Delete with confirmation works correctly.
- Status: proposed
- Automation Location:
  - File: `src/test/components/TemplateManager.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests template deletion with confirmation

### TC-ID: TC-COMP-TMPL-005
- Type: unit
- Related Requirements:
  - REQ-416
- Related Modules:
  - MOD-FE-Core, COM-TEMPLATE-MGR
- Pre-Conditions:
  - Template with content rendered.
- Test Steps:
  1. Click Preview button/icon.
  2. Verify preview modal opens.
  3. Verify template content displays.
  4. Verify modal shows full content (not truncated).
  5. Close modal.
- Expected Result:
  - Preview modal displays template content correctly.
- Status: proposed
- Automation Location:
  - File: `src/test/components/TemplateManager.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests template preview display

### TC-ID: TC-COMP-TMPL-006
- Type: unit
- Related Requirements:
  - REQ-418
- Related Modules:
  - MOD-FE-Core, COM-TEMPLATE-MGR
- Pre-Conditions:
  - Template with parameters {{lang}} and {{code}}.
- Test Steps:
  1. Open template for insertion.
  2. Fill parameter inputs: lang="Python", code="def foo(): pass".
  3. Verify preview shows substituted text: "Python code: def foo(): pass".
  4. Insert into input.
  5. Verify substitution is applied.
- Expected Result:
  - Parameter substitution works before insertion.
- Status: proposed
- Automation Location:
  - File: `src/test/components/TemplateManager.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests parameter substitution

### TC-ID: TC-COMP-TMPL-007
- Type: unit
- Related Requirements:
  - REQ-414
- Related Modules:
  - MOD-FE-Core, COM-TEMPLATE-MGR
- Pre-Conditions:
  - Templates with different categories exist.
- Test Steps:
  1. Render TemplateManager.
  2. Verify category filter/tabs display.
  3. Click category filter (e.g., "Code Review").
  4. Verify list filters to show only that category.
  5. Click "All" to reset.
- Expected Result:
  - Category filtering works correctly.
- Status: proposed
- Automation Location:
  - File: `src/test/components/TemplateManager.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests template category filtering

### TC-ID: TC-COMP-TMPL-008
- Type: unit
- Related Requirements:
  - REQ-418
- Related Modules:
  - MOD-FE-Core, COM-CHATINPUT
- Pre-Conditions:
  - ChatInput rendered.
  - Template selected and parameters filled.
- Test Steps:
  1. Click "Insert Template" button.
  2. Verify template text (with substitutions) appears in input.
  3. Verify cursor is positioned after template.
  4. Verify user can continue typing.
- Expected Result:
  - Template inserts correctly into chat input.
- Status: proposed
- Automation Location:
  - File: `src/test/components/ChatInput.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests template insertion into input

## 13. Frontend Tests - Integration Tests

### TC-ID: TC-INTG-001
- Type: integration
- Related Requirements:
  - REQ-323, REQ-324, REQ-401, REQ-514
- Related Modules:
  - MOD-FE-Core, MOD-BE-Conversations
- Pre-Conditions:
  - ChatPage fully rendered.
  - Backend API available (real or mocked).
- Test Steps:
  1. Type message in input.
  2. Click Send button.
  3. Verify message appears in chat immediately.
  4. Verify loading spinner shows.
  5. Mock AI response returns.
  6. Verify AI response displays.
  7. Verify both messages persist in state.
- Expected Result:
  - Complete message send flow works end-to-end.
- Status: proposed
- Automation Location:
  - File: `src/test/integration/messageFlow.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests complete message send workflow

### TC-ID: TC-INTG-002
- Type: integration
- Related Requirements:
  - REQ-307, REQ-512, REQ-514
- Related Modules:
  - MOD-FE-Core, MOD-BE-Providers
- Pre-Conditions:
  - ChatPage rendered.
  - Multiple providers configured.
- Test Steps:
  1. Send message with provider="openai".
  2. Verify response shows openai provider.
  3. Switch to provider="anthropic" in selector.
  4. Send another message.
  5. Verify response shows anthropic provider.
  6. Verify both messages persisted with correct provider.
- Expected Result:
  - Provider switching mid-conversation works.
- Status: proposed
- Automation Location:
  - File: `src/test/integration/providerSwitching.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests provider switching during conversation

### TC-ID: TC-INTG-003
- Type: integration
- Related Requirements:
  - REQ-210, REQ-212, REQ-213, REQ-218
- Related Modules:
  - MOD-FE-Core, useProjectStore, useChatStore
- Pre-Conditions:
  - Multiple projects and sessions exist.
- Test Steps:
  1. Add message to Session A.
  2. Navigate to Project B and Session C.
  3. Add message to Session C.
  4. Reload page.
  5. Verify Project B and Session C are still selected.
  6. Verify Session C shows correct message history.
  7. Switch back to Project A, Session A.
  8. Verify Session A shows correct messages.
- Expected Result:
  - Project/session navigation with persistence works.
- Status: proposed
- Automation Location:
  - File: `src/test/integration/projectSessionNavigation.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests project/session navigation with state persistence

### TC-ID: TC-INTG-004
- Type: integration
- Related Requirements:
  - REQ-414, REQ-418, REQ-323, REQ-324, REQ-401
- Related Modules:
  - MOD-FE-Core, COM-CHATINPUT, COM-TEMPLATE-MGR
- Pre-Conditions:
  - ChatPage rendered.
  - Template with parameters exists.
- Test Steps:
  1. Click template dropdown in input.
  2. Select template "Code Review".
  3. Fill parameter fields.
  4. Click Preview.
  5. Verify substituted text in preview.
  6. Click Insert.
  7. Verify substituted text appears in input.
  8. Click Send.
  9. Verify message is sent with substituted content.
  10. Verify message is saved correctly.
- Expected Result:
  - Template creation and insertion workflow works end-to-end.
- Status: proposed
- Automation Location:
  - File: `src/test/integration/templateUsage.test.tsx`
  - Framework: Vitest + React Testing Library
- Notes: Tests template usage end-to-end

## 14. Frontend Test Implementation Status Summary

| Test Category | Count | Status | Notes |
|---|---|---|---|
| Unit Tests (Layout & Components) | 14 | proposed | REQ-301-305, REQ-307-318, REQ-321-325 |
| Functional Tests (Navigation) | 18 | proposed | REQ-210-214, REQ-301-309, REQ-310-314 |
| Functional Tests (Chat Display) | 8 | proposed | REQ-315-322 |
| Functional Tests (Chat Input) | 3 | proposed | REQ-323-325 |
| Functional Tests (Templates) | 4 | proposed | REQ-414-418 |
| Functional Tests (Settings) | 3 | proposed | REQ-706-710 |
| Component Tests (Templates) | 8 | proposed | REQ-414, REQ-416-418 |
| Integration Tests | 4 | proposed | Complete workflows |
| **Total** | **62** | **proposed** | Full frontend coverage |
