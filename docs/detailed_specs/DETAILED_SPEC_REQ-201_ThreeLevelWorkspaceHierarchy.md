# REQ-201: Three-Level Workspace Hierarchy

**Registry Entry:** See `docs/01_requirements_registry.md` (Line 38)  
**Functionality Reference:** `specifications/functionality.md` Section 2.1.1  
**Document Version:** 1.0  
**Last Updated:** November 15, 2025  
**Status:** implemented  

---

## 1. Overview

### 1.1 Brief Description
Implement a three-level organizational structure (Main Chat → Projects → Sessions) that allows users to group related conversations and files into hierarchical projects, with each project containing multiple isolated chat sessions.

### 1.2 Business Value
- **Organization:** Users can organize conversations by topic/project, preventing context overload
- **Focus:** Sessions maintain isolated context, allowing focused work on specific topics
- **Scalability:** Hierarchy allows unlimited nesting of projects for complex workflows
- **Context Separation:** Sessions prevent conversation context from mixing between different topics

### 1.3 Scope & Boundaries

**In Scope:**
- ✅ Three-level structure: Main Chat ↔ Projects ↔ Sessions ↔ Messages
- ✅ Default project auto-created for initial "Main Chat"
- ✅ User-created projects at any level
- ✅ Nested project support (projects within projects)
- ✅ Session isolation (separate message histories)
- ✅ Project file workspace (shared across sessions)
- ✅ Session file workspace (session-specific files)

**Out of Scope:**
- ❌ Project templates (Phase 2)
- ❌ Project duplication/cloning (Phase 2)
- ❌ Cross-project search (Phase 2)
- ❌ Project sharing between users (out of scope - single user)
- ❌ Project archiving (Phase 2)

---

## 2. Functional Requirements

### 2.1 Core Requirements

#### REQ-201-A: Main Chat as Default Project
- **Description:** Application starts with "Main Chat" default project automatically created
- **Technical Details:**
  - Auto-created on first app launch (no user interaction needed)
  - UUID: Stored with specific constant ID for identification
  - Name: "Main Chat" (fixed, not user-editable)
  - Purpose: Entry point for casual conversations before creating formal projects
  - Behavior: Behaves identically to user-created projects
- **Acceptance Criteria:**
  - ✓ Exists immediately on app start (first launch creates it)
  - ✓ Cannot be deleted (safeguard against leaving app empty)
  - ✓ Cannot be renamed (remains "Main Chat")
  - ✓ Appears as top-level project in tree view
  - ✓ Has own file workspace for shared resources

#### REQ-201-B: Three-Level Hierarchy Structure
- **Description:** Data organized as Main Chat → Projects → Sessions → Messages
- **Technical Details:**
  ```
  Level 1: Main Chat (Default Project)
  └── Level 2: User Projects
      ├── Project A
      │   └── Level 3: Sessions
      │       ├── Session 1
      │       │   └── Messages
      │       └── Session 2
      │           └── Messages
      └── Project B
          └── Sessions...
  ```
- **File Structure:**
  - `data/projects/` - All projects (including Main Chat)
  - `data/chat_sessions/` - All sessions across all projects
  - `data/projects/{id}/files/` - Project-level files
  - `data/chat_sessions/{id}/files/` - Session-level files
- **Acceptance Criteria:**
  - ✓ Main Chat accessible at app startup
  - ✓ Can create projects under Main Chat
  - ✓ Can create sessions within any project
  - ✓ Messages isolated per session
  - ✓ File workspaces maintained at project and session levels

#### REQ-201-C: Project-to-Session Relationship
- **Description:** Each project contains multiple sessions with isolated contexts
- **Technical Details:**
  - Project stores list of session IDs (in project metadata)
  - Session stores parent project_id (foreign key)
  - One-to-many relationship: 1 project : N sessions
  - Each session has its own message history
- **Metadata Structure:**
  - Project metadata includes: session_ids array (denormalized for quick lookup)
  - Session metadata includes: project_id (required), title, created_at, message_count
