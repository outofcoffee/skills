# TestFlight CI

A GitHub Actions workflow that, on a version tag, builds the iOS app in Release and uploads it to TestFlight — no manual Xcode Organizer. Full template: [../templates/testflight.yml](../templates/testflight.yml). Start with the simple shape below; the **proven end state** (beta channel + automated review submission + persisted signing) is further down.

## Shape (starter)

- **Trigger:** `on: push: tags: ['v*']`. Tag `v0.2.0` → the build. Keeps every TestFlight build tied to an explicit release.
- **Versioning:** the tag (minus `v`) becomes the marketing version (`CFBundleShortVersionString`); the workflow **run number** becomes the build number (`CFBundleVersion`). Every upload is therefore monotonically increasing without editing committed Info.plist defaults. Stamp both with `PlistBuddy` after generating the project and before archiving.
- **Signing:** an App Store Connect API key + Xcode automatic signing (`-allowProvisioningUpdates`). Xcode creates and downloads the distribution cert + profile on the runner from the key — fine for the first runs, but see **the certificate cap** below before this becomes a routine pipeline.

## Shape (proven end state)

Once releases are routine, grow the workflow into two channels driven by what's pushed — one workflow, one `mode` output:

```
push → develop   : tests ─▶ upload to TestFlight            (beta: no metadata, no submission)
push tag v*.*.*  : tests ─▶ upload ─▶ wait for processing ─▶ deliver: metadata + attach + SUBMIT FOR REVIEW
workflow_dispatch: dropdown picks beta or release
```

- The tag job is a **full hands-off release**: after upload, a `submit-for-review` job (cheap **Linux** runner — no Xcode needed) waits for Apple to finish processing the build ([../scripts/wait_for_build.py](../scripts/wait_for_build.py), 5–30 min), then one fastlane `deliver` call pushes all listing metadata, sets the App Store version to the tag, attaches the build, and submits. Lanes: [../templates/Fastfile](../templates/Fastfile); details in [submission-review.md](submission-review.md).
- Beta builds (develop pushes) use the latest `v*.*.*` tag as marketing version and never touch the listing.
- **Pre-validate store assets on a cheap runner first.** A seconds-long Linux job checking the icon asset catalogue (covers every required device family) gates the macOS jobs — a missing iPhone icon size otherwise surfaces at Apple's validator ~40 macOS-runner-minutes in. Keep the check narrow: metadata is validated by `deliver` when it pushes, screenshot dimensions by Apple at reserve time — don't reimplement those.
- **Universal apps:** matrix the UI-test job over both device families (`device: [iPad, iPhone]`) so a release is gated on both.
- Cap every job with `timeout-minutes` a bit above its healthy runtime — the GitHub default is 6 h, and a hung UI test will happily sit there burning macOS minutes.

## Signing: the certificate cap (why the end state uses a persisted cert)

`-allowProvisioningUpdates` on an **ephemeral runner** asks Apple to mint a **fresh distribution certificate every run** (each runner has an empty keychain). These pile up invisibly until the account hits Apple's certificate cap and archives fail with *"Your account has reached the maximum number of certificates."*

The fix: create the distribution cert **once**, persist it, and sign **manually** — the API key then only authenticates the upload:

