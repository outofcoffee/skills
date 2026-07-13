---
name: app-store-publishing
description: Publish an iOS/macOS app to the App Store and TestFlight end to end — create the App Store Connect record, write listing copy (name, subtitle, description, keywords) within Apple's limits, draft a privacy policy and answer the data questionnaire, capture bare screenshots from the simulator and upload them via the App Store Connect API, wire up a tag-triggered TestFlight build in GitHub Actions, set pricing, and submit for review via the API — including recovering from a rejection (resubmission, review-note answers for data-practice and face-data questions). Use when releasing an app, editing its store listing/metadata, generating or uploading screenshots, setting up App Store Connect API signing/upload, submitting or resubmitting for review, or responding to App Review. Bundles a screenshot-uploader script, CI/export/listing/privacy templates, and the hard-won gotchas.
---

Publish an app to the App Store / TestFlight, and everything around the listing. This skill captures a full, working run: what the phases are, which parts a human must do, and the concrete gotchas that each cost real time to discover.

## The phases

Work them in this order; each has a deep-dive reference file — read the one you're on rather than loading everything.

1. **App Store Connect setup** → [references/app-store-connect-setup.md](references/app-store-connect-setup.md)
   The app record, the account prerequisites that silently block it, and the API keys (with the crucial role distinction).
2. **TestFlight CI** → [references/testflight-ci.md](references/testflight-ci.md)
   A tag-triggered GitHub Actions build that signs with an API key and uploads to TestFlight. Template: [templates/testflight.yml](templates/testflight.yml).
3. **Listing copy** → [references/listing-copy.md](references/listing-copy.md)
   Name, subtitle, description, keywords — the character limits, the search-indexing rules, and how to write it. Master-copy template: [templates/listing.md](templates/listing.md).
4. **Privacy** → [references/privacy.md](references/privacy.md)
   The required privacy-policy URL and the App Privacy data questionnaire. Template: [templates/privacy-policy.md](templates/privacy-policy.md).
5. **Screenshots** → [references/screenshots.md](references/screenshots.md)
   Capture bare shots from the simulator (staging realistic data), then upload via the API with [scripts/upload_screenshots.py](scripts/upload_screenshots.py).
6. **Submission, pricing & review** → [references/submission-review.md](references/submission-review.md)
   Attach a build to the version, set the price, submit via the API — and the rejection playbook: resubmitting (thread replies alone restart nothing), pre-empting the data-practice/face-data questions, and the Kids Category trap.

You rarely do all six in one sitting. Identify which the user is asking for and go straight there.

## Cross-cutting rules (apply throughout)

- **Never do the human-only steps.** Do not enter Apple ID credentials, and do not accept legal agreements or attestations on the user's behalf: the Paid Apps Agreement, the App Privacy *Publish* confirmation, Age Rating, Content Rights, EU trader status, tax forms, or bank details. Fill in the *factual* draft fields, then stop and hand these to the user with a clear explanation of what's being attested.
- **Confirm irreversible/outward actions first.** Creating the app record fixes the **bundle ID and SKU permanently**; clicking **Create**, **Submit**, or **Publish** is a commitment. Show the filled form and get a yes.
- **Keep a master copy of the listing text in the repo** (e.g. an `app-store/` dir), and mirror every live edit back to it. App Store Connect fields don't diff or review well; the repo copy is the source of truth. See [templates/listing.md](templates/listing.md).
- **Secrets stay out of the transcript.** Take the API key `.p8` as a file path, not pasted text. Scripts read it from a path / env var. Never print private keys.
- **Verify saves.** App Store Connect often shows a transient "Sorry, something went wrong" banner on save even when it succeeded — reload the page and re-read the field to confirm, rather than trusting the banner either way.
- **Browsers can't be fully driven.** File-pickers (screenshot upload) and OAuth/login can't be automated. Use the App Store Connect **API** for uploads; hand login and file-drag to the user if no API path exists.

## Quick reference

**Listing character limits**

| Field | Limit |
|---|---|
| Name | 30 |
| Subtitle | 30 |
| Promotional text | 170 |
| Keywords (comma-separated, no spaces) | 100 |
| Description | 4000 |

Words in the **Name** and **Subtitle** are indexed for App Store search — don't waste keyword-field characters repeating them.

**Screenshot sizes (portrait; the simulator's native resolution *is* the required size)**

| Device class | Simulator | Size | API display type |
|---|---|---|---|
| iPhone 6.9" | iPhone 17 Pro Max | 1320×2868 | `APP_IPHONE_67` |
| iPad 13" | iPad Pro 13-inch | 2064×2752 | `APP_IPAD_PRO_3GEN_129` (verify) |

**The greatest-hits gotchas** (details in the references):

- **Signing:** cloud-creating a *distribution* certificate via `-allowProvisioningUpdates` needs an **Admin**-role API key. App Manager can only cloud-create *development* certs (archive passes, distribution export fails with "Cloud signing permission error"). App Manager *is* enough for uploading screenshots/metadata.
- **SDK:** App Store Connect rejects uploads not built with the **iOS 26 SDK** — run the release job on the **`macos-26`** runner (default `macos-latest` still ships Xcode 16).
- **Simulators drift:** don't hard-code `name=iPhone 16` in CI test destinations; discover an available simulator by UDID at runtime.
- **ASC API auth:** the JWT is ES256 and the signature must be **raw `R||S` (64 bytes), not DER**.
- **Screenshot upload:** reserve (`POST /v1/appScreenshots`) → PUT the bytes from `uploadOperations` → commit (`PATCH` with `uploaded:true` + MD5 `sourceFileChecksum`) → poll `assetDeliveryState` to `COMPLETE`.
- **App creation via API is unreliable** — create the app *record* in the console; the API is fine for everything after.
- **Simulator text input:** the computer-use `type` action garbles into iOS text fields. Set the **Mac** clipboard (`pbcopy` — the Simulator auto-syncs it) and paste with Cmd+V.
- **Icons via XcodeGen:** there is no `resources:` key — assets must be listed under `sources:`, or the asset catalog silently isn't compiled and the icon goes missing.
- **Export compliance:** set `ITSAppUsesNonExemptEncryption` = `NO` in Info.plist, or every TestFlight build stalls on a manual encryption question.
- **Rejections don't resume from the Messages thread.** Answering App Review in the thread leaves the submission in `UNRESOLVED_ISSUES` forever; the stuck submission is immutable — **cancel it and create a fresh one** (the version becomes editable again: rename it and attach the newest build rather than resubmitting the stale one).
- **Pre-empt review questions in the notes:** camera apps get the face-data questionnaire even with zero face processing (listing the TrueDepth camera for front-camera selection is enough) — answer data-practices and face-data up front in `appStoreReviewDetail.notes`.
- **Consistency is a rejection axis:** a "Free to use" description on a paid app, or a `kidsAgeBand` set while telling review it's not a Kids app — every surface (price, listing, age rating, review replies, privacy declarations) must tell one story.

## Templates and scripts

- [templates/testflight.yml](templates/testflight.yml) — the CI workflow.
- [templates/export-options-appstore.plist](templates/export-options-appstore.plist) — App Store export options.
- [templates/listing.md](templates/listing.md) — master-copy for the listing text.
- [templates/privacy-policy.md](templates/privacy-policy.md) — a no-data-collection privacy policy.
- [scripts/upload_screenshots.py](scripts/upload_screenshots.py) — screenshot uploader (only needs `cryptography`).
