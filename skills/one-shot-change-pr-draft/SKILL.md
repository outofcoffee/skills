---
name: one-shot-change-pr-draft
description: Chains a set of skills together that makes the specified change, then raises a PR for it in draft mode and checks CI.
---

If the user has not specified what the scope of the work is, do not assume - ask the user explicitly.

Once you understand the scope of the work, follow this approach:

### If the work is an openspec change

If the user is asking for an openspec change, then this is the section to follow. If it is ambiguous whether the user has asked for a "change" then confirm with the user if they meant an openspec change or not.

1. Run /openspec-propose for the change
2. Once the proposal is complete, run /commit-message
3. Run /openspec-apply-change
4. Run /commit-message
5. Run /improve-test-coverage for the change
6. Run /docs-update for the change
7. Once all tests pass locally, run /pull-request to create a draft PR for the change
8. Once the PR is created, check CI status

### If the work is not an openspec change

If the scope of the work is not an openspec change, then we should first perform these safety checks:

1. Does the scope of the change actually touch any specs?
2. If so, stop and confirm with the user before proceding whether they really want to skip making this an OpenSpec change.

Once you have performed the safety checks above, if EITHER the work scope does not touch a spec OR the user still wishes to proceed without running the OpenSpec change process follow these steps:

1. Write the scope of the work to a plan file, in markdown format, within the repository. Include: purpose of change, goals/non-goals, high level tech design, and how to verify the change. The plan file should not be committed as part of this work.
2. Implement the work using the plan file.
3. Run /commit-message, but exclude the plan file.
4. Run /improve-test-coverage for the scope of the work
5. Once all tests pass locally, run /pull-request to create a draft PR for the change
6. Once the PR is created, check CI status

## After making the change

Summarise to the user the steps taken, what the PR URL was.
If the work is an openspec change, remind the user they will need to archive the change.
