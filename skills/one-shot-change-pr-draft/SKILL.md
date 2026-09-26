---
name: one-shot-change-pr-draft
description: Chains a set of skills together that makes the specified change, then raises a PR for it in draft mode and checks CI.
---

1. Run the /one-shot-change skill to make the change.
2. Once all tests pass locally, run /pull-request to create a draft PR for the change
3. Once the PR is created, check CI status

## After making the change

Summarise to the user the steps taken, what the PR URL was.
If the work is an openspec change, remind the user they will need to archive the change.