1. Store as secrets: `APPLE_DIST_CERT_P12` (base64 of the cert+key `.p12`), `APPLE_DIST_CERT_PASSWORD`, `APPLE_DIST_PROFILE` (base64 of the App Store `.mobileprovision`).
2. In the job, import the `.p12` into a **throwaway keychain** (`security create-keychain` → `import -T /usr/bin/codesign` → `set-key-partition-list`), install the profile under its UUID in `~/Library/MobileDevice/Provisioning Profiles/`, and delete the keychain in an `always()` cleanup.
3. Archive with `CODE_SIGN_STYLE=Manual CODE_SIGN_IDENTITY="Apple Distribution" PROVISIONING_PROFILE_SPECIFIER="<profile name>"` — no `-allowProvisioningUpdates` anywhere.
4. Keep the profile **name** in sync between the workflow and the export options plist's `provisioningProfiles` entry.
5. Rotation (~yearly, all via ASC API with an Admin key): new key+CSR → `POST /v1/certificates` (`DISTRIBUTION`) → `POST /v1/profiles` bound to it → rebuild the `.p12` **with `openssl pkcs12 -export -legacy`** (macOS `security import` can't read modern-alg .p12s) → refresh the three secrets → revoke the old cert.

## Required repo secrets

| Secret | Value |
|---|---|
| `APP_STORE_CONNECT_API_KEY_ID` | the Key ID |
| `APP_STORE_CONNECT_API_ISSUER_ID` | the Issuer ID (UUID) |
| `APP_STORE_CONNECT_API_KEY_P8` | base64 of the `.p8` (`base64 -i AuthKey_XXXX.p8`) |
| `APPLE_TEAM_ID` | 10-char Team ID |

Set them without the secret touching your context — pipe the file:
`base64 -i /path/AuthKey.p8 | tr -d '\n' | gh secret set APP_STORE_CONNECT_API_KEY_P8 --repo owner/repo`.

⚠️ The `--body ""` form silently sets an *empty* secret if the input command fails (e.g. `base64` can't read `~/Downloads`). Read the file from a readable path and verify.

## The gotchas that each broke a run

1. **API key must be Admin** *(cloud signing only)*. Cloud-creating the *distribution* cert needs Admin; App Manager fails the export with `Cloud signing permission error`. See [app-store-connect-setup.md](app-store-connect-setup.md). With the persisted-cert setup above, the per-run key needs no signing power at all (App Manager suffices — Admin is only needed at rotation time).
2. **iOS 26 SDK is mandatory for uploads.** Apple rejects anything not built with the iOS 26 SDK: `SDK version issue. This app was built with the iOS 18.5 SDK...`. Run the job on **`runs-on: macos-26`** — `macos-latest` still ships Xcode 16.
3. **Metal toolchain, only on new Xcode.** Xcode 16.1+ splits the Metal toolchain into a downloadable component (`xcodebuild -downloadComponent MetalToolchain`); older Xcode bundles it and rejects the flag with exit 64. If a dependency ships Metal shaders, make the step tolerant:
   ```sh
   xcodebuild -downloadComponent MetalToolchain >/dev/null 2>&1 \
     || echo "toolchain bundled or flag unsupported; continuing"
   ```
4. **Export options: `destination: upload`.** With the export options plist set to `method: app-store`, `destination: upload`, the `xcodebuild -exportArchive` step uploads to TestFlight directly (pass the same API key via `-authenticationKeyPath/-authenticationKeyID/-authenticationKeyIssuerID`). No fastlane needed. Template: [../templates/export-options-appstore.plist](../templates/export-options-appstore.plist).
5. **dSYM warning for gomobile/static frameworks is benign** — it's a warning, not a failure; the upload still completes.
6. **Every build stalls on the encryption question** until `ITSAppUsesNonExemptEncryption` (`NO` for standard OS crypto/HTTPS only) is in Info.plist — the declaration is read at archive time, so it fixes builds from the *next* one onward. See [submission-review.md](submission-review.md).

## If the app embeds a non-Swift core (gomobile / Go)

The template includes steps to build a `*.xcframework` via `gomobile bind` and to install Go. **Delete those steps for a pure-Swift app.** They're only there because this pattern came from an app whose core is a Go module compiled to an xcframework the Xcode project consumes. Same idea applies to any prebuilt binary dependency.

## The sibling test workflow (and the simulator-name trap)

A separate `test.yml` runs unit tests on push/PR. The lesson worth carrying: **`xcodebuild test` needs a concrete simulator destination, and runner images drop/rename simulators over time.** Hard-coding `name=iPhone 16` breaks with `Unable to find a device matching the destination` when the image moves on. Discover one at runtime instead:

```sh
udid=$(xcrun simctl list devices available \
       | grep -oE 'iPhone[^(]*\([0-9A-Fa-f-]{36}\)' \
       | grep -oE '[0-9A-Fa-f-]{36}' | head -1)
xcodebuild ... -destination "id=$udid" test
```

(`generic/platform=iOS Simulator` works for `build` but **not** `test`.)

## Kicking it off and watching

```sh
git tag v0.2.0 && git push origin v0.2.0
gh run watch <run-id> --repo owner/repo --exit-status   # exit 0 == success
```

A first-ever run needs the **app record to exist** (uploads fail without it) and all four secrets set.
