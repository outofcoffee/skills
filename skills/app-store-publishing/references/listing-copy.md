# Listing copy

Writing the App Store text: name, subtitle, promotional text, description, keywords, URLs.

## Character limits

| Field | Limit | Notes |
|---|---|---|
| Name | 30 | display name + brief descriptor |
| Subtitle | 30 | complements the name; don't repeat it |
| Promotional text | 170 | editable without a new app version |
| Keywords | 100 | comma-separated, **no spaces** (spaces waste characters) |
| Description | 4000 | plain text — App Store does **not** render Markdown |

Always count before entering, and verify the on-screen "characters remaining" after — the browser can pick up a stray character.

## Name + subtitle: pack the value, don't duplicate

- **Name = `AppName: brief descriptor`.** Words in the Name *and* Subtitle are indexed for App Store search, so the descriptor pulls double duty (clarity + discoverability). Because of that indexing, **don't** also spend keyword-field characters on words already in the name/subtitle.
- Make the name/subtitle **accurate**, not just catchy. "Client" beat "Chat" for an app that connects to the user's own backends rather than being a standalone chatbot — accuracy matched what the app actually is. Small wording choices like this are worth surfacing to the user.
- Name the **headline integrations/partners** if they fit and they're search terms (e.g. specific gateways/services) — good for both meaning and search.
- Spread the top features across name + subtitle so together they cover the strongest 3–4 (e.g. category, the unique angle, multi-X, bring-your-own-X).

Example progression from a real listing (each ≤30):
`Lucinate: Terminal AI Client` / `OpenClaw, Hermes, any agent`.

## Description

Lead with the hook, then structure with UPPERCASE section headers (no Markdown) and `•` bullets. A working shape:

1. One-line hook — what it is + why you'd want it.
2. A short paragraph on the core experience.
3. `SECTION HEADER` + bullets for the feature groups.
4. An honest "REQUIRES …" section if the app depends on an external service/account — this sets expectations and helps App Review.
5. A closing line (open-source, pricing, link).

Source the voice from the product's own marketing (website/landing copy) so the store reads consistently — but trim to App Store length and drop web-only flourishes.

## Keywords

Comma-separated, no spaces, ≤100 chars. Include category terms, competitor/adjacent names, and specific technologies — but not words already in the Name/Subtitle (Apple already indexes those). Re-optimise when you move a term into the name/subtitle.

## URLs

- **Support URL** (required) — a real help destination (site, or a repo's issues/discussions).
- **Marketing URL** (optional) — the product site.
- **Privacy Policy URL** (required) — see [privacy.md](privacy.md).

## Keep the source of truth in the repo

App Store Connect fields don't diff, review, or back up well — the repo copy is the source of truth and every live edit mirrors back to it. Two artifacts, two jobs:

- **`fastlane/metadata/`** (the standard `deliver` layout: one file per field, `en-GB/description.txt` etc.) — the **machine-readable** copy that CI actually pushes to ASC via the lanes in [../templates/Fastfile](../templates/Fastfile). Once this exists, *edit these files, never the console*. See [submission-review.md](submission-review.md) for the push/submit lanes.
- **[`app-store/listing.md`](../templates/listing.md)** — the human notes `deliver` can't carry: identifiers (Apple ID, SKU), copy rationale and character counts, and the checklist of human-only attestations (App Privacy publish, Age Rating, Content Rights).

Consistency across these surfaces is itself a review axis: a description claiming "free" on a paid app, or listing text contradicting the age rating, is a rejection on its own (see [submission-review.md](submission-review.md)).

## App-level vs version-level fields

- **App Information** (app-level, editable anytime — even while live or in review): Name, Subtitle, Categories, Content Rights, Privacy Policy URL.
- **Version** (per-version, needs an *editable* App Store version): Promotional text, Description, Keywords, Support URL, Marketing URL, Copyright, What's New, Screenshots.

Set the **Primary/Secondary Category** on App Information — it isn't asked at app creation and is required for submission.
