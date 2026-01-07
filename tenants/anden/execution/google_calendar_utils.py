#!/usr/bin/env python3
"""
Shared helpers for Google Calendar tools.

Required environment variables:
- GOOGLE_CALENDAR_CLIENT_ID (or GOOGLE_DRIVE_CLIENT_ID)
- GOOGLE_CALENDAR_CLIENT_SECRET (or GOOGLE_DRIVE_CLIENT_SECRET)
- GOOGLE_CALENDAR_REFRESH_TOKEN

Note: You can reuse your Drive client ID/secret, but you need a new
refresh token with calendar scope. Generate it using OAuth helper.
"""

import json
import os
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

TOKEN_URL = "https://oauth2.googleapis.com/token"
CALENDAR_API_BASE = "https://www.googleapis.com/calendar/v3"


def load_env():
    """Load .env file from current directory."""
    env_path = Path.cwd() / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    os.environ.setdefault(key.strip(), value.strip().strip('"\''))


def _get_env(name, fallback_name=None):
    """Get env var with optional fallback."""
    value = os.environ.get(name)
    if not value and fallback_name:
        value = os.environ.get(fallback_name)
    return value


def get_access_token():
    """Get OAuth access token using refresh token."""
    load_env()

    # Try calendar-specific vars first, fall back to drive vars
    client_id = _get_env("GOOGLE_CALENDAR_CLIENT_ID", "GOOGLE_DRIVE_CLIENT_ID")
    client_secret = _get_env("GOOGLE_CALENDAR_CLIENT_SECRET", "GOOGLE_DRIVE_CLIENT_SECRET")
    refresh_token = _get_env("GOOGLE_CALENDAR_REFRESH_TOKEN")

    if not client_id:
        raise RuntimeError("Missing GOOGLE_CALENDAR_CLIENT_ID (or GOOGLE_DRIVE_CLIENT_ID)")
    if not client_secret:
        raise RuntimeError("Missing GOOGLE_CALENDAR_CLIENT_SECRET (or GOOGLE_DRIVE_CLIENT_SECRET)")
    if not refresh_token:
        raise RuntimeError("Missing GOOGLE_CALENDAR_REFRESH_TOKEN - generate one with calendar scope")

    payload = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }).encode("utf-8")

    request = urllib.request.Request(TOKEN_URL, data=payload, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Token request failed: {exc.code} {body}")

    data = json.loads(body)
    access_token = data.get("access_token")
    if not access_token:
        raise RuntimeError(f"Token response missing access_token: {body}")

    return access_token


def calendar_request(access_token, path, params=None, method="GET", data=None, headers=None):
    """Make a Calendar API request."""
    url = CALENDAR_API_BASE + path
    if params:
        query = urllib.parse.urlencode(params, doseq=True)
        url = f"{url}?{query}"

    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {access_token}")

    if headers:
        for key, value in headers.items():
            req.add_header(key, value)

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Calendar API request failed: {exc.code} {body}")


def calendar_get_json(access_token, path, params=None):
    """Make GET request and parse JSON response."""
    raw = calendar_request(access_token, path, params=params)
    return json.loads(raw.decode("utf-8"))


def calendar_post_json(access_token, path, payload, params=None):
    """Make POST request with JSON body."""
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json; charset=utf-8"}
    raw = calendar_request(access_token, path, params=params, method="POST", data=data, headers=headers)
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))
