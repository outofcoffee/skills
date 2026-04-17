---
name: commit-message
description: Create a git commit following conventional commit format with imperative style and British English spelling
---

Create a git commit for the current staged and unstaged changes, following the rules below.

## Commit message format

- Use **conventional commit** format: `<type>[optional scope]: <description>`
  - Common types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`, `style`, `perf`, `build`
- Use **imperative mood** in the subject (e.g. `feat: add flux capacitor`, not `feat: added flux capacitor`)
- Do **not** end the subject line with a full stop
- Use **British English** spelling (e.g. `organise`, `colour`, `behaviour`, `initialise`)
- Do **not** include a `Co-Authored-By` trailer or reference the agent name

## Commit body

- Omit the body unless it is genuinely necessary to explain *why* the change was made or to clarify something non-obvious
- When a body is included, keep it brief and focused — do not replay the history of how the final change was reached

## Process

1. Run `git status` (never use `-uall`) and `git diff` to review all changes
2. Run `git log --oneline -5` to see recent commit style for context
3. Stage the relevant files (prefer naming files explicitly over `git add -A`)
4. Compose the commit message according to the rules above
5. Create the commit
6. Run `git status` to confirm success
