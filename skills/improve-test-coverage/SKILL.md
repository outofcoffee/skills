---
name: improve-test-coverage
description: Improve test coverage by adding meaningful tests for core functionality, with coverage verification before and after changes
---

Analyse the project's core functionality and identify areas lacking test coverage. Focus on adding tests that verify important behaviours and edge cases, not just increasing coverage metrics for their own sake.

## Initial Assessment
- Identify the project's main purpose and core features
- Determine what testing framework and coverage tools are available (e.g., Jest, pytest, coverage.py, nyc, etc.)
- Run initial coverage report if possible to establish baseline
- Review existing tests to understand current coverage patterns

## Test Planning
- Prioritise testing core business logic, critical paths, and error handling
- Identify untested functions, methods, and components that are essential to the project's functionality
- Look for edge cases, boundary conditions, and failure scenarios that should be tested
- Avoid adding tests for trivial code (e.g., simple getters/setters unless they have important logic)

## Test Implementation
- Write unit tests for individual functions/methods
- Add integration tests for key workflows
- Include tests for error conditions and invalid inputs
- Ensure tests are readable and maintainable
- Follow the project's existing testing conventions and patterns
- Use British English spelling in all test names, comments, and documentation

## Coverage Verification
- Run coverage analysis after adding tests to verify improvement
- Compare before/after coverage reports if available
- Ensure new tests contribute to meaningful coverage of core functionality
- Remove or refactor any tests that don't add value

## Quality Checks
- All new tests must pass
- Tests should be fast and reliable
- Avoid flaky tests that could break CI/CD
- Document any test setup or mocking requirements

## Completion
- Provide summary of coverage improvements
- List the core functionality areas that were tested
- Suggest any remaining high-priority areas for future testing