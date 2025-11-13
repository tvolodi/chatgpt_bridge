# DOCUMENT_TYPE: REQUIREMENTS_REGISTRY
# VERSION: 1.0

> Single source of truth for all requirements.

## 1. Status Legend

- `proposed`, `approved`, `in_progress`, `implemented`, `tested`, `accepted`, `deprecated`

## 2. Requirements Table

| REQ_ID   | Title                           | Type            | Priority | Status     | Description                                                    | Sources (Product Brief refs) | Modules (FE/BE)                           | Tests (IDs)                          | Notes |
|----------|---------------------------------|-----------------|----------|-----------|----------------------------------------------------------------|------------------------------|------------------------------------------|--------------------------------------|-------|
| REQ-001  | User login via email & password | functional      | high     | approved  | User can log in with email & password and see dashboard.       | F1 (Login)                   | MOD-FE-Login, MOD-BE-Auth                 | TC-UNIT-001, TC-FUNC-001, TC-E2E-001 |       |
| REQ-002  | Password reset via email link   | functional      | medium   | proposed  | User can request a reset link and set a new password.          | F2 (Password reset)         | MOD-FE-Login, MOD-BE-Auth, MOD-BE-Email   | TC-FUNC-002, TC-E2E-002              |       |
| REQ-010  | Login response time             | non_functional  | medium   | proposed  | 95% of login requests < 500ms under normal load.               |                              | MOD-BE-Auth, MOD-BE-DB                    | TC-FUNC-010                          |       |
| REQ-011  | Password encryption             | security        | high     | approved  | Passwords stored using strong hashing algorithm.               |                              | MOD-BE-Auth                              | TC-UNIT-010                          |       |

## 3. Notes

- Add one row per requirement.
- Always keep `Modules (FE/BE)` and `Tests (IDs)` updated.
- AI AGENTS: use this table to understand **what** must exist and where.
