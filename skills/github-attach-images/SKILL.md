---
name: github-attach-images
description: Get screenshots, images and videos to actually render inside GitHub issues, pull requests and comments, uploaded straight from the command line with the GitHub CLI's repeatable --attach flag — inline Markdown embedding, alt text, before/after evidence in a PR, bug-repro screenshots, format and size limits, and fallbacks for older gh versions or repositories without upload access. Use whenever an agent has an image or video a reviewer should see on GitHub — "attach the screenshot", "show a before/after", "post proof it works", "embed this recording", or any time you are about to paste a local file path into an issue or PR body — even if the user doesn't mention gh or the word "attach".
---

# Attaching images to GitHub issues and pull requests

A screenshot sitting on your local disk tells the reviewer nothing, and a local path pasted into an
issue body renders as a broken image for everyone but you. Upload the file and let GitHub render it.
Since **gh v2.99.0** the GitHub CLI has a repeatable `--attach` flag that uploads a local image or
video and writes the resulting URL into the body of the issue, pull request or comment being
created or edited — one command, rendered inline, exactly as if it had been dragged into the browser.

## Requirements

- `gh --version` ≥ 2.99.0. If older, `gh upgrade` (or `brew upgrade gh`) first — the rest of this
  skill assumes the flag exists.
- **Push (write) access to the repository.** Uploads ride on the same credentials gh already uses
  (`gh auth login` token or `GH_TOKEN`), and GitHub only accepts media from people who can write to
  the repo.
- GitHub.com and GitHub Enterprise Cloud. GitHub Enterprise Server did not support `--attach` as of
  its release — use the fallbacks at the bottom if uploads fail there.

## The core pattern

`--attach` is available on every command that writes a Markdown body:
`gh issue create`, `gh issue edit`, `gh issue comment`, `gh pr create`, `gh pr edit`, `gh pr comment`.

```sh
# File the bug with its screenshot in one command
gh issue create --title "Login spinner never settles on error" \
  --body "Seen every time credentials are wrong:" \
  --attach ./login-error.png#The login form stuck on its loading spinner

# Attach to an existing issue or PR afterwards
gh pr comment 456 --attach ./repro.mov
```

Repeat the flag for more than one file (`--attach ./a.png --attach ./b.png`), up to 50 files per
command, but never the *same* file twice in one command.

### Alt text

Add alt text after a `#` on the path (quote the argument so the shell doesn't eat it):

```sh
gh issue comment 123 --attach './before.png#Settings screen with the dark-mode toggle off'
```

Omit it and gh falls back to the filename — fine for `after.png`, useless for
`Screenshot 2026-10-24 at 11.02.45.png`. Alt text describes the image for screen readers and for
readers when the image fails to load, so give every content-bearing image real alt text; a
filename-derived fallback is not a substitute. Alt text is not supported on video files.

## Embed inline, don't append

If the body text already references the local path you attach, gh **rewrites that reference in
place** — the Markdown and its alt text are kept, and no second copy is appended. Any attached file
the body does *not* reference is appended to the end of the body, in flag order, which usually reads
badly. So write the body first with ordinary local image links, then attach the same paths:

```sh
cat > body.md <<'MD'
## Before / after

Before the fix, the login spinner never settled:

![Login form stuck on its loading spinner](./before.png)

After, it shows the validation error immediately:

![Login form showing the "invalid credentials" error](./after.png)
MD

gh pr create --title "fix: settle login spinner on error response" \
  --body-file body.md \
  --attach ./before.png --attach ./after.png
```

This also means you can write and locally preview a body file whose images render from disk, then
post it unchanged. Two details worth knowing:

- The reference is rewritten wherever the body comes from — `--body`, `--body-file`, stdin, or the
  editor.
- For a rewritten reference the alt text comes from the Markdown; the `#` alt text on the flag only
  applies to files that get appended.

### Videos

To embed a video as a playable player rather than a link, the reference `![](./demo.mp4)` must be
the **only content in its paragraph**. Inside a sentence it degrades to a plain link.

## Formats and size limits

- Supported: PNG, JPEG, GIF, WebP, SVG, MP4, MOV, WebM. Only images and media — a log file or
  archive cannot be attached this way; commit those or paste excerpts as text.
- 10 MB per image or GIF; videos 10 MB on Free plans, 100 MB on paid plans.

Check before attaching (`ls -lh ./screenshot*.png`) — a full-resolution retina screenshot can slip
over 10 MB. Shrink images with `sips --resampleWidth 1600 file.png` (macOS) and re-record or trim
videos rather than retrying an upload that will be rejected.

## Gotchas and recovery

- **Don't blind-retry a failed `gh pr create`.** Uploads normally happen before the PR is created,
  but if the command fails part-way, check `gh pr view` / `gh pr list --head "$(git branch
  --show-current)"` before retrying so you don't file a duplicate PR. When in doubt, create the PR
  plain and add the media afterwards with `gh pr comment N --attach ./shot.png`.
- **Paths must match.** The in-place rewrite matches the body's `![](./x.png)` against the path you
  passed to `--attach`. Use the same spelling in both, or the image gets appended at the end
  instead of embedded where you wrote it.
- **Screenshots from tools:** have the browser/simulator tool save into a dedicated directory (e.g.
  `$(mktemp -d)`) and pass those paths — don't scrape the file back out of tool output.

## Fallbacks when `--attach` isn't available

1. **Old gh** — `gh upgrade`. Do not hand-roll uploads against undocumented web endpoints.
2. **Enterprise Server, or an API-only path without media support** — commit the image to the PR
   branch (e.g. `docs/images/fix-login/before.png`) and reference its raw URL in the body:
   `https://raw.githubusercontent.com/OWNER/REPO/BRANCH/path/to/image.png`. It renders, but the
   binary lives in git history forever — keep such images small and few.
3. **No write access at all** — GitHub will refuse uploads from your token no matter the method.
   Say so in the issue body (reference the file path and describe what it shows) and ask a
   collaborator with write access to attach it, or note it in the PR for the human who will merge
   and comment.
