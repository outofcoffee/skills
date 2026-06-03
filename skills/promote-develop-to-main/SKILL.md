—
name: promote-develop-to-main
description: Promote the develop branch to main, using specific rules
—

# End goal

We want the main branch to be stable and up to date with changes in the develop branch. To achieve this, we first will ensure develop is a superset of main, then ensure all its tests and checks pass. Once we confirm develop is stable, we will merge develop into main using the `—ff-only` strategy. We should then check that the tests pass on the main branch.

# Process

1. Hard reset the local main branch to origin/main
2. Update the local develop branch to origin/develop
3. Rebase the local develop branch onto the local main branch
4. Push the local develop branch to origin
5. Monitor CI to see if all tests and checks pass
6. If any tests or checks do not pass, do not dismiss them as ‘pre-existing’ or ‘not related to my changes’ - you should abort and report back to the user
7. If all tests and checks pass, merge the local develop branch into the local main branch using the `—ff-only` strategy. No merge commits. Clean fast-forward only.
8. Push the local main branch to origin
9. Monitor CI to see if all tests and checks pass
10. Report the outcome to the user
