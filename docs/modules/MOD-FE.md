# DOCUMENT_TYPE: MODULE_SPEC
# MODULE_ID: MOD-FE-Core
# MODULE_TYPE: frontend
# VERSION: 1.0

## 1. Meta

- Name: AI Chat Assistant - Frontend Core Module Specification
- Owner: Development Team
- Status: implemented <proposed | in_progress | implemented | tested | accepted>
- Tech Stack:
  - Framework: React 18.2+
  - Language: TypeScript 5.0+
  - State Management: Zustand 4.0+
  - Styling: Tailwind CSS 3.0+
  - UI Components: Lucide React (icons)
  - HTTP Client: Axios
  - Testing: Vitest + React Testing Library

## 2. Linked Requirements

### Main Screen & Layout
- REQ-301: Header bar at top
- REQ-302: Status bar below header
- REQ-303: Resizable left sidebar
- REQ-304: Main chat content area
- REQ-305: Application title and logo
- REQ-306: Search bar with dropdown results
- REQ-307: AI provider selector dropdown
- REQ-308: Settings button in header
- REQ-309: User profile menu dropdown
- REQ-310: Project tree view in sidebar
- REQ-311: Session list under current project
- REQ-312: Context menu on right-click (proposed)
- REQ-313: New Project button
- REQ-314: New Session button

### Chat Display & Input
- REQ-315: Message display in chat bubbles
- REQ-316: User/AI message alignment
- REQ-317: Message timestamps
- REQ-318: Provider name display for AI messages
- REQ-319: Auto-scroll to latest message
- REQ-320: Preserve scroll position in history
- REQ-321: Copy message to clipboard
- REQ-322: Loading indicator for AI response
- REQ-323: Multi-line text input
- REQ-324: Send button
- REQ-325: Character counter

### Chat Features
- REQ-414 through REQ-418: Message templates

### Settings & Preferences
- REQ-701 through REQ-710: Settings page and API key management

### State & Persistence
- REQ-212: Last accessed project persistence
- REQ-218: Last accessed session persistence
- REQ-512: Selected provider persistence

## 3. Screens / Components

### 3.1 Screen/Component List

| UI_ID            | Name                    | Type        | Description                                          | Status       | Requirements |
|------------------|------------------------|-------------|------------------------------------------------------|-------------|--------------|
| SCR-MAIN         | Main Chat Screen        | screen      | Primary interface with sidebar, header, chat area    | implemented | REQ-301-304 |
| SCR-SETTINGS     | Settings Page           | screen      | Configuration page for API keys and preferences      | implemented | REQ-701-710 |
| SCR-SEARCH       | Search Results Page     | screen      | Search interface and results display (optional)      | implemented | REQ-306 |
| COM-HEADER       | Header Component        | component   | Top bar with title, search, provider selector        | implemented | REQ-301, REQ-305-309 |
| COM-SIDEBAR      | Sidebar Navigation      | component   | Left sidebar with project tree and sessions          | implemented | REQ-303, REQ-310-314 |
| COM-STATUSBAR    | Status Bar              | component   | Fixed status area below header                       | implemented | REQ-302 |
| COM-CHATAREA     | Chat Area               | component   | Message display with auto-scroll                     | implemented | REQ-304, REQ-315-322 |
| COM-CHATINPUT    | Chat Input              | component   | Text input with send button and templates            | implemented | REQ-323-325 |
| COM-CHATMESSAGE  | Chat Message            | component   | Individual message bubble with metadata              | implemented | REQ-315-318 |
| COM-PROVIDER-SEL | Provider Selector       | component   | Dropdown for provider selection with status          | implemented | REQ-307 |
| COM-SEARCH-BAR   | Search Bar              | component   | Input and dropdown for search results                | implemented | REQ-306 |
| COM-PROJECTTREE  | Project Tree            | component   | Hierarchical project navigation                      | implemented | REQ-310 |
| COM-TEMPLATE-MGR | Template Manager        | component   | Modal for template CRUD operations                   | implemented | REQ-414-418 |
| COM-USERMENU     | User Menu               | component   | User profile dropdown (minimal in single-user mode)  | implemented | REQ-309 |

