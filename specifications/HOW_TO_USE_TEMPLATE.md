# How to Use the Detailed Requirement Template

**Purpose:** Quick reference guide for creating detailed requirement specifications  
**Last Updated:** November 15, 2025

---

## Quick Start (5 Minutes)

### 1. Find Your Requirement
Look in `docs/01_requirements_registry.md`:

```markdown
| REQ-101 | File-based data persistence | functional | critical | implemented |
```

### 2. Open the Template
Copy template from: `specifications/DETAILED_REQUIREMENT_TEMPLATE.md`

### 3. Fill in Sections
Focus on these key sections (in order):
1. **Header** (5 min): REQ ID, Status, Date
2. **Section 1** (5 min): Overview and scope
3. **Section 3.1** (15 min): Backend implementation details
4. **Section 4.1** (10 min): Test cases
5. **Section 9** (10 min): Examples

### 4. Save with Naming Convention
```
docs/detailed_specs/DETAILED_SPEC_[REQ-ID]_[SHORT_TITLE].md
```

Example:
```
docs/detailed_specs/DETAILED_SPEC_REQ-501_MultiProviderSupport.md
```

---

## Section-by-Section Guide

### Section 1: Overview (Most Important)
**Time: 10 minutes**

#### 1.1 Brief Description
- **What to write:** One sentence explaining what users/system get
- **Example (Good):** "Allow users to switch between multiple AI providers without interrupting conversation"
- **Example (Bad):** "Provider selector implementation"
- **Length:** 1 sentence, max 20 words

#### 1.2 Business Value
- **What to write:** 2-4 bullets explaining WHY this matters
- **Format:** Benefits to user, not technical details
- **Examples:**
  - ✅ "Users not locked into single AI provider"
  - ✅ "Compare outputs from multiple AI models"
  - ❌ "Implements dropdown component"

#### 1.3 Scope & Boundaries
- **In Scope:** List things that ARE included
- **Out of Scope:** List things that are NOT (including future ideas)
- **Why:** Prevents scope creep, clarifies what's a different requirement

**Example:**
```markdown
**In Scope:**
- ✅ Display available providers
- ✅ Switch providers mid-conversation
- ✅ Persist provider selection

**Out of Scope:**
- ❌ Provider configuration (separate requirement)
- ❌ Custom provider creation (future phase)
- ❌ Provider comparison tool (separate feature)
```

---

### Section 2: Functional Requirements (Critical)
**Time: 20 minutes**

#### 2.1 Core Requirements
**What to write:** Break requirement into sub-components

**Example Structure:**
```markdown
#### REQ-501-A: Provider Selector in Header
- **Description:** Display dropdown showing available providers
- **Acceptance Criteria:**
  - ✓ Shows all configured providers
  - ✓ Shows current selection with checkmark
  - ✓ Shows provider status (available/unavailable)
  - ✓ Click to select provider

#### REQ-501-B: One-Click Provider Switching
- **Description:** Switch between providers without losing chat context
- **Acceptance Criteria:**
  - ✓ Selected provider highlighted
  - ✓ Previous messages remain visible
  - ✓ New messages use selected provider
  - ✓ No interruption to user
```

**Pro Tips:**
- Each sub-requirement should be testable
- Acceptance criteria should be checkable (yes/no)
- Use ✓ symbols for clarity

#### 2.2 Technical Constraints
- **What to write:** Limitations, performance requirements
- **Examples:**
  - "Temperature must be between 0.0 and 2.0"
  - "Maximum 5 concurrent requests per provider"
  - "Response must arrive within 30 seconds"

#### 2.3 User Interactions
- **What to write:** How users interact with this feature
- **Include:** Normal flow, edge cases, errors
- **Example:**
  ```
  Normal: User clicks provider → sees dropdown → selects new provider
  Edge case: User selects unconfigured provider → disabled (grayed out)
  Error: API down → show "Provider unavailable" message
  ```

---

