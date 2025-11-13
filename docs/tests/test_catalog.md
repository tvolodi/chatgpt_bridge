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

## 2. Example Test Cases

### TC-ID: TC-UNIT-001
- Type: unit
- Related Requirements:
  - REQ-001
- Related Modules:
  - MOD-FE-Login
- Pre-Conditions:
  - Component \`LoginForm\` compiled.
- Test Steps:
  1. Render \`LoginForm\`.
  2. Type invalid email.
  3. Blur the field.
- Expected Result:
  - Validation error message is shown.
- Status: implemented
- Automation Location:
  - File: \`frontend/src/components/LoginForm.test.tsx\`
  - Framework: Jest + Testing Library

### TC-ID: TC-E2E-001
- Type: e2e
- Related Requirements:
  - REQ-001
- Related Modules:
  - MOD-FE-Login, MOD-BE-Auth
- Pre-Conditions:
  - User with email/password exists in DB.
- Test Steps:
  1. Open \`/login\` in browser.
  2. Enter valid email/password.
  3. Click "Log In".
- Expected Result:
  - User lands on \`/dashboard\` with greeting.
- Status: automated
- Automation Location:
  - File: \`e2e/login.spec.ts\`
  - Framework: Playwright