- **Acceptance Criteria:**
  - ✓ Sessions cannot exist without parent project
  - ✓ Deleting project deletes all child sessions (cascade)
  - ✓ Sessions clearly tied to parent project
  - ✓ Session creation requires project selection

#### REQ-201-D: Nested Project Support
- **Description:** Projects can contain other projects (unlimited nesting depth)
- **Technical Details:**
  - Each project has optional parent_id field
  - parent_id = null indicates top-level project (under Main Chat)
  - child_ids array in project metadata for quick lookup
  - Recursive tree rendering in frontend
- **Example Hierarchy:**
  ```
  Main Chat/
    ├── AI Research/
    │   ├── Foundations (parent_id = AI Research ID)
    │   │   ├── Session: Intro to ML
    │   │   └── Session: Neural Nets
    │   └── Advanced Topics
    │       └── Session: Transformers
    └── Personal/
        ├── Learning (parent_id = Personal ID)
        └── Experiments
  ```
- **Acceptance Criteria:**
  - ✓ Create projects with optional parent
  - ✓ Tree renders recursively without depth limit
  - ✓ Delete parent doesn't orphan children (cascade)
  - ✓ Move operation supports parent reassignment

#### REQ-201-E: Session Isolation and Context Boundaries
- **Description:** Each session maintains completely isolated message history and context
- **Technical Details:**
  - Session has dedicated: `messages.json` file with full history
  - Session has dedicated: `metadata.json` with session config
  - Session has dedicated: `files/` directory for session-specific files
  - No cross-session message access by default
  - Context built from: session messages + project files + session files
- **Isolation Enforced:**
  - Backend API requires session_id for all message operations
  - Cannot query messages across multiple sessions
  - Each message tagged with session_id
- **Acceptance Criteria:**
  - ✓ Messages in Session A invisible to Session B
  - ✓ File operations scoped to session/project
  - ✓ Deleting session deletes all messages
  - ✓ Switching sessions shows different message history

#### REQ-201-F: File Workspace Hierarchy
- **Description:** Files organized at project and session levels with appropriate sharing
- **Technical Details:**
  - **Project files:** Shared across all sessions in project
    - Location: `data/projects/{project_id}/files/`
    - Accessible: All sessions in that project
    - Lifecycle: Deleted when project deleted
  - **Session files:** Specific to individual session
    - Location: `data/chat_sessions/{session_id}/files/`
    - Accessible: Only that session
    - Lifecycle: Deleted when session deleted
- **File Context in AI Calls:**
  - AI receives both project files and session files as context
  - User can reference files when asking questions
  - AI can access and reason about file contents
- **Acceptance Criteria:**
  - ✓ Project files accessible in all project sessions
  - ✓ Session files only accessible in that session
  - ✓ Files included in AI context appropriately
  - ✓ File scoping prevents unintended access

### 2.2 Technical Constraints

- **Hierarchy Depth:** No practical limit (recursive implementation supports any depth)
- **Sessions per Project:** Unlimited
- **Projects per Project:** Unlimited (nesting)
- **Message Count per Session:** Recommended < 10,000 (JSON file size concern)
- **File Space per Project:** 500MB limit enforced
- **File Space per Session:** 100MB limit enforced

### 2.3 User Interactions

**Creating the Hierarchy:**
```
1. App starts → Main Chat created automatically
2. User clicks "New Project" → "AI Research" created
3. User selects "AI Research" project
4. User clicks "New Session" → "Transformer Analysis" session created
5. User chats → Messages saved to session
6. User clicks "New Project" under AI Research → "Foundations" sub-project
7. User selects "Foundations" project
8. User can now create sessions under "Foundations"
```

**Navigating the Hierarchy:**
```
Sidebar shows:
- Main Chat (expanded)
  - AI Research (collapsible)
    ├─ Sessions list
    ├─ Foundations (sub-project, collapsible)
    │  └─ Sessions under Foundations
    └─ Advanced Topics
```

---

## 3. Implementation Details

### 3.1 Backend Implementation