### Section 3: Implementation Details (Most Technical)
**Time: 30 minutes**

#### 3.1 Backend Implementation

**Write:**
```markdown
**Services Affected:**
- ServiceName (backend/services/file_name.py)

**Key Methods:**
- method_name() at lines X-Y in filename.py
  - Purpose: What it does
  - Key logic: Brief explanation
```

**How to find this info:**
1. Open `specifications/functionality.md`
2. Find your requirement section
3. Copy the "Backend:" lines
4. Add actual line numbers from the code

**Example (Good):**
```markdown
**Services Affected:**
- AIProviderService (backend/services/ai_provider_service.py)

**Key Methods:**
- get_available_providers() at lines 45-62
  - Loads providers from data/providers.json
  - Filters by is_available flag
  - Returns list of AIProvider objects
```

**Example (Bad):**
```markdown
**Services Affected:**
- AI stuff

**Key Methods:**
- Get providers
  - Does something
```

#### 3.2 Frontend Implementation

**Write:**
```markdown
**Component(s) Affected:**
- ComponentName.tsx (path/to/file.tsx)

**Key Methods:**
- functionName() at lines X-Y in ComponentName.tsx
  - Purpose: What it does
  - User-visible behavior: What user sees
```

**State Management:**
```markdown
- selectedProvider: UUID of currently selected provider
- availableProviders: List of AIProvider objects
- isDropdownOpen: Boolean for dropdown visibility
```

#### 3.3 API Endpoints

**Format:**
```markdown
- **METHOD** `/api/endpoint-path` - Description
  - Request: `{ field1, field2 }`
  - Response: `{ result_field }`
  - Error codes: `400, 404, 500`
```

**Example:**
```markdown
- **GET** `/api/providers` - Get list of available providers
  - Response: `[{ id, name, is_available, model_count }]`
  - Error codes: `500`

- **POST** `/api/conversations/send` - Send message
  - Request: `{ session_id, provider_id, content }`
  - Response: `{ message_id, content, status }`
  - Error codes: `400, 404, 500`
```

---

### Section 4: Testing Strategy (Critical)
**Time: 20 minutes**

#### 4.1 Unit Tests

**Format:**
```markdown
**Test File:** `tests/test_[service_name].py`

**Test Case: test_[feature_name]_success**
- **Setup:** Initial state before test
- **Action:** What we're testing
- **Assertion:** Expected result
```

**Example:**
```markdown
**Test Case: test_get_available_providers**
- **Setup:** Three providers configured, one with missing API key
- **Action:** Call get_available_providers()
- **Assertion:** Returns only providers with is_available=True (2 providers)
```

**How to find test info:**
1. Look at `tests/test_*.py` files
2. Check what tests exist for this service
3. If tests don't exist, suggest what tests SHOULD be created
4. Reference actual test file names

#### 4.2-4.4 Other Tests
- **Integration Tests:** How this works with other services
- **E2E Tests:** Complete user workflow
- **Coverage Target:** Percentage of code covered by tests

---

### Section 5: Dependencies & Relationships
**Time: 10 minutes**

#### 5.1 Depends On
**What to write:** What this requirement needs to work

| REQ-ID | Title | Reason |
|--------|-------|--------|
| REQ-105 | API key management | Provider selector needs configured API keys |
| REQ-301 | Header bar | Provider selector displayed in header |

**How to find:**
- Look at registry for "Sources" column
- Check if other REQ-IDs mentioned in description
- Look at Section 5.2 "Enables" in other requirements

#### 5.2 Enables / Unblocks
**What to write:** What this requirement enables other things to work

| REQ-ID | Title | How |
|--------|-------|-----|
| REQ-514 | Send message to provider | Need to know which provider to use |
| REQ-511 | Provider switching | Depends on provider selector |

---

### Section 6: Known Issues & Notes
**Time: 10 minutes**

#### 6.1 Implementation Notes
**Write if implementation differs from spec:**

