#!/usr/bin/env python3
"""
Send email via SendGrid API.

Required environment variables:
- SENDGRID_API_KEY: Your SendGrid API key
- DEFAULT_FROM_EMAIL: Default sender email address
"""

import sys
import json
import os

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
except ImportError:
    print(json.dumps({
        "status": "error",
        "message": "SendGrid library not installed. Run: pip install sendgrid"
    }))
    sys.exit(1)


def main():
    try:
        # Read JSON input from stdin
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

        # Get credentials from environment
        api_key = os.environ.get("SENDGRID_API_KEY")
        from_email = os.environ.get("DEFAULT_FROM_EMAIL")

        if not api_key:
            print(json.dumps({"status": "error", "message": "SENDGRID_API_KEY not configured"}))
            sys.exit(1)
        if not from_email:
            print(json.dumps({"status": "error", "message": "DEFAULT_FROM_EMAIL not configured"}))
            sys.exit(1)

        # Create and send email
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            plain_text_content=body
        )

        sg = SendGridAPIClient(api_key)
        response = sg.send(message)

        # Check response
        if response.status_code in [200, 201, 202]:
            print(json.dumps({
                "status": "success",
                "message": f"Email sent to {to_email}",
                "status_code": response.status_code
            }))
        else:
            print(json.dumps({
                "status": "error",
                "message": f"SendGrid returned status {response.status_code}",
                "status_code": response.status_code
            }))
            sys.exit(1)

    except json.JSONDecodeError as e:
        print(json.dumps({"status": "error", "message": f"Invalid JSON input: {e}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
