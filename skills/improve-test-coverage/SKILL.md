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
- When the work is scoped to a branch or diff, make the baseline per-function over the changed functions rather than a whole-repo report — across a large project the repo-wide number is noise you scroll past

## Trace the Callers of What Changed

Do this before writing any test, whenever the work is scoped to a diff or branch.

- List every caller of each changed function (grep, call hierarchy, IDE/LSP references)
- For each caller, ask the question coverage cannot: **can it skip the changed code entirely?** A precondition check, an early return, a cached result, a feature flag
- Test through each caller's public entry point, not just the changed function

Coverage of a function is not coverage of the paths that reach it. A function can sit at 100% while a caller silently declines to call it — and that caller is where a defect hides, because from the changed function's point of view the missing path does not exist.

## Test Planning
- Prioritise testing core business logic, critical paths, and error handling
- Identify untested functions, methods, and components that are essential to the project's functionality
- Look for edge cases, boundary conditions, and failure scenarios that should be tested
- Look for guards that pre-empt the code under test: callers that check "does this file exist / is this set / did we already do this" *before* delegating. When a change teaches shared code to handle a new input, these guards are where that input gets silently dropped — and the changed function's coverage stays green throughout
- Avoid adding tests for trivial code (e.g., simple getters/setters unless they have important logic)

## Test Implementation
- Write unit tests for individual functions/methods
- Add integration tests for key workflows
- Include tests for error conditions and invalid inputs
- Assert the claim, including the negative. Turn each normative claim into an assertion — specs, SHALL wording, promises made in commit messages ("fails loudly rather than falling back") — and assert the *wrong* path did not happen, not merely that something failed. Check the fallback's message is absent, not just that an error is present: a test that only asserts "an error" passes for the wrong reason
- Ensure tests are readable and maintainable
- Follow the project's existing testing conventions and patterns
- Use British English spelling in all test names, comments, and documentation

## Coverage Verification
- Run coverage analysis after adding tests to verify improvement
- Compare before/after coverage reports if available
- Treat a changed function at 100% statement coverage as the start of the check, not the end — prefer branch thinking and the caller list over the percentage
- Ensure new tests contribute to meaningful coverage of core functionality
- Remove or refactor any tests that don't add value. Where a test adds no coverage, say so plainly and justify it on other grounds (pinning a previously unasserted error message, say) or drop it

## Quality Checks
- All new tests must pass
- Tests should be fast and reliable
- Avoid flaky tests that could break CI/CD
- Document any test setup or mocking requirements

## Completion
- Provide summary of coverage improvements
- List the core functionality areas that were tested
- Suggest any remaining high-priority areas for future testing