| Aspect | Spec Says | Actually Done | Reason |
|--------|-----------|---------------|--------|
| Message format | .jsonl (streaming) | .json (array) | Simpler for current volumes |

#### 6.2 Limitations
**Examples:**
- "No API caching - each request hits provider"
- "Dropdown only shows 20 providers max"
- "No offline support for switching providers"

#### 6.3 Future Enhancements
- "Phase 2: Add provider comparison view"
- "Phase 3: Custom provider creation"

---

### Section 9: Examples & Use Cases (Important for clarity)
**Time: 15 minutes**

**What to write:** Real-world scenario showing the requirement in action

**Format:**
```
Step 1: User does X
  Backend does Y
  System response: Z

Step 2: User does A
  Backend does B
  System response: C
```

**Good Example:**
```
User clicks provider dropdown
  Frontend shows list of 3 providers
  OpenAI (✓ selected)
  Claude (available)
  Ollama (not configured - disabled)

User clicks Claude
  Frontend updates selectedProvider state
  Previous messages stay visible
  Next message will use Claude provider
  User types new message and sends
  Claude generates response instead of OpenAI
```

**Bad Example:**
```
User clicks provider
Provider changes
```

---

## Filling in Section 3 (Backend Implementation) - Detailed Example

### Find the Information

**Step 1:** Look in `specifications/functionality.md`:
```markdown
### 5.3 Provider Selection & Switching
**Status:** ✅ Fully Implemented

- **Requirement 5.3.1:** Provider selector dropdown in header
  - **Implementation:** ✅ Fully implemented
  - **Location:** Header bar right section
```

**Step 2:** Search code for the service:
```bash
# In backend/services/ai_provider_service.py
grep -n "def.*provider" ai_provider_service.py
```

**Step 3:** Look at the actual code:
```python
# Line 45-62 in ai_provider_service.py
def get_available_providers(self) -> List[AIProvider]:
    """Get all configured providers."""
    providers = []
    for provider_file in self.data_dir.glob('*.json'):
        provider_data = self._load_provider(provider_file)
        if provider_data['is_available']:
            providers.append(AIProvider(**provider_data))
    return providers
```

### Write the Documentation

```markdown
### 3.1 Backend Implementation

**Services Affected:**
- `AIProviderService` (backend/services/ai_provider_service.py)

**Key Methods:**

- `get_available_providers()` at lines 45-62
  - Purpose: Retrieve all configured providers with available status
  - Key logic: Loads provider JSON files, filters by is_available flag
  - Returns: List[AIProvider] with metadata

- `select_provider(provider_id)` at lines 64-75
  - Purpose: Update current provider selection
  - Key logic: Validates provider_id exists, updates state
  - Returns: Selected AIProvider

**Data Structures:**

AIProvider model:
```json
{
  "id": "openai-001",
  "name": "OpenAI",
  "description": "GPT-4 and GPT-3.5",
  "base_url": "https://api.openai.com/v1",
  "is_available": true,
  "models": ["gpt-4", "gpt-3.5-turbo"],
  "model_count": 2
}
```
```

---

## Common Mistakes to Avoid

### ❌ Too Vague
```markdown
Backend: ChatService handles this
```
**Fix:** Provide actual class names, method names, and line numbers

### ❌ Just Code Snippets
```markdown
def send_message(self, message):
    return self.api.post(message)
```
**Fix:** Explain what the code does and why, with context

### ❌ Copying Spec Exactly
```markdown
This requirement enables feature X to work (just copied from spec)
```
**Fix:** Expand with actual details - HOW does it enable it?

### ❌ Missing Acceptance Criteria
```markdown
REQ-501-A: Provider selector
  Description: Show providers
```
**Fix:** Add measurable acceptance criteria:
```markdown
REQ-501-A: Provider selector
  Description: Show dropdown with providers
  Acceptance Criteria:
    ✓ Dropdown shows all configured providers
    ✓ Checkmark indicates current provider
    ✓ Unconfigured providers show as disabled
    ✓ Click provider switches selection
```