### 3.2 Screen: SCR-MAIN (Main Chat Screen)

- **UI_ID:** SCR-MAIN
- **Component File:** frontend/src/pages/ChatPage.tsx (+ MainLayout.tsx wrapper)
- **Related REQ:** REQ-301 through REQ-304, REQ-310 through REQ-314
- **Status:** implemented

#### Layout

- **Sections:**
  - **Header:** Fixed height ~80px, contains app title, search, provider selector, settings, user menu
  - **Status Bar:** Fixed height ~40px, shows project path and session info
  - **Sidebar (left):** ~280px default width, resizable, contains project tree + session list
  - **Main Content:** Flex-fill, contains message display area + input area
  - **Footer:** Message input area with send button

#### Elements

| Element_ID       | Type       | Label/Purpose                        | Validation Rules | Handler |
|------------------|-----------|--------------------------------------|------------------|---------|
| app-title        | header    | "AI Chat Assistant" title            | static           | N/A |
| search-input     | search    | Search messages/files                | min 1 char       | onChange → SearchPage |
| provider-select  | dropdown  | Current provider display + selector  | only configured  | onChange → updateProvider |
| settings-btn     | button    | Navigate to settings                 | always enabled   | onClick → /settings |
| user-menu        | menu      | User profile dropdown                | single-user      | onClick → logout |
| project-tree     | nav       | Hierarchical project navigation      | dynamic load     | onClick → selectProject |
| new-proj-btn     | button    | Create new project                   | always enabled   | onClick → openProjectModal |
| session-list     | nav       | Sessions under current project       | project required | onClick → selectSession |
| new-sess-btn     | button    | Create new session                   | project required | onClick → openSessionModal |
| message-area     | container | Scrollable message display           | auto-scroll      | onScroll → updatePosition |
| chat-input       | textarea  | Multi-line message input             | max 10k chars    | onChange → updateInput |
| send-btn         | button    | Send message to AI                   | disabled if empty/loading | onClick → sendMessage |

#### Interaction & State

- **Initial State:**
  - Load last accessed project (from localStorage)
  - Load last accessed session (from localStorage)
  - Load message history for session
  - Display available providers
  - Display project tree

- **On Project Select:**
  - Update UI to show selected project
  - Load sessions in project
  - Save project ID to localStorage

- **On Session Select:**
  - Load messages for session
  - Clear input field
  - Auto-scroll to bottom
  - Save session ID to localStorage

- **On Message Send:**
  - Add user message to chat display
  - Show loading spinner
  - Send to /api/conversations/send
  - Display AI response
  - Auto-scroll to bottom
  - Save to session history

- **On Provider Change:**
  - Update currently selected provider
  - Validate provider has API key
  - Save to localStorage
  - Subsequent messages use new provider

#### Data Flows

- **Sends:**
  - POST /api/chat_sessions (create session)
  - POST /api/projects (create project)
  - POST /api/conversations/send (send message)
  - GET /api/projects (load projects)
  - GET /api/chat_sessions (load sessions)
  - GET /api/ai-providers (load providers)

- **Receives:**
  - Conversation messages with metadata
  - Project/session list with hierarchy
  - Provider info (name, models, status)
  - User state from localStorage

#### Accessibility

- **Keyboard Navigation:**
  - Tab through buttons and inputs
  - Enter to send message (Shift+Enter for new line)
  - Ctrl+Enter as alternative send shortcut
  - Escape to close modals

- **ARIA Attributes:**
  - aria-label on all icon buttons
  - role="main" on main content area
  - role="navigation" on sidebars
  - aria-busy="true" during loading
  - aria-selected="true" on current item

