#!/usr/bin/env python3
"""
Send email via Gmail API (HTTPS, not SMTP).
Works on Railway where SMTP ports are blocked.

Required environment variables:
- GOOGLE_DRIVE_CLIENT_ID: OAuth client ID
- GOOGLE_DRIVE_CLIENT_SECRET: OAuth client secret
- GOOGLE_DRIVE_REFRESH_TOKEN: OAuth refresh token (with gmail.modify scope)
- GMAIL_ADDRESS: Your Gmail address (for From header)
"""

import sys
import json
import os
import base64
import urllib.request
import urllib.parse
import urllib.error
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def load_env_from_cwd():
    """Load .env file from current working directory into os.environ."""
    env_path = os.path.join(os.getcwd(), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip()
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    os.environ[key] = value


# Load .env from cwd (tenant folder)
load_env_from_cwd()


def get_access_token(client_id, client_secret, refresh_token):
    """Exchange refresh token for access token."""
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }).encode()

    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=data,
        method="POST"
    )
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode())
        return result["access_token"]


def send_email(access_token, from_email, to_email, subject, body):
    """Send email using Gmail API."""
    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # Encode the message
    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')

    # Send via Gmail API
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
    payload = json.dumps({"raw": raw_message}).encode()

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def main():
    try:
        input_data = json.loads(sys.stdin.read())

        to_email = input_data.get("to")
        subject = input_data.get("subject")
        body = input_data.get("body")

        # Validate required fields
        if not to_email:
            print(json.dumps({"status": "error", "message": "Missing 'to' email address"}))
            sys.exit(1)
        if not subject:
            print(json.dumps({"status": "error", "message": "Missing 'subject'"}))
            sys.exit(1)
        if not body:
            print(json.dumps({"status": "error", "message": "Missing 'body'"}))
            sys.exit(1)

        # Get OAuth credentials
        client_id = os.environ.get("GOOGLE_DRIVE_CLIENT_ID")
        client_secret = os.environ.get("GOOGLE_DRIVE_CLIENT_SECRET")
        refresh_token = os.environ.get("GOOGLE_DRIVE_REFRESH_TOKEN")
        gmail_address = os.environ.get("GMAIL_ADDRESS")

        if not all([client_id, client_secret, refresh_token]):
            print(json.dumps({
                "status": "error",
                "message": "Missing OAuth credentials (GOOGLE_DRIVE_CLIENT_ID, GOOGLE_DRIVE_CLIENT_SECRET, GOOGLE_DRIVE_REFRESH_TOKEN)"
            }))
            sys.exit(1)

        if not gmail_address:
            print(json.dumps({"status": "error", "message": "GMAIL_ADDRESS not configured"}))
            sys.exit(1)

        # Get access token
        access_token = get_access_token(client_id, client_secret, refresh_token)

        # Send the email
        result = send_email(access_token, gmail_address, to_email, subject, body)

        print(json.dumps({
            "status": "success",
            "message": f"Email sent to {to_email}",
            "message_id": result.get("id")
        }))

    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        try:
            error_json = json.loads(error_body)
            error_msg = error_json.get("error", {}).get("message", error_body)
        except:
            error_msg = error_body
        print(json.dumps({"status": "error", "message": f"Gmail API error: {error_msg}"}))
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(json.dumps({"status": "error", "message": f"Invalid JSON input: {e}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
