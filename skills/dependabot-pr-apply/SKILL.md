---
name: dependabot-pr-apply
description: Use this to cleanly apply open Dependabot pull requests (PRs) in GitHub
---
Ask the user which branch the changes should be applied to. Suggest `develop` if it exists, otherwise suggest `main`.

Run all tests before starting. If any tests already fail, stop and ask the user what to do.

## Discovering PRs

List open PRs authored by `app/dependabot`:
```
gh pr list --author app/dependabot --state open
```

Work through these PRs systematically and apply them to the target branch as clean commits. No merges. If multiple PRs upgrade the same dependency, apply only the highest version and skip the rest.

If a PR has conflicts with the target branch, stop and ask the user how to proceed.

## Committing

- No `Co-authored-by` trailers in commit messages.
- Clean commits on top of the target branch.

## Testing

- Run all tests, including e2e tests, after each change and before committing.
- All tests must pass before moving to the next PR.