### 3.3 Screen: SCR-SETTINGS (Settings Page)

- **UI_ID:** SCR-SETTINGS
- **Component File:** frontend/src/pages/SettingsPage.tsx
- **Related REQ:** REQ-701 through REQ-710
- **Status:** implemented

#### Layout

- **Sections:**
  - **Header:** Tab navigation (API Keys, Preferences, About)
  - **Content Area:** Tab-specific content
  - **Footer:** Save/Cancel buttons

#### Elements

| Element_ID       | Type       | Label | Validation | Handler |
|------------------|-----------|-------|-----------|---------|
| api-keys-tab     | tab       | "API Keys" | active class | onClick → showApiKeysPanel |
| preferences-tab  | tab       | "Preferences" | active class | onClick → showPreferencesPanel |
| about-tab        | tab       | "About" | active class | onClick → showAboutPanel |
| provider-input   | input     | API Key input per provider | required, min length | onChange → updateKey |
| test-btn         | button    | Test API key | enabled if key entered | onClick → testKey |
| test-status      | span      | Test result (✓/✗) | dynamic | shows after test |
| save-btn         | button    | Save changes | enabled if changed | onClick → saveSettings |
| cancel-btn       | button    | Discard changes | always enabled | onClick → closeSettings |

#### Interaction & State

- **Initial State:**
  - Load current API keys (masked)
  - Load user preferences
  - Display about information

- **On API Key Input:**
  - Validate format
  - Update state (not saved yet)
  - Enable Save button

- **On Test API Key:**
  - Send POST /api/settings/test-api-key
  - Display result (✓ valid / ✗ invalid)
  - Show error message if invalid

- **On Save:**
  - Send PUT /api/settings with updated keys
  - Show success/error toast
  - Update global provider state
  - Close settings if no errors

#### Data Flows

- **Sends:**
  - PUT /api/settings (save API keys)
  - POST /api/settings/test-api-key (test key)

- **Receives:**
  - Current settings from backend
  - Test result (valid/invalid)

#### Accessibility

- **Keyboard Navigation:**
  - Tab between input fields
  - Arrow keys for tab selection
  - Enter to test/save

- **ARIA Attributes:**
  - role="tablist" on tab container
  - role="tabpanel" on tab content
  - aria-selected for current tab
  - aria-label on test button

## 4. Component-Level Implementation Status

| UI_ID            | Implementation Status | Test Coverage Status | Notes |
|------------------|----------------------|----------------------|-------|
| SCR-MAIN         | implemented          | 80% coverage         | Main interface complete |
| SCR-SETTINGS     | implemented          | 70% coverage         | API key management done |
| SCR-SEARCH       | implemented          | 60% coverage         | Basic search implemented |
| COM-HEADER       | implemented          | 85% coverage         | All elements present |
| COM-SIDEBAR      | implemented          | 80% coverage         | Project tree complete |
| COM-STATUSBAR    | implemented          | 50% coverage         | Minimal info displayed |
| COM-CHATAREA     | implemented          | 90% coverage         | Full message display |
| COM-CHATINPUT    | implemented          | 95% coverage         | Comprehensive tests |
| COM-CHATMESSAGE  | implemented          | 90% coverage         | Message styling complete |
| COM-PROVIDER-SEL | implemented          | 85% coverage         | Dropdown fully functional |
| COM-SEARCH-BAR   | implemented          | 70% coverage         | Basic search UX |
| COM-PROJECTTREE  | implemented          | 75% coverage         | Recursive rendering |
| COM-TEMPLATE-MGR | implemented          | 95% coverage         | Full CRUD + tests |
| COM-USERMENU     | implemented          | 60% coverage         | Single-user minimal |

## 5. Frontend Tests (Unit + Functional)

### 5.1 Unit Tests

