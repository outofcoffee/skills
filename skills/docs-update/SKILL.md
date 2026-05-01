---
name: docs-update
description: Update the root README.md and files in the docs directory to reflect the current state of the project, keeping each document aligned with its intended audience
---

Bring the project's documentation back in line with the current state of the code. Cover the root `README.md` and every file in the `docs/` directory (recursively). Each document has a job — do not blur them together.

## Scope

- Root `README.md`
- All Markdown files under `docs/` (recurse into subdirectories)
- Do **not** edit other docs (e.g. `CONTRIBUTING.md`, `CHANGELOG.md`, inline code comments) unless the user explicitly asks

## README.md — user-facing, punchy, fun

The root README is the product's front door. It is for **users**, not maintainers. It explains **how to use the product**, not how it works internally.

Rules:

- **Audience is the user.** Someone who wants to install it, run it, and get value from it.
- **No implementation details.** No internal architecture, no module breakdowns, no class diagrams, no "how the parser works". If the reader does not need it to *use* the project, leave it out.
- **Punchy.** Short sentences. Short sections. Cut filler. If a paragraph can be a bullet, make it a bullet. If a bullet can be a sentence fragment, trim it.
- **Tonally fun.** Keep it light and human. A bit of personality is good — dry humour, a wink, a memorable phrase. Do not be cute to the point of unclear, and do not pad with jokes. Fun ≠ verbose.
- **Useful first.** The reader should be able to install and run the thing within seconds of opening the file. Lead with what it is and how to start, not with badges or backstory.
- **British English** spelling throughout (`organise`, `colour`, `behaviour`).
- **No agent attribution.** Do not mention that the docs were updated by an AI, agent, or tool.

A good README usually has, in roughly this order:

1. One-line description of what the project is and why someone would want it
2. Quick install / quickstart that actually works when copy-pasted
3. The most common usage examples
4. Pointers to the `docs/` directory for anything deeper

Cut anything that does not earn its place.

## docs/ directory — match each file's audience

Files under `docs/` vary. Some are written for **users** (tutorials, guides, reference, FAQ). Some are written for **maintainers** (architecture notes, design decisions, contributor setup, release process, internal runbooks). A few are mixed.

For each file:

1. **Identify the audience** from the existing content, filename, and surrounding directory. Signals:
   - User-facing: "getting started", "guide", "tutorial", "usage", "reference", "FAQ", "examples", instructions written in second person ("you run…")
   - Maintainer-facing: "architecture", "design", "internals", "contributing", "release", "ADR", "RFC", references to internal modules, class names, build pipelines, deploy steps
2. **Identify the existing style and level of detail.** Tone, formality, depth, code-example density, use of diagrams, headings depth. Do not flatten different documents into a single house style — preserve each one's character.
3. **Update in place.** Bring it up to date with the current code, commands, flags, file paths, version numbers, and behaviour. Keep the audience and style consistent with what was there.
4. **Do not retarget a document.** If a doc was written for maintainers, do not rewrite it for users (or vice versa) just because you are touching it. If the audience genuinely seems wrong, flag it to the user rather than silently changing it.

Cross-document rules:

- British English spelling throughout
- No agent attribution anywhere
- Fix broken internal links and stale references as you go
- Remove sections that describe removed features; add short sections for new features that warrant documentation at that file's level of detail

## Process

1. Read the root `README.md` and list every Markdown file under `docs/` (recurse).
2. Skim the codebase enough to know what the project currently does — entry points, public API, CLI, config, install path, supported platforms. Note anything the docs claim that is no longer true.
3. Rewrite/refresh `README.md` against the user-facing rules above. Be ruthless about cutting implementation detail.
4. For each file in `docs/`:
   a. Classify the audience (user / maintainer / mixed).
   b. Note its existing tone and depth.
   c. Update the content to match current reality, staying within that audience and style.
5. Re-read each updated file end-to-end to check it still flows and that nothing now contradicts the README or another doc.
6. Summarise the changes for the user: which files changed and the headline reason for each.