**Services Affected:**
- `ProjectService` (backend/services/project_service.py)
- `ChatSessionService` (backend/services/chat_session_service.py)
- `UserStateService` (backend/services/user_state_service.py)

**Key Methods:**

- **`ProjectService.initialize_default_project()`** (lines 20-40)
  - Purpose: Create Main Chat project on first app launch
  - Called: In app startup sequence
  - Implementation:
    ```python
    def initialize_default_project(self) -> Project:
        """Create default 'Main Chat' project if not exists"""
        # Check if default project exists
        default_id = UUID('00000000-0000-0000-0000-000000000001')
        existing = self._load_project_metadata(default_id)
        if existing:
            return existing
        
        # Create new default project
        project = Project(
            id=default_id,
            name="Main Chat",
            description="Default project for main chat",
            parent_id=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self._save_project_metadata(project)
        return project
    ```

- **`ProjectService.create_project()`** at lines 42-75
  - Purpose: Create new project with optional parent
  - Parameters: name, description, parent_id (optional)
  - Returns: Project object
  - Updates parent's child_ids if parent_id provided

- **`ProjectService.get_project_tree()`** at lines 100-130
  - Purpose: Get hierarchical tree of all projects and sessions
  - Returns: Nested dict structure for frontend tree rendering
  - Implementation: Recursive traversal building tree with children
  ```python
  def get_project_tree(self) -> Dict:
      """Get hierarchical project tree"""
      # Find all top-level projects (parent_id = None)
      # For each, recursively get children
      # Include sessions for each project
      return {
          "id": uuid,
          "name": "Main Chat",
          "projects": [...recursively...],
          "sessions": [...]
      }
  ```

- **`ChatSessionService.create_session()`** at lines 150-185
  - Purpose: Create session under specified project
  - Requires: project_id (must exist)
  - Returns: ChatSession object
  - Side effect: Updates project's session_ids list
  ```python
  def create_session(self, name: str, project_id: UUID) -> ChatSession:
      """Create new session under project"""
      # Verify project exists
      project = self.project_service.get_project(project_id)
      if not project:
          raise ValueError(f"Project {project_id} not found")
      
      session = ChatSession(
          id=uuid4(),
          project_id=project_id,  # Foreign key
          title=name,
          created_at=datetime.now()
      )
      
      # Save and update parent project
      self._save_session_metadata(session)
      self._add_session_to_project(project_id, session.id)
      
      return session
  ```

- **`ChatSessionService.delete_session()`** at lines 187-210
  - Purpose: Delete session and all its messages
  - Requires: session_id and project_id (for validation)
  - Side effect: Removes session_id from project's session list
  - Cascade: Deletes messages, files, metadata

**Data Structures:**

```python
# Project model with hierarchy support
class Project(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    parent_id: Optional[UUID] = None      # Enables nesting
    child_ids: List[UUID] = []             # Denormalized for quick lookup
    session_ids: List[UUID] = []           # Denormalized sessions list
    created_at: datetime
    updated_at: datetime
    path: str

# ChatSession model with project reference
class ChatSession(BaseModel):
    id: UUID
    project_id: UUID                       # Foreign key to project
    title: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    is_active: bool = True
    metadata: Dict[str, Any] = {}

# Message model with session reference
class Message(BaseModel):
    id: UUID
    session_id: UUID                       # Foreign key to session
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime
    # ... other fields
```

### 3.2 Frontend Implementation

**Components Affected:**
- `ProjectTree.tsx` - Renders hierarchical project structure
- `SessionList.tsx` - Lists sessions under current project
- `Sidebar.tsx` - Navigation with both trees
- `MainLayout.tsx` - Selection and routing

**Key Functions:**