- **TC-UNIT-301:** Header renders with all elements
- **TC-UNIT-302:** Status bar displays correct info
- **TC-UNIT-303:** Sidebar toggle works
- **TC-UNIT-305:** App title displays correctly
- **TC-UNIT-310:** Project tree renders hierarchically
- **TC-UNIT-313:** New Project button opens modal
- **TC-UNIT-314:** New Session button opens modal
- **TC-UNIT-315:** Messages render in bubble format
- **TC-UNIT-316:** User messages align right, AI left
- **TC-UNIT-317:** Timestamp displays correctly
- **TC-UNIT-318:** Provider name shows for AI messages
- **TC-UNIT-321:** Copy to clipboard works
- **TC-UNIT-322:** Loading spinner displays during send
- **TC-UNIT-323:** Textarea auto-expands
- **TC-UNIT-324:** Send button disabled when empty
- **TC-UNIT-325:** Character counter displays at max

### 5.2 Functional UI Tests

- **TC-FUNC-210:** Clicking project loads it + displays sessions
- **TC-FUNC-211:** Project workspace loads with all files
- **TC-FUNC-212:** Last accessed project persists on reload
- **TC-FUNC-213:** Clicking session loads its messages
- **TC-FUNC-216:** Session auto-saves before switching
- **TC-FUNC-217:** Session list shows under project
- **TC-FUNC-218:** Last accessed session persists on reload
- **TC-FUNC-301:** Header renders at ~80px height
- **TC-FUNC-302:** Status bar displays project path + session name
- **TC-FUNC-303:** Sidebar resizes and collapses
- **TC-FUNC-304:** Chat area scrolls and shows messages
- **TC-FUNC-305:** App title visible in header
- **TC-FUNC-306:** Search dropdown opens and shows results
- **TC-FUNC-307:** Provider selector shows current + list
- **TC-FUNC-308:** Settings button navigates to /settings
- **TC-FUNC-309:** User menu opens and shows logout
- **TC-FUNC-310:** Project tree expands/collapses projects
- **TC-FUNC-311:** Sessions show under expanded project
- **TC-FUNC-313:** New Project modal creates project
- **TC-FUNC-314:** New Session modal creates session
- **TC-FUNC-315:** Messages display as bubbles
- **TC-FUNC-316:** Message alignment correct per role
- **TC-FUNC-317:** Timestamps show in HH:MM format
- **TC-FUNC-318:** Provider name shows under AI messages
- **TC-FUNC-319:** Auto-scroll to bottom on new message
- **TC-FUNC-320:** Scroll position preserved in history
- **TC-FUNC-321:** Copy message button works
- **TC-FUNC-322:** Loading spinner shows during wait
- **TC-FUNC-323:** Enter key sends, Shift+Enter new line
- **TC-FUNC-324:** Send button disables when loading
- **TC-FUNC-325:** Character counter shows near max
- **TC-FUNC-415:** Template dropdown inserts on click
- **TC-FUNC-416:** Template preview modal displays
- **TC-FUNC-706:** API key test shows valid/invalid
- **TC-FUNC-707:** Settings save shows success toast
- **TC-FUNC-710:** API keys not stored in localStorage

### 5.3 Component Tests (Message Templates - Implemented)

- **TC-COMP-TMPL-001:** TemplateManager renders with list
- **TC-COMP-TMPL-002:** Create template form validates input
- **TC-COMP-TMPL-003:** Edit template updates fields
- **TC-COMP-TMPL-004:** Delete template with confirmation
- **TC-COMP-TMPL-005:** Preview modal shows content
- **TC-COMP-TMPL-006:** Parameter substitution works
- **TC-COMP-TMPL-007:** Category filter works
- **TC-COMP-TMPL-008:** Template insertion into input

### 5.4 Integration Tests

- **TC-INTG-001:** Complete message send flow (input → API → display)
- **TC-INTG-002:** Provider switching mid-conversation
- **TC-INTG-003:** Project/session navigation with save
- **TC-INTG-004:** Template creation and insertion workflow

