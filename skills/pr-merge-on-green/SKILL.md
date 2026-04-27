---
name: pr-merge-on-green
description: Wait for CI to pass on a GitHub pull request and then merge it
disable-model-invocation: true
---

Monitor CI on a GitHub pull request, wait for it to pass, then merge with the user's chosen strategy.

## Inputs

- The PR can be given as a number, URL, or branch name. If nothing is supplied, use the PR for the current branch (`gh pr view --json number`).
- If no PR can be resolved, stop and ask the user which PR to monitor.

## Process

### 1. Confirm the PR

Run `gh pr view <pr> --json number,title,headRefName,state,mergeable,isDraft` and show the user the PR title and number you are about to act on. Stop immediately if:
- The PR is closed or already merged (`state` is not `OPEN`).
- The PR is a draft (`isDraft` is `true`) — ask the user whether to mark it ready or abort.

### 2. Ask for the merge strategy

Before starting the watch, ask the user to choose between:
- **squash** — single conventional-commit-formatted commit, no body
- **rebase** — replay the PR's commits onto the base branch as-is

Do not assume a default. Wait for the user's answer.

If **squash** is chosen, also confirm the commit subject up front (see "Squash commit message" below) so the merge can proceed without further interruption once CI is green.

### 3. Watch CI

Run:

```
gh pr checks <pr> --watch --fail-fast
```

This blocks until all checks finish and exits non-zero on the first failure.

- If the command exits **0**: all required checks passed → continue to merge.
- If it exits **non-zero**: a check failed or was cancelled. Stop, report which check failed (`gh pr checks <pr>` for the summary), and do **not** merge.
- If there are no checks configured at all, stop and ask the user whether to merge anyway.

For long waits, prefer running the watch command with `run_in_background: true` so the conversation is not blocked, and report back when it finishes.

### 4. Merge

Use `gh pr merge` with the chosen strategy.

#### Squash

```
gh pr merge <pr> --squash --subject "<conventional commit subject>" --body ""
```

Squash commit message rules:
- Use **conventional commit** format: `<type>[optional scope]: <description>`
  - Common types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`, `style`, `perf`, `build`
- Use **imperative mood** (e.g. `feat: add flux capacitor`, not `feat: added flux capacitor`)
- Do **not** end with a full stop
- Use **British English** spelling (e.g. `organise`, `colour`, `behaviour`)
- **No commit body** — pass `--body ""` to suppress GitHub's default body
- Do **not** include a `Co-Authored-By` trailer or agent attribution

If the PR title already follows conventional commit format, reuse it; otherwise compose a subject from the PR title and changes and confirm it with the user before merging.

#### Rebase

```
gh pr merge <pr> --rebase
```

The PR's existing commits are replayed onto the base branch unchanged. Do not rewrite commit messages.

### 5. Confirm

After merging, run `gh pr view <pr> --json state,mergedAt` and report the result to the user.

## Failure handling

- **CI failed**: do not merge; surface the failing check name(s) and a link via `gh pr checks <pr>`.
- **Merge conflict reported by GitHub**: stop and ask the user how to proceed; do not attempt to resolve conflicts as part of this skill.
- **Branch protection blocks the merge** (e.g. requires up-to-date branch, missing approvals): stop, report the reason, and ask the user how to proceed.