### ❌ No Examples
Document without showing real usage is hard to understand

**Fix:** Include at least 2 examples:
1. Happy path (normal usage)
2. Error/edge case

---

## Time Estimates

| Section | Time | Difficulty |
|---------|------|------------|
| 1. Overview | 10 min | Easy |
| 2. Functional Requirements | 20 min | Medium |
| 3. Implementation Details | 30 min | Hard |
| 4. Testing Strategy | 20 min | Medium |
| 5. Dependencies | 10 min | Easy |
| 6. Known Issues | 10 min | Easy |
| 7-8. Checklists | 5 min | Easy |
| 9. Examples | 15 min | Medium |
| **Total** | **120 min** | **~2 hours** |

**Time-Saving Tips:**
- Copy from `functionality.md` sections
- Reuse example from existing detailed specs
- Ask AI for help on backend code analysis
- Use template sections as checklists

---

## Workflow: From Registry to Detailed Spec

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  1. READ requirement in registry                           │
│     docs/01_requirements_registry.md                       │
│                                                             │
│  2. FIND source in functionality.md                        │
│     Look for matching "Func X.X.X" reference             │
│                                                             │
│  3. IDENTIFY implementation details                        │
│     Service names, file paths, line numbers              │
│                                                             │
│  4. SEARCH code for actual implementation                 │
│     backend/services/*.py, frontend/pages/*.tsx          │
│                                                             │
│  5. COPY template                                          │
│     specifications/DETAILED_REQUIREMENT_TEMPLATE.md      │
│                                                             │
│  6. FILL sections systematically                          │
│     1→2→3.1→3.2→4.1→5→6→9                               │
│                                                             │
│  7. ADD examples from real code/UI                        │
│     Show actual API calls, file paths, states            │
│                                                             │
│  8. SAVE with convention                                   │
│     docs/detailed_specs/DETAILED_SPEC_REQ-[ID]_[Title].md│
│                                                             │
│  9. UPDATE registry with link                             │
│     Add reference to detailed spec in Notes column       │
│                                                             │
│  10. REVIEW for completeness                              │
│      Check all sections filled, examples work             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Validation Checklist

Before finalizing your detailed spec, verify:

- [ ] **Header:** REQ-ID, Status, Dates filled
- [ ] **Overview:** Why does this matter? (Business value)
- [ ] **Requirements:** At least 3 sub-requirements with acceptance criteria
- [ ] **Backend:** Actual service names, method names, line numbers
- [ ] **Frontend:** Component names, state variables
- [ ] **Tests:** References to actual test files (or what should be tested)
- [ ] **Dependencies:** Lists what's needed and what's enabled
- [ ] **Examples:** Shows normal usage + error case
- [ ] **Links:** All references are valid (no broken links)
- [ ] **Tone:** Technical but readable (not overly complex)

---

## Examples from Codebase

### REQ-101: File-based Data Persistence
**Template:** `docs/detailed_specs/DETAILED_SPEC_REQ-101_FileBasedPersistence.md`
- ✅ Complete implementation details
- ✅ Shows file structure with actual paths
- ✅ JSON examples with real field names
- ✅ Detailed test cases with setup/action/assertion
- ✅ Migration path documented

**Use this as reference for quality.**

---

## Need Help?

- **Question:** "How do I find method names and line numbers?"
  - **Answer:** Search GitHub or use IDE search feature (Ctrl+F)

- **Question:** "What if method doesn't exist yet?"
  - **Answer:** Document what SHOULD be created, mark as "Planned"

- **Question:** "How detailed should examples be?"
  - **Answer:** Detailed enough that someone reading can follow without code

- **Question:** "Should I include ALL acceptance criteria?"
  - **Answer:** Include the critical ones, mention "see test file for complete list"

---

**Last Updated:** November 15, 2025  
**Version:** 1.0