- **`ProjectTree.tsx` recursive rendering** (lines 20-60)
  ```typescript
  interface ProjectNode {
    id: string
    name: string
    projects?: ProjectNode[]      // Child projects
    sessions?: SessionNode[]       // Sessions in this project
  }
  
  const renderProjectTree = (node: ProjectNode, level: number) => {
    return (
      <div key={node.id} className="ml-4">
        <ProjectItem 
          project={node}
          onClick={() => selectProject(node.id)}
        />
        {node.projects?.map(child => 
          renderProjectTree(child, level + 1)
        )}
        {node.sessions?.map(session =>
          <SessionItem key={session.id} session={session} />
        )}
      </div>
    )
  }
  ```

- **`useProjectStore` Zustand state** (in frontend/src/stores/)
  ```typescript
  interface ProjectStore {
    currentProject: Project | null
    projectTree: ProjectNode
    setCurrentProject: (project: Project) => void
    loadProjectTree: () => Promise<void>
    createProject: (name: string, parentId?: UUID) => Promise<Project>
    deleteProject: (projectId: UUID) => Promise<void>
  }
  ```

- **`useChatSessionStore` Zustand state** (in frontend/src/stores/)
  ```typescript
  interface SessionStore {
    currentSession: ChatSession | null
    sessions: ChatSession[]         // Sessions in current project
    setCurrentSession: (session: ChatSession) => void
    loadSessions: (projectId: UUID) => Promise<void>
    createSession: (name: string, projectId: UUID) => Promise<ChatSession>
    deleteSession: (sessionId: UUID) => Promise<void>
  }
  ```

### 3.3 API Endpoints

- **GET** `/api/projects/tree` - Get hierarchical project tree
  - Response: Complete tree with projects and sessions nested
  - Used by: Frontend ProjectTree component
  
- **POST** `/api/projects` - Create new project
  - Request: `{ name, description, parent_id? }`
  - Response: Project object
  - Side effect: Updates parent's child_ids if parent provided

- **DELETE** `/api/projects/{project_id}` - Delete project
  - Cascade: Deletes all child projects and sessions
  - Side effect: Removes from parent's child_ids

- **GET** `/api/chat_sessions?project_id={id}` - Get sessions for project
  - Response: List of ChatSession objects
  - Filters: Only sessions with matching project_id

- **POST** `/api/chat_sessions` - Create session
  - Request: `{ title, project_id }`
  - Response: ChatSession object
  - Requires: project_id must exist

---

## 4. Testing Strategy

### 4.1 Unit Tests

**Test File:** `tests/unit/test_workspace_hierarchy.py`

**Test Case: test_default_project_creation**
- **Setup:** Fresh app state
- **Action:** Call ProjectService.initialize_default_project()
- **Assertion:**
  - ✓ Project created with name "Main Chat"
  - ✓ Project has fixed UUID
  - ✓ parent_id is null
  - ✓ Cannot be deleted
- **Location:** `tests/unit/test_workspace_hierarchy.py` lines 10-30

**Test Case: test_nested_project_creation**
- **Setup:** Main Chat project exists
- **Action:** Create project "Research" with parent = Main Chat ID
- **Assertion:**
  - ✓ Child project created
  - ✓ parent_id set correctly
  - ✓ Parent's child_ids updated
  - ✓ Tree structure reflects nesting
- **Location:** `tests/unit/test_workspace_hierarchy.py` lines 32-55

**Test Case: test_session_creation_requires_project**
- **Setup:** No projects exist
- **Action:** Try to create session without project
- **Assertion:**
  - ✓ ValueError raised with message "Project not found"
  - ✓ Session not created
  - ✓ Error message helpful
- **Location:** `tests/unit/test_workspace_hierarchy.py` lines 57-70

**Test Case: test_session_isolation**
- **Setup:** Project with 2 sessions, each with 3 messages
- **Action:** Query messages for session 1
- **Assertion:**
  - ✓ Only 3 messages returned (not 6)
  - ✓ All messages belong to session 1
  - ✓ Session 2 messages invisible
- **Location:** `tests/unit/test_workspace_hierarchy.py` lines 72-90

**Test Case: test_project_tree_structure**
- **Setup:** Complex hierarchy (Main Chat > AI > Foundations + Advanced, Personal > Learning)
- **Action:** Call get_project_tree()
- **Assertion:**
  - ✓ Returns nested structure
  - ✓ Depth correct
  - ✓ All projects present
  - ✓ Sessions listed under projects
