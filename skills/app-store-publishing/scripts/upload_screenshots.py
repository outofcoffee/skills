#!/usr/bin/env python3
"""Upload App Store screenshots to App Store Connect via the API.

Browser file-pickers can't be automated, so this uploads programmatically:
reserve -> PUT bytes -> commit, per screenshot, into the display set for the
editable iOS version's localization.

Config via environment (no secrets in the repo):
  ASC_KEY_ID      App Store Connect API key ID (App Manager or Admin role)
  ASC_ISSUER_ID   Issuer ID
  ASC_KEY_P8      path to the AuthKey_XXXX.p8
  ASC_APP_ID      the app's Apple ID (e.g. 6785043473)

Usage:
  ASC_KEY_ID=... ASC_ISSUER_ID=... ASC_KEY_P8=/path/AuthKey.p8 ASC_APP_ID=... \
    upload_screenshots.py \
      --dir build/screenshots/iphone-6.9 \
      --display APP_IPHONE_67 [--locale en-GB]

Display types: iPhone 6.9" (1320x2868) -> APP_IPHONE_67 (the 6.7"/6.9" slot).
iPad 13" (2064x2752) -> APP_IPAD_PRO_3GEN_129 (verify against the API).
See the app-store-publishing skill's references/screenshots.md.

Only needs the `cryptography` package; everything else is stdlib.
"""
import argparse, base64, hashlib, json, os, sys, time
import urllib.request, urllib.error
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

BASE = "https://api.appstoreconnect.apple.com"


def b64url(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=")


def make_jwt(key_id, issuer_id, p8_path):
    """ES256 JWT. The signature must be raw R||S (64 bytes), not DER."""
    key = load_pem_private_key(open(p8_path, "rb").read(), password=None)
    now = int(time.time())
    header = {"alg": "ES256", "kid": key_id, "typ": "JWT"}
    payload = {"iss": issuer_id, "iat": now, "exp": now + 1200, "aud": "appstoreconnect-v1"}
    si = (b64url(json.dumps(header, separators=(",", ":")).encode()) + b"."
          + b64url(json.dumps(payload, separators=(",", ":")).encode()))
    der = key.sign(si, ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(der)
    return (si + b"." + b64url(r.to_bytes(32, "big") + s.to_bytes(32, "big"))).decode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="directory of PNGs (uploaded in sorted order)")
    ap.add_argument("--display", required=True, help="screenshotDisplayType, e.g. APP_IPHONE_67")
    ap.add_argument("--locale", default="en-GB")
    args = ap.parse_args()

    try:
        key_id = os.environ["ASC_KEY_ID"]
        issuer = os.environ["ASC_ISSUER_ID"]
        p8 = os.environ["ASC_KEY_P8"]
        app_id = os.environ["ASC_APP_ID"]
    except KeyError as e:
        sys.exit(f"missing env var: {e}")

    token = make_jwt(key_id, issuer, p8)

    def api(method, path, body=None):
        url = path if path.startswith("http") else BASE + path
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", "Bearer " + token)
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req) as r:
                raw = r.read()
                return r.status, (json.loads(raw) if raw else {})
        except urllib.error.HTTPError as e:
            raw = e.read()
            try:
                return e.code, json.loads(raw)
            except Exception:
                return e.code, {"raw": raw.decode(errors="replace")}

    def die(msg, st=None, body=None):
        print("ERROR:", msg)
        if st is not None:
            print("  status:", st)
        if body is not None:
            print("  body:", json.dumps(body)[:800])
        sys.exit(1)

    # 1. editable iOS version
    st, d = api("GET", f"/v1/apps/{app_id}/appStoreVersions?filter%5Bplatform%5D=IOS&limit=50")
    if st != 200:
        die("list versions", st, d)
    editable = {"PREPARE_FOR_SUBMISSION", "DEVELOPER_REJECTED", "REJECTED",
                "METADATA_REJECTED", "INVALID_BINARY", "WAITING_FOR_REVIEW"}
    vers = [v for v in d["data"] if v["attributes"]["appStoreState"] in editable] or d["data"]
    ver = vers[0]
    print(f"version {ver['attributes']['versionString']} "
          f"({ver['attributes']['appStoreState']}) id={ver['id']}")

    # 2. localization
    st, d = api("GET", f"/v1/appStoreVersions/{ver['id']}/appStoreVersionLocalizations?limit=50")
    if st != 200:
        die("list localizations", st, d)
    loc = next((l for l in d["data"] if l["attributes"]["locale"] == args.locale), None)
    if not loc:
        die(f"no {args.locale} localization", st, d)
    print(f"localization {args.locale} id={loc['id']}")

    # 3. screenshot set
    st, d = api("GET", f"/v1/appStoreVersionLocalizations/{loc['id']}/appScreenshotSets?limit=50")
    if st != 200:
        die("list screenshot sets", st, d)
    ss = next((s for s in d["data"]
               if s["attributes"]["screenshotDisplayType"] == args.display), None)
    if not ss:
        st, d = api("POST", "/v1/appScreenshotSets", {
            "data": {"type": "appScreenshotSets",
                     "attributes": {"screenshotDisplayType": args.display},
                     "relationships": {"appStoreVersionLocalization": {
                         "data": {"type": "appStoreVersionLocalizations", "id": loc["id"]}}}}})
        if st not in (200, 201):
            die("create screenshot set", st, d)
        ss = d["data"]
    print(f"screenshot set {args.display} id={ss['id']}")

    st, d = api("GET", f"/v1/appScreenshotSets/{ss['id']}/appScreenshots?limit=50")
    existing = {s["attributes"].get("fileName") for s in d.get("data", [])} if st == 200 else set()

    # 4. reserve -> upload -> commit
    pngs = sorted(f for f in os.listdir(args.dir) if f.lower().endswith(".png"))
    if not pngs:
        die(f"no PNGs in {args.dir}")
    for fn in pngs:
        if fn in existing:
            print(f"skip {fn} (already present)")
            continue
        blob = open(os.path.join(args.dir, fn), "rb").read()
        st, d = api("POST", "/v1/appScreenshots", {
            "data": {"type": "appScreenshots",
                     "attributes": {"fileName": fn, "fileSize": len(blob)},
                     "relationships": {"appScreenshotSet": {
                         "data": {"type": "appScreenshotSets", "id": ss["id"]}}}}})
        if st not in (200, 201):
            die(f"reserve {fn}", st, d)
        sid = d["data"]["id"]
        for op in d["data"]["attributes"]["uploadOperations"]:
            req = urllib.request.Request(op["url"],
                                         data=blob[op["offset"]:op["offset"] + op["length"]],
                                         method="PUT")
            for h in op.get("requestHeaders", []):
                req.add_header(h["name"], h["value"])
            urllib.request.urlopen(req).read()
        st, d = api("PATCH", f"/v1/appScreenshots/{sid}", {
            "data": {"type": "appScreenshots", "id": sid,
                     "attributes": {"uploaded": True,
                                    "sourceFileChecksum": hashlib.md5(blob).hexdigest()}}})
        if st not in (200, 201):
            die(f"commit {fn}", st, d)
        print(f"uploaded {fn} ({len(blob)} bytes)")

    # 5. verify
    st, d = api("GET", f"/v1/appScreenshotSets/{ss['id']}/appScreenshots?limit=50")
    for s in d.get("data", []):
        a = s["attributes"]
        img = a.get("imageAsset") or {}
        print(f"  {a.get('fileName'):24} {a.get('assetDeliveryState', {}).get('state')} "
              f"{img.get('width')}x{img.get('height')}")
    print("DONE")


if __name__ == "__main__":
    main()
