# Privacy

Two required pieces: a **Privacy Policy URL** and the **App Privacy data questionnaire**. Both live under App Store Connect → App Privacy.

## Privacy Policy URL (required)

Apple requires a reachable privacy-policy page before submission. If the product has no privacy page yet:

1. **Draft one** honestly from what the app actually does. For a client that stores everything on-device and collects nothing, the policy is short and true — see [../templates/privacy-policy.md](../templates/privacy-policy.md). Align it with the app's `PrivacyInfo.xcprivacy` (same "no tracking / no data collected" story, same required-reason APIs).
2. **Host it** — a `/privacy` route on the marketing site is cleanest. Add the page to the site repo; it must be **deployed** (resolving) before submission, though you can enter the URL in the draft listing before it's live.
3. Enter the URL under App Privacy → Privacy Policy → Edit.

## App Privacy data questionnaire

App Privacy → **Get Started** → "Do you or your third-party partners collect data from this app?"

- If the app has **no analytics, no tracking, no third-party data-collection SDKs**, and only sends data to a service the *user* configured (to service their own request, not for you to collect), the honest answer is **"No, we do not collect data."** This matches a `PrivacyInfo.xcprivacy` with `NSPrivacyTracking = false` and no collected data types.
- If it does collect anything, answer Yes and complete the data-type breakdown truthfully.

### Stop before Publish (attestation)

Saving the answer is fine. The final **Publish** step makes you *agree the responses are accurate and legally compliant* — that's a legal attestation. **Fill in the factual answer, then hand the Publish click to the user.** Same rule for Age Rating and Content Rights: pre-fill the factual selections if asked, but the user owns the attestation.

## Required-reason APIs

The app's privacy manifest (`PrivacyInfo.xcprivacy`) must declare the system APIs it (or its runtime) uses for approved reasons — commonly file timestamps, `UserDefaults`, and system boot time. Apple validates this at upload; a missing/incomplete manifest triggers a warning email and eventually a rejection. Keep the manifest and the written policy consistent.
