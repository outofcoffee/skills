---
name: dependabot-pr-apply
description: Use this to cleanly apply open Dependabot pull requests (PRs) in GitHub
---
work through the open dependabot PRs and systematically apply them to develop as a clean commit - NO MERGES - testing as you go.

ask the user on which branch they should be merged into. suggest the 'develop' branch if it exists, otherwise, suggest 'main'.

run tests first before starting any merges. if any tests already fail - stop and ask the user what to do

## committing
- no 'co-authored-by' trailers to commit messages
- clean commits on top of the target branch

## testing
- run all tests including e2e tests, after each change is made, before committing
- tests need to pass

