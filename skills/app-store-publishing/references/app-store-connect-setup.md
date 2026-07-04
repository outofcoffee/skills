# App Store Connect setup

Getting from "I have an app" to "there's a record in App Store Connect I can upload builds to and edit a listing on."

## 1. Register the bundle ID

In the Apple Developer portal → Certificates, Identifiers & Profiles → Identifiers → register an **Explicit** App ID matching the app's bundle identifier (e.g. `ai.example.app`). No extra capabilities unless the app needs them. This must exist before the app record — the New App form only lists registered bundle IDs.

## 2. Create the app record (console, not API)

App Store Connect → **Apps → + → New App**. The API can't reliably create app *records*, so do this in the browser.

Fields, and what's permanent:

| Field | Notes |
|---|---|
| Platform(s) | iOS / macOS as needed |
| Name | Store display name (≤30 chars) — editable later |
| Primary language | editable later |
| **Bundle ID** | **permanent** |
| **SKU** | **permanent** — any unique string, e.g. `myapp-ios` |
| User access | Full Access unless restricting |

Because bundle ID and SKU are permanent, **show the filled form and get an explicit "yes" before clicking Create.**

The New App dialog opens the moment you click the `+` menu → New App. Note the numeric **Apple ID** the console assigns (e.g. `6785043473`) — scripts and API calls need it.

## 3. Account prerequisites that silently block creation

New-app creation can be hard-blocked by account state, surfaced as an unhelpful modal ("Your paid application agreement is outdated" / "Agreement Update"). Check **Business → Agreements** and the account banners. Common blockers:

- **Paid Apps Agreement** in "Pending User Info" — needs bank account + tax forms completed to activate. Even free apps can be gated behind acknowledging the current agreement.
- **Bank account** not on file.
- **Tax forms** incomplete.
- **EU trader status** (Digital Services Act) not declared — required to distribute in the EU.

**These are all the user's to complete** — they involve accepting legal agreements and entering **bank/tax/legal** details, which you must never do on their behalf. Surface exactly what's outstanding and hand it over. Free-only apps may only need the updated agreement *acknowledged*, not full banking — but that's still the user's click.

## 4. App Store Connect API keys — and the role trap

Users and Access → **Integrations → App Store Connect API → Team Keys → Generate API Key**. First use requests org-wide API access (a terms acceptance — **let the user click "Request Access"**).

You get: an **Issuer ID** (per-account UUID, shown above the table), a **Key ID** (per key), and a one-time-download **`AuthKey_<KeyID>.p8`**. Keys are immutable — you can't change a key's role after creation.

**The role trap (this cost a full CI cycle):**

| Task | Minimum role |
|---|---|
| Upload screenshots / edit metadata | **App Manager** |
| Cloud-create a **distribution** certificate (CI signing via `-allowProvisioningUpdates`) | **Admin** |

App Manager can cloud-create *development* certs — so the **archive** step passes — but the distribution **export** then fails with `Cloud signing permission error` / `No signing certificate "iOS Distribution" found`. If CI signing hits that, the fix is a new **Admin** key (you can't upgrade the old one). Generating an Admin key stores a broad credential — get the user's explicit OK, and note they can revoke it anytime.

**Downloading the `.p8`:** the download needs a real user click (browsers block script-triggered downloads), and macOS blocks tool access to `~/Downloads`. Ask the user to click Download, then **move the file somewhere readable** (e.g. a project `secrets/` dir) and give you the path + Key ID + Issuer ID. Never have the private key pasted into the conversation.

## 5. Editing the listing via the browser

Most listing fields are edited in the console (the API is used mainly for media upload and CI). When driving the browser:

- App Store Connect is an Ember app — set an input's `value` and dispatch `input` + `change` events; for buttons/menu items dispatch the full pointer/mouse sequence (`pointerdown, mousedown, pointerup, mouseup, click`).
- **Saves show a transient error banner even on success.** Don't trust it either way — reload the page and re-read the field to confirm what actually persisted.
- Sessions expire; if a page redirects to `login?...authResult=FAILED`, stop and ask the user to sign in again (never enter credentials).
