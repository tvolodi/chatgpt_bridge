# Documentation
Do not generate .md files if they are not asked directly.

Feature implementation rules:
1. **Always** treat `docs/01_requirements_registry.md` as the main truth for the feature that must be implemented.
2. Use correspondent **module specs** (`doc/modules/MOD-<module>.md` files) for detailed implementation guidance.
3.For each requirement:
    - Define unit tests (core logic).
    - Define functional tests (API or UI flows).
    - Define e2e tests (cross-module flows).
    - Document them in `docs/tests/test_catalog.md`.
    - Reference `TC-*` IDs in:
        - Requirements registry (`Tests (IDs)` column).
        - Module specs (test sections).
3. Implement the feature using:
     - Module spec (`doc/modules/MOD-<module>.md` file)
     - Related `REQ-*` entries from the registry
     - Related `TC-*` definitions from the test catalog
   - Generate:
     - Source code aligned with the module spec and requirements.
     - Test code aligned with the test descriptions.
4.  - Update statuses:
        - In module specs `doc/modules/MOD-<module>.md` (feature & implementation status).
        - In test catalog `docs/tests/test_catalog.md` (test implementation/automation status).
        - In requirements registry `docs/01_requirements_registry.md` (from `approved` → `implemented` → `tested` → `accepted`).
5. Run the full test suite to ensure all tests pass. Resolve any issues. Update **doc/test/test catalog.md**.
6. Update the:
    - docs/01_requirements_registry.md to reflect the current status.
    - doc/modules/MOD-<module>.md files to reflect actual implementation details.
