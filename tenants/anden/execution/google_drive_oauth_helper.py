#!/usr/bin/env python3
"""
Generate a Google Drive OAuth refresh token.

Required environment variables:
- GOOGLE_DRIVE_CLIENT_ID
- GOOGLE_DRIVE_CLIENT_SECRET

Optional:
- GOOGLE_DRIVE_SCOPE (default: https://www.googleapis.com/auth/drive)
- GOOGLE_DRIVE_REDIRECT_URI (default: http://localhost)
"""

import json
import os
import sys
import urllib.parse
import urllib.request
import urllib.error


AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"


def load_env_file():
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    if not os.path.exists(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception:
        # Ignore .env parsing errors
        return


def get_env(name):
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


def extract_code(value):
    value = value.strip()
    if "code=" in value:
        parsed = urllib.parse.urlparse(value)
        query = urllib.parse.parse_qs(parsed.query)
        code = query.get("code", [None])[0]
        return code
    return value


def main():
    try:
        load_env_file()
        client_id = get_env("GOOGLE_DRIVE_CLIENT_ID")
        client_secret = get_env("GOOGLE_DRIVE_CLIENT_SECRET")
        scope = os.environ.get("GOOGLE_DRIVE_SCOPE", "https://www.googleapis.com/auth/drive")
        redirect_uri = os.environ.get("GOOGLE_DRIVE_REDIRECT_URI", "http://localhost")

        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": scope,
            "access_type": "offline",
            "prompt": "consent",
        }
        auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

        print("Open this URL in your browser and approve access:")
        print(auth_url)
        print("")
        raw = input("Paste the authorization code or full redirect URL here: ").strip()
        if not raw:
            print(json.dumps({"status": "error", "message": "No authorization code provided"}))
            sys.exit(1)

        code = extract_code(raw)
        if not code:
            print(json.dumps({"status": "error", "message": "Authorization code not found"}))
            sys.exit(1)

        payload = urllib.parse.urlencode({
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }).encode("utf-8")

        request = urllib.request.Request(TOKEN_URL, data=payload, method="POST")
        request.add_header("Content-Type", "application/x-www-form-urlencoded")

        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8")

        data = json.loads(body)
        refresh_token = data.get("refresh_token")

        result = {
            "status": "success",
            "refresh_token": refresh_token,
            "access_token": data.get("access_token"),
            "expires_in": data.get("expires_in"),
            "scope": data.get("scope"),
            "token_type": data.get("token_type"),
        }

        if not refresh_token:
            result["status"] = "warning"
            result["message"] = "No refresh_token returned. Try again with prompt=consent and a new grant."

        print(json.dumps(result, indent=2))

    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(json.dumps({"status": "error", "message": f"Token request failed: {exc.code} {body}"}))
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(json.dumps({"status": "error", "message": f"Invalid JSON response: {exc}"}))
        sys.exit(1)
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
