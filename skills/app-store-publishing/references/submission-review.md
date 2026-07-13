# Submission, pricing, and review

From "listing is ready" to "app in the review queue" — and what to do when Apple rejects it. Everything here is API-driven (no browser needed); the whole submit and resubmit lifecycle is four small calls.

## Builds vs versions (the two-tabs confusion)

Every uploaded build lands in the **TestFlight** pool automatically. The **Distribution / App Store** tab is not a build list — it shows *versions*, and a version carries exactly **one** attached build that you choose. A build never appears under Distribution until it's attached, and a version only ever surfaces its single attached build.

- The version's `versionString` must equal the build's marketing version (`1.0` vs a `1.0.0` build blocks submission — `PATCH /v1/appStoreVersions/{id}` to fix).
- A build is attachable once `processingState: VALID` **and** export compliance is resolved.
- A just-uploaded build may not show under `/v1/apps/{id}/builds` yet; `/v1/builds?filter[app]={id}&sort=-uploadedDate` is more current.

## Export compliance: declare it in the build

Add to Info.plist so every build answers the encryption question at archive time instead of stalling in TestFlight waiting for a manual answer:

```xml
<key>ITSAppUsesNonExemptEncryption</key>
<false/>
```

`NO` is correct for apps using only standard OS crypto/HTTPS. Takes effect from the *next* build — already-uploaded builds keep whatever they answered.

## Pricing

- Price points per app: `GET /v1/apps/{id}/appPricePoints?filter[territory]=USA` → find the tier (e.g. `2.99`), then `POST /v1/appPriceSchedules` with the app, `baseTerritory` (e.g. USA) and one `manualPrices` entry referencing the price-point id (use a `${placeholder}` temp id in `included`). Apple equalizes all other territories from the base.
- A `201` here doubles as proof the **Paid Applications Agreement is active** — an inactive agreement is rejected at this call.
- **Free → paid is allowed any time** (change or schedule it; no resubmission needed). The catch: anyone who downloaded while free keeps it free forever, updates included — you can't retroactively charge. So "launch free for reviews, flip to paid" spends the whole free-window cohort as marketing, not deferred revenue.
- **When the price changes, sweep the listing text.** A description saying "Free to use" on a paid app is a Guideline 2.3 (accurate metadata) rejection waiting to happen.

## Submitting via the API

```
1. PATCH /v1/appStoreVersions/{vid}/relationships/build   {"data":{"type":"builds","id":<buildId>}}
2. POST  /v1/reviewSubmissions                             {platform: IOS, relationships.app}
3. POST  /v1/reviewSubmissionItems                         {relationships: reviewSubmission + appStoreVersion}
4. PATCH /v1/reviewSubmissions/{sid}                       {"attributes":{"submitted":true}}
```

Step 4 succeeding (state `WAITING_FOR_REVIEW`) is also your verification that every required piece was in place — Apple validates App Privacy publication, age rating, screenshots, etc. at submit time and rejects the call naming what's missing. Typical review turnaround: 24–48h, `WAITING_FOR_REVIEW → IN_REVIEW →` approved/rejected. Check the version's release option (auto vs manual) *before* approval if the user wants to control the go-live moment.

## Rejection: Guideline 2.1 "Information Needed" (the nine-day lesson)

- **A Messages-thread reply does NOT restart review.** The submission sits in `UNRESOLVED_ISSUES` indefinitely, with Apple waiting on you. Post the answers in the thread *and* resubmit.
- **The stuck submission is immutable.** Its `REJECTED` item can't be deleted (`409: Item was already submitted`) and no items can be added. The ASC UI shows the same dead end as a disabled Resubmit button. The path: `PATCH` the old submission with `canceled: true`, then create a **fresh** submission (steps 2–4 above).
- Right after cancelling, the item-add on the new submission can `409` with "not in valid state" — propagation lag, not a real failure. Retry once.
- **A rejected version becomes editable again** (`PREPARE_FOR_SUBMISSION` on edit). By rejection time you're usually several releases ahead — rename `versionString` to the current release and attach the **newest** build rather than resubmitting the stale one.
- Replies/notes: plain text (ASC renders no Markdown), under 4000 chars. Keep the draft in the repo (`app-store/`) like everything else.

## Pre-empting the questions (camera/photo apps especially)

Put the answers in `appStoreReviewDetail.notes` **before** the reviewer has to ask; each 2.1 round-trip costs days.

- **Data practices (Guidelines 1.3/5.1):** state outright whether there's third-party analytics / advertising / SDKs, what network connections exist, where user data lives, and list the required-reason APIs with their reason codes (e.g. UserDefaults → `CA92.1`, file timestamps → `C617.1`). Say explicitly that it matches the App Privacy declaration and privacy manifest.
- **Face data:** any app that touches the camera can get the face-data questionnaire (collected? purpose? sharing? retention? where in the policy?). If the app uses none, say so explicitly — no Vision/ARKit/CoreML/CIDetector imports, decorations placed manually — and note that merely listing the front **TrueDepth** camera in device discovery (to pick the front camera) is enough to trigger the question. Add a face-data section to the hosted privacy policy and quote it in the reply.
- **Explain any PIN or gate:** a local deletion PIN reads like an account or parental gate to a reviewer — say what it is and isn't.
- Review-contact phone must be international format (`+44 …`); a national number 409s the `appStoreReviewDetails` write.

## Kids Category: don't drift into it

Setting a `kidsAgeBand` on the age-rating declaration enrols the app in the **Kids Category** — parental-gate requirements, third-party-code restrictions, and extra review scrutiny. For a family-friendly-but-general app, leave the band unset (plain 4+ rating). Whichever you choose, every surface must tell the same story: age rating, review notes, thread replies, and listing. A "not a Kids app" reply while `kidsAgeBand` is still set invites another rejection round. (Age rating lives on `/v1/appInfos/{id}/ageRatingDeclaration`, not the version.)

## API reading quirks

- List endpoints return relationship *stubs* — categories read as `None` from `/v1/apps/{id}/appInfos` even when set. Fetch the single resource with `?include=…` before concluding a PATCH didn't stick.
- The transient "Sorry, something went wrong" banner rule from the browser applies to the API too, in mirror image: verify by re-reading, not by trusting the write's response shape.