- **Location:** `tests/unit/test_workspace_hierarchy.py` lines 92-120

**Test Case: test_cascade_delete_project**
- **Setup:** Project with 3 sessions and files
- **Action:** Delete parent project
- **Assertion:**
  - ✓ Project deleted
  - ✓ All 3 sessions deleted
  - ✓ All session files deleted
  - ✓ Project files deleted
- **Location:** `tests/unit/test_workspace_hierarchy.py` lines 122-145

### 4.2 Functional Tests

**Test File:** `tests/functional/test_hierarchy_ui.py`

- **test_project_tree_rendering:** Project tree displays with correct nesting
- **test_session_list_updates:** Session list updates when switching projects
- **test_create_project_modal:** Can create nested projects from UI

### 4.3 E2E Tests

**Test File:** `tests/test_e2e_workflows.py`

- **test_complete_hierarchy_workflow:** Create projects → sessions → send messages → verify isolation
  - Steps:
    1. App starts (Main Chat created)
    2. Create "AI Research" project
    3. Create "Foundations" sub-project
    4. Create "Intro to ML" session under Foundations
    5. Send message "What is ML?"
    6. Switch to different session
    7. Send message "What is Deep Learning?"
    8. Switch back to first session
    9. Verify first message is still there, second message is not
    10. Switch back to second session
    11. Verify second message is present, first message is not

### 4.4 Test Coverage

- **Target Coverage:** 90% for hierarchy logic
- **Critical Paths:**
  - Default project creation and immutability
  - Nested project creation and deletion
  - Session isolation
  - Tree structure generation
  - Cascade deletes

---

## 5. Dependencies & Relationships

### 5.1 Depends On

| REQ-ID | Title | Reason |
|--------|-------|--------|
| REQ-101 | File-based data persistence | Hierarchy depends on persistent storage of projects/sessions |
| REQ-102 | Directory hierarchy with metadata | Directory structure supports project/session organization |
| REQ-103 | Version control in metadata | Timestamps track when projects/sessions created |

### 5.2 Enables / Unblocks

| REQ-ID | Title | How |
|--------|-------|-----|
| REQ-202 | Default project auto-creation | Implemented as part of this requirement |
| REQ-203 | Default project functionality | Main Chat has same capabilities as user projects |
| REQ-204 | User-created projects | This requirement enables creating projects beyond default |
| REQ-205 | Nested project structure | Implemented as part of this requirement |
| REQ-206 | Chat session isolation | Sessions isolated within projects |
| REQ-213 | Session CRUD operations | Sessions exist within this hierarchy |
| REQ-210 | Project tree view | Tree rendering depends on hierarchy structure |
| REQ-310 | Project tree in sidebar | UI component renders this hierarchy |

### 5.3 Related Features

- **Project Search:** Can search across projects (future)
- **Project Templates:** Can clone project structures (future)
- **Project Archiving:** Can archive old projects (future)
- **Cross-project References:** Can link between projects (future)

---

## 6. Known Issues & Notes

### 6.1 Implementation Notes

| Aspect | Specification | Actually Done | Reason |
|--------|---|---|---|
| Session storage | Under projects | Flat structure at data root | Simpler implementation, same functionality |
| Default project UUID | Spec flexible | Fixed UUID 00000000-0000-0000-0000-000000000001 | Enables reliable identification |
| Main Chat editability | Not specified | Immutable (cannot rename/delete) | User safeguard |
| Denormalization | Not specified | child_ids and session_ids stored in metadata | Performance optimization |

### 6.2 Limitations

- No project-level permissions (single user only)
- No project cloning or templates (Phase 2)
- No batch operations on projects (Phase 2)
- Nesting depth unlimited but UI may struggle with very deep hierarchies
- No project move/reorganization (Phase 2)

### 6.3 Future Enhancements