## 6. Frontend Architecture & Patterns

### 6.1 State Management (Zustand Stores)

**Store Structure:**
- `useChatStore`: Messages, current session, loading state
- `useProjectStore`: Projects, current project, hierarchy
- `useProviderStore`: Available providers, current provider
- `useTemplateStore`: Message templates, categories
- `useSettingsStore`: User settings and preferences

**Persistence:**
- All stores use Zustand `persist` middleware
- Data stored in browser localStorage
- Auto-sync across tabs/windows

### 6.2 Component Patterns

**Container Pattern:**
- Page components (ChatPage, SettingsPage) manage store + data fetching
- Presentational components receive data as props
- Hooks for state management separation

**Reusable Components:**
- Modal wrapper for dialogs
- Button with loading state
- Toast notifications for feedback
- Spinner for loading indicators

### 6.3 API Integration

**Service Layer (src/services/api.ts):**
- Axios instance with base URL
- Error handling and retry logic
- Request/response interceptors
- Type-safe API methods

**Async Patterns:**
- useEffect for data fetching
- Loading + error states
- Optimistic updates where appropriate

## 7. Key Frontend Files & Responsibilities

| File Path | Purpose | Status |
|-----------|---------|--------|
| src/pages/ChatPage.tsx | Main chat interface | implemented |
| src/pages/SettingsPage.tsx | Settings/configuration | implemented |
| src/components/ChatArea.tsx | Message display | implemented |
| src/components/ChatInput.tsx | User input with templates | implemented |
| src/components/ChatMessage.tsx | Individual message | implemented |
| src/components/Header.tsx | Top navigation bar | implemented |
| src/components/Sidebar.tsx | Left sidebar navigation | implemented |
| src/components/ProjectTree.tsx | Project hierarchy view | implemented |
| src/components/ProviderSelector.tsx | Provider dropdown | implemented |
| src/components/TemplateManager.tsx | Template CRUD modal | implemented |
| src/stores/chatStore.ts | Chat state (Zustand) | implemented |
| src/stores/projectStore.ts | Project state | implemented |
| src/stores/providerStore.ts | Provider state | implemented |
| src/stores/templateStore.ts | Template state | implemented |
| src/services/api.ts | HTTP client | implemented |
| src/test/components/*.test.tsx | Component tests | implemented |

## 8. Frontend UI/UX Guidelines

### 8.1 Styling

- **Framework:** Tailwind CSS utility classes
- **Color Scheme:** Light/dark theme ready
- **Icons:** Lucide React for consistent iconography
- **Spacing:** 4px grid system (Tailwind default)
- **Responsive:** Mobile-first approach (optional for now)

### 8.2 User Feedback

- **Loading:** Spinner component during async operations
- **Errors:** Toast notifications (error color)
- **Success:** Toast notifications (success color)
- **Confirmation:** Modal dialogs for destructive actions
- **Validation:** Real-time input validation with messages

### 8.3 Accessibility

- **WCAG 2.1 AA:** Target compliance level
- **Keyboard Navigation:** Full keyboard support
- **Screen Readers:** Proper ARIA labels
- **Color Contrast:** Sufficient contrast ratios
- **Focus Management:** Visible focus indicators

## 9. Notes for AI AGENTS (frontend)

- All components are TypeScript for type safety
- Use Zustand stores for state management (already set up)
- API calls go through src/services/api.ts (centralized)
- Test new components with Vitest + React Testing Library
- Component files use .tsx extension (TypeScript + JSX)
- Store files use .ts extension
- Follow existing component folder structure
- Use Tailwind CSS classes for styling (no separate CSS files)
- Import Lucide React icons as needed
- Document complex props with JSDoc comments
- Maintain consistency with existing components (naming, patterns)
- Backend contracts defined in MOD-BE.md service endpoints
- Cross-reference requirements in REQ-* format in comments
