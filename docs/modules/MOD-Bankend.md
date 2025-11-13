# DOCUMENT_TYPE: MODULE_SPEC
# MODULE_ID: MOD-BACKEND-Template
# MODULE_TYPE: backend
# VERSION: 1.0

## 1. Meta

- Name: AI Chat Assistant - Backend Module Specification
- Owner:
- Status: in_progress <proposed | in_progress | implemented | tested | accepted>
- Tech Stack:
  - Language: Python
  - Framework: FastAPI
  - Database: Json / SQLite
  - External Services: OpenAI API, Anthropic API

## 2. Linked Requirements

- REQ-XXX
- REQ-YYY

## 3. Public API (Endpoints)

### 3.1 Endpoint List

| EP_ID          | Method | Path                | Description                 | Status       | Requirements |
|----------------|--------|---------------------|-----------------------------|-------------|--------------|
| EP-Example     | POST   | /api/example        | Example endpoint            | proposed    | REQ-XXX      |

### 3.2 Endpoint Specification: EP-Example

- EP_ID:
- Method:
- Path:
- Related REQ:
- Status:

#### Request

\`\`\`json
{
  "field": "value"
}
\`\`\`

Validation rules:

- 

#### Responses

- \`200 OK\`

\`\`\`json
{
  "result": "ok"
}
\`\`\`

- Error codes (e.g. 400, 401, 500):

#### Business Logic

- Steps:
  1. 
  2. 

#### Performance Expectations

- Target response time:
- Indexes / caching:

#### Security

- Authentication:
- Authorization:
- Rate limiting:

## 4. Data Model

### 4.1 Example Entity

- Table / Collection:
- Fields:
  - \`id\`:
  - \`created_at\`:

## 5. Internal Services

- \`ExampleService\`
  - Methods:
    - \`doSomething(args): Result\`

## 6. Implementation Status per Feature

| Feature_ID  | Description             | Status       | Notes |
|-------------|------------------------|-------------|-------|
| BE-Example  | Example feature        | not_started |       |

## 7. Backend Tests (Unit, Functional, E2E)

### 7.1 Unit Tests

- TC-UNIT-XXX
  - Scope:
  - Related Requirement:

### 7.2 Functional Tests

- TC-FUNC-XXX
  - Scope:

### 7.3 E2E Tests (optional)

- TC-E2E-XXX
  - Flow:

## 8. Notes for AI AGENTS (backend)

- Generate models, services, and endpoints according to sections 3–5.
- Maintain consistency with any frontend contracts defined in MOD-FRONTEND-* specs.
