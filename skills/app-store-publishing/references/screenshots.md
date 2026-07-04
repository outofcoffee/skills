# Screenshots

Capture bare device screenshots from the simulator (with realistic on-screen content), then upload them via the App Store Connect API. Manual, occasional work — there's no full automation, but the pieces below make it repeatable.

## Sizes

The simulator's **native resolution is the required App Store size** — capture portrait, no resizing.

| Device class | Simulator | Size | API display type |
|---|---|---|---|
| iPhone 6.9" | iPhone 17 Pro Max | 1320×2868 | `APP_IPHONE_67` (the 6.7"/6.9" slot) |
| iPad 13" | iPad Pro 13-inch | 2064×2752 | `APP_IPAD_PRO_3GEN_129` (verify against the API) |

A universal app needs a set per class. Apple shows the first ~3 most prominently — lead with your strongest.

## Style: bare captures

Prefer **bare device captures** — no captions, frames, or marketing overlays. They're honest and fast, and read well for a utility/developer audience. The place to inject brand personality is the **content typed into the app** (prompts, sample data), matching the product's voice — not an overlay.

## 1. Build and install

```sh
DEV=$(xcrun simctl list devices available | grep 'iPhone 17 Pro Max' | head -1 | grep -oE '[0-9A-Fa-f-]{36}')
xcrun simctl boot "$DEV"; open -a Simulator
xcrun simctl install "$DEV" /path/to/App.app     # a Debug-iphonesimulator build
```

## 2. Stage realistic data

Empty screens make weak screenshots. Two ways to populate state:

- **Pre-seed the app's data container** before launch (fastest, avoids typing). Find it with
  `xcrun simctl get_app_container "$DEV" <bundle-id> data`, then write the app's config/DB under
  `<container>/Library/Application Support/<app>/…`. Great for seeding accounts/connections/settings so the app comes up already configured.
- **Drive the UI** for anything that must be created live (e.g. server-side records, auth). See the input gotcha below.

Notes from a real run: the simulator reaches the **Mac's `localhost`**, and plain HTTP to `localhost` works in-sim (no ATS exception). Some backends need a live pairing/approval step you can't pre-seed (a device token issued by a server) — do those through the UI, and if approval is a privileged action on the user's machine, **ask the user to run it**. Create a few realistic records (e.g. several backends, a handful of agents/items) so list screens tell the "works with many" story.

## 3. Typing into the simulator (the gotcha)

The computer-use `type` action garbles into iOS text fields. Use the **clipboard**: the Simulator auto-syncs the *Mac* pasteboard, so set it on the Mac and paste:

```sh
printf '%s' "text to enter" | pbcopy      # Mac clipboard
# then Cmd+V into the focused field (focused whenever the keyboard accessory bar shows)
```

Drive navigation with the app's own commands/shortcuts; screenshot after each screen settles.

## 4. Capture

```sh
xcrun simctl io "$DEV" screenshot out/01-name.png       # already at the required resolution
```

To **review** a shot (the full-res is too tall for most image viewers), downscale a preview: `sips -Z 1400 out/01-name.png preview.png`.

Save the set to a gitignored `build/` dir — screenshots are binaries, don't commit them. Number them in display order.

## 5. Upload

Browser file-pickers can't be driven from tooling, so:

- **By hand** — drag the PNGs into App Store Connect → the version → the matching display set. Foolproof.
- **Via the API** — [../scripts/upload_screenshots.py](../scripts/upload_screenshots.py) does it. Needs only the `cryptography` package; config via env vars:

  ```sh
  ASC_KEY_ID=... ASC_ISSUER_ID=... ASC_KEY_P8=/path/AuthKey.p8 ASC_APP_ID=... \
    scripts/upload_screenshots.py --dir build/screenshots/iphone-6.9 --display APP_IPHONE_67
  ```

  The key needs **App Manager or Admin** (editing media — lighter than the signing key). The flow, and the traps if you rebuild it:

  1. **Auth** — an ES256 JWT: header `{alg:ES256, kid:<KeyID>}`, payload `{iss:<IssuerID>, iat, exp, aud:"appstoreconnect-v1"}`. The signature must be **raw `R||S` (64 bytes), not DER** — the one real trap.
  2. Find the editable iOS `appStoreVersion` (state `PREPARE_FOR_SUBMISSION`) → its `en-GB` (or target locale) `appStoreVersionLocalization`.
  3. Get or create the `appScreenshotSet` for the display type. **6.9" (1320×2868) → `APP_IPHONE_67`.**
  4. Per file: **reserve** (`POST /v1/appScreenshots` with `fileName` + `fileSize`) → the response's `uploadOperations` give PUT URL(s) + headers → **PUT** the byte ranges → **commit** (`PATCH …` with `uploaded:true` and `sourceFileChecksum` = the file's MD5 hex).
  5. **Verify** each screenshot's `assetDeliveryState.state` reaches `COMPLETE` (`FAILED` = wrong dimensions/format for that display type). The script prints this.

  The script skips files already in the set (by `fileName`), so re-running after a partial failure is safe.

## Cleanup

Delete any throwaway records you created purely to stage the shots (demo accounts/agents) if the user doesn't want them, and remove seeded credentials from the simulator container.
