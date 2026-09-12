---
name: one-shot-change-pr-merge
description: Chains a set of skills together that makes the specified change, then raises a PR for it then merges the PR on green checks.
---

1. Run the /one-shot-change-pr-draft skill to make the change and raise a draft PR for it.
2. Once the draft PR is created, check CI status.
3. If the tests are failing, attempt to fix the tests and push the changes to the PR branch. If you are unable to fix the tests, inform the user that you are unable to merge the PR due to failing tests.
4. If the tests are passing, run /openspec-archive-change (with sync), then /commit-message and push
5. Set the PR status to ready for review.
6. Run /pr-merge-on-green squash

## After making the change

Summarise to the user the steps taken, what the PR URL was.
