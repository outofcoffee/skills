---
name: archive-and-squash-merge
description: Chains a set of skills together that completes and archives a change then merges the PR on green checks.
---

This skill is designed to be used with the /one-shot-change family skills.

## Test check

First check if the tests are passing. If they are not, inform the user that you are unable to complete the change due to failing tests. Suggest how you can fix the tests in a reliable and robust way.

If the tests are passing, then follow these steps to complete the change:

### If the work is an openspec change

If the change is an openspec change, then:

1. Run /openspec-archive-change (with sync)
2. Run /commit-message and push

### If the work is not an openspec change

If the scope of the work is not an openspec change, then:

1. Check the plan file created by the /one-shot-change skill to determine if all the work has been completed. If not, inform the user of the remaining scope. Suggest how you can complete the work.

## Completing the change

1. Set the PR status to ready for review.
2. Run /pr-merge-on-green squash
3. Summarise to the user the steps taken, what the PR URL was.
