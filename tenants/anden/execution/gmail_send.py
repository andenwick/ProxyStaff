#!/usr/bin/env python3
"""
Send email via Gmail SMTP.

Required environment variables:
- GMAIL_ADDRESS: Your Gmail address
- GMAIL_APP_PASSWORD: Gmail App Password (not your regular password)
"""

import sys
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


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

        # Get credentials
        gmail_address = os.environ.get("GMAIL_ADDRESS")
        gmail_password = os.environ.get("GMAIL_APP_PASSWORD")

        if not gmail_address or not gmail_password:
            print(json.dumps({"status": "error", "message": "GMAIL_ADDRESS or GMAIL_APP_PASSWORD not configured"}))
            sys.exit(1)

        # Create message
        msg = MIMEMultipart()
        msg['From'] = gmail_address
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # Connect and send via Gmail SMTP
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_address, gmail_password)
        server.sendmail(gmail_address, to_email, msg.as_string())
        server.quit()

        print(json.dumps({
            "status": "success",
            "message": f"Email sent to {to_email}"
        }))

    except smtplib.SMTPAuthenticationError:
        print(json.dumps({"status": "error", "message": "Authentication failed. Check your Gmail App Password."}))
        sys.exit(1)
    except smtplib.SMTPException as e:
        print(json.dumps({"status": "error", "message": f"SMTP error: {e}"}))
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(json.dumps({"status": "error", "message": f"Invalid JSON input: {e}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