- **Phase 2:** Add project templates for quick creation
- **Phase 2:** Add project cloning with duplicate sessions
- **Phase 2:** Add project archiving
- **Phase 3:** Add project-level settings (AI preferences, defaults)
- **Phase 4:** Add cross-project file sharing

---

## 7. Acceptance Checklist

- [x] Requirement implemented per specification
- [x] Default project creates automatically
- [x] Nesting works recursively
- [x] Sessions properly isolated
- [x] File workspaces scoped correctly
- [x] All unit tests passing (TC-UNIT-201)
- [x] Integration tests passing
- [x] E2E tests passing
- [x] Code reviewed and approved
- [x] Documentation updated
- [x] Production ready

---

## 8. Related Documentation

- [Functionality.md Section 2.1.1](../specifications/functionality.md#211-workspace-organization-architecture)
- [MOD-BE.md Section 5.1](../modules/MOD-BE.md#51-projectservice)
- [MOD-FE.md Section 3.1](../modules/MOD-FE.md#31-screencomponent-list)
- [Requirements Registry REQ-201-205](../01_requirements_registry.md#ii-workspace-organization--structure)

---

## 9. Examples & Use Cases

### 9.1 Happy Path: Creating Nested Project Structure

```
Step 1: App starts
  Backend: initialize_default_project() called
  Backend: Main Chat project created with UUID 00000000-0000-0000-0000-000000000001
  Frontend: Tree shows "Main Chat" at root
  
Step 2: User clicks "New Project", enters "AI Research"
  Backend: create_project(name="AI Research", parent_id=None)
  Backend: New project created as sibling to Main Chat
  Backend: Tree updated to show both projects
  
Step 3: User right-clicks "AI Research", creates child project "Foundations"
  Backend: create_project(name="Foundations", parent_id=<AI Research UUID>)
  Backend: parent_id set, added to AI Research's child_ids
  Backend: Tree shows Foundations indented under AI Research
  
Step 4: User selects "Foundations", creates session "Intro to ML"
  Backend: create_session(name="Intro to ML", project_id=<Foundations UUID>)
  Backend: Session created with project_id reference
  Backend: Session appears under Foundations in tree
  
Step 5: User sends message "What is machine learning?"
  Backend: Message saved to session's messages.json
  Backend: message_count incremented in session metadata
  
Result: ✓ Full hierarchy created and working
```

### 9.2 Session Isolation Verification

```
Setup: Two sessions under same project
  - Session A: "Machine Learning" with 5 messages
  - Session B: "Deep Learning" with 3 messages

Step 1: User selects Session A
  Frontend: GET /api/chat_sessions/{sessionA_id}/messages
  Backend: Returns only messages from sessionA (5 messages)
  Display: Shows "What is ML?", "Explain backprop", etc.
  
Step 2: User switches to Session B
  Frontend: GET /api/chat_sessions/{sessionB_id}/messages
  Backend: Returns only messages from sessionB (3 messages)
  Display: Shows "What is a neuron?", "Explain attention", etc.
  
Step 3: User switches back to Session A
  Frontend: GET /api/chat_sessions/{sessionA_id}/messages
  Backend: Returns original 5 messages from sessionA
  Display: Shows same messages as before (isolated)
  
Result: ✓ Sessions maintain complete isolation
```

### 9.3 Cascade Delete

```
Setup: Project "AI Research" with:
  - Subproject "Foundations"
  - Direct sessions: "Session 1", "Session 2"
  - Each session has 10 messages and 5 files

User Action: Clicks delete on "AI Research"

Backend Cascade:
  1. Delete all sessions under "AI Research" (2 sessions)
  2. For each session:
     a. Delete all messages (20 total)
     b. Delete all files in session (10 total)
     c. Delete session metadata
  3. Delete all child projects (Foundations + all its content)
  4. Delete project files (project-level workspace)
  5. Delete project metadata
  
Result: ✓ Entire hierarchy cleaned up completely
```

---

## Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-15 | Development Team | Initial detailed specification creation |

---

**Status:** Ready for team use and implementation reference
