#!/usr/bin/env python3
"""
Mark emails as read by ID in Gmail.

Required environment variables:
- GMAIL_ADDRESS: Your Gmail address
- GMAIL_APP_PASSWORD: Gmail App Password (not your regular password)
"""

import sys
import json
import os
import imaplib


def load_env_from_cwd():
    """Load .env file from current working directory into os.environ."""
    env_path = os.path.join(os.getcwd(), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip().strip('"').strip("'")
                    os.environ[key.strip()] = value


def main():
    load_env_from_cwd()
    try:
        input_data = json.loads(sys.stdin.read())

        email_ids = input_data.get("email_ids", [])

        if not email_ids:
            print(json.dumps({"status": "error", "message": "Missing 'email_ids' parameter"}))
            sys.exit(1)

        # Get credentials
        gmail_address = os.environ.get("GMAIL_ADDRESS")
        gmail_password = os.environ.get("GMAIL_APP_PASSWORD")

        if not gmail_address or not gmail_password:
            print(json.dumps({"status": "error", "message": "GMAIL_ADDRESS or GMAIL_APP_PASSWORD not configured"}))
            sys.exit(1)

        # Connect to Gmail IMAP
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(gmail_address, gmail_password)
        mail.select('INBOX')

        marked = []
        failed = []

        for email_id in email_ids:
            try:
                # Mark as read (add Seen flag)
                status, _ = mail.store(email_id.encode(), '+FLAGS', '\\Seen')
                if status == 'OK':
                    marked.append(email_id)
                else:
                    failed.append(email_id)
            except Exception as e:
                failed.append(email_id)

        mail.logout()

        result = {
            "status": "success",
            "marked": len(marked),
            "failed": len(failed),
            "marked_ids": marked,
            "failed_ids": failed
        }

        print(json.dumps(result))

    except imaplib.IMAP4.error as e:
        print(json.dumps({"status": "error", "message": f"IMAP error: {e}"}))
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(json.dumps({"status": "error", "message": f"Invalid JSON input: {e}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
