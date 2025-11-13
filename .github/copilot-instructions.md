# Documentation
Do not generate .md files if they are not asked directly.

# Function implementation
This section used when Prompt starts with "Implement function" only.
Use the following files for the work:
- ./specifications/functionality.md
- ./specifications/
Use next workflow for a function code implementation tasks:
- Identify function in the file ./specifications/functionality.md
- Implement the function as per the specifications mentioned in ./specifications/functionality.md
- Set status to "implemented" in ./specifications/functionality.md after completing the implementation
- Generate functional tests for the implemented function in ./frontend/src/test folder with the file name of the function being implemented followed by .test.ts or .test.tsx as applicable.
- Run all tests to ensure that the implementation is correct and all tests pass.
- If any test fails, debug and fix the implementation until all tests pass.
- Set status to "tested" in ./specifications/functionality.md after all tests pass successfully for the implemented function.
- Make commit with message "Implemented and tested <function name> function"



