#!/usr/bin/env python3
"""Wait until a TestFlight build finishes processing on App Store Connect.

The release job (.github/workflows/testflight.yml) uploads the build to
TestFlight, then submits it for App Store review with fastlane deliver. deliver
can only attach a build that has finished processing on Apple's side, which is
asynchronous and can take 5-30 minutes — so this polls the build's
processingState until it is VALID (or times out).

Config via environment (no secrets in the repo):
  ASC_KEY_ID      App Store Connect API key ID (App Manager or Admin role)
  ASC_ISSUER_ID   Issuer ID
  ASC_KEY_P8_B64  base64 of the AuthKey_XXXX.p8
  ASC_APP_ID      the app's Apple ID (e.g. 6787093034)

Usage:
  wait_for_build.py --version 1.2.3 --build 42 [--timeout 1800] [--interval 30]

Only needs the `cryptography` package; everything else is stdlib.
"""
import argparse, base64, json, os, sys, time
import urllib.request, urllib.error
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

BASE = "https://api.appstoreconnect.apple.com"


def b64url(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=")


def make_jwt(key_id, issuer_id, p8_bytes):
    """ES256 JWT. The signature must be raw R||S (64 bytes), not DER. Apple caps
    the token lifetime at 20 minutes, so we mint a fresh one on every poll."""
    key = load_pem_private_key(p8_bytes, password=None)
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
    ap.add_argument("--version", required=True, help="marketing version, e.g. 1.2.3")
    ap.add_argument("--build", required=True, help="build number (CFBundleVersion), e.g. 42")
    ap.add_argument("--timeout", type=int, default=1800, help="seconds to wait (default 1800)")
    ap.add_argument("--interval", type=int, default=30, help="seconds between polls (default 30)")
    args = ap.parse_args()

    try:
        key_id = os.environ["ASC_KEY_ID"]
        issuer = os.environ["ASC_ISSUER_ID"]
        p8 = base64.b64decode(os.environ["ASC_KEY_P8_B64"])
        app_id = os.environ["ASC_APP_ID"]
    except KeyError as e:
        sys.exit(f"missing env var: {e}")

    # Filter builds by app, marketing (pre-release) version and build number.
    query = (f"/v1/builds?filter%5Bapp%5D={app_id}"
             f"&filter%5BpreReleaseVersion.version%5D={args.version}"
             f"&filter%5Bversion%5D={args.build}&limit=1")

    def get(path, token):
        req = urllib.request.Request(BASE + path, method="GET")
        req.add_header("Authorization", "Bearer " + token)
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            raw = e.read()
            try:
                return e.code, json.loads(raw)
            except Exception:
                return e.code, {"raw": raw.decode(errors="replace")}

    deadline = time.time() + args.timeout
    while True:
        st, d = get(query, make_jwt(key_id, issuer, p8))
        if st != 200:
            print("ERROR querying builds:", st, json.dumps(d)[:400])
            sys.exit(1)
        builds = d.get("data", [])
        if builds:
            state = builds[0]["attributes"].get("processingState")
            print(f"build {args.version} ({args.build}): processingState={state}")
            if state == "VALID":
                print("build is ready for submission")
                return
            if state in ("INVALID", "FAILED"):
                sys.exit(f"build processing ended in state {state}")
        else:
            print(f"build {args.version} ({args.build}) not visible yet")
        if time.time() >= deadline:
            sys.exit(f"timed out after {args.timeout}s waiting for the build to process")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
