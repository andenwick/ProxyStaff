#!/usr/bin/env python3
"""
Read a specific email by ID from Gmail.

Required environment variables:
- GMAIL_ADDRESS: Your Gmail address
- GMAIL_APP_PASSWORD: Gmail App Password (not your regular password)
"""

import sys
import json
import os
import imaplib
import email
from email.header import decode_header


def decode_mime_header(header):
    """Decode MIME encoded header to string."""
    if header is None:
        return ""
    decoded_parts = decode_header(header)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(charset or 'utf-8', errors='replace'))
        else:
            result.append(part)
    return ''.join(result)


def get_email_body(msg):
    """Extract plain text body from email message."""
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))

            # Skip attachments
            if "attachment" in content_disposition:
                continue

            # Get plain text content
            if content_type == "text/plain":
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode(charset, errors='replace')
                        break
                except:
                    pass
            # Fallback to HTML if no plain text
            elif content_type == "text/html" and not body:
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    payload = part.get_payload(decode=True)
                    if payload:
                        # Simple HTML to text - strip tags
                        import re
                        html = payload.decode(charset, errors='replace')
                        body = re.sub(r'<[^>]+>', '', html)
                        body = re.sub(r'\s+', ' ', body).strip()
                except:
                    pass
    else:
        # Not multipart - get payload directly
        try:
            charset = msg.get_content_charset() or 'utf-8'
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode(charset, errors='replace')
        except:
            body = str(msg.get_payload())

    return body.strip()


def main():
    try:
        input_data = json.loads(sys.stdin.read())

        email_id = input_data.get("email_id")

        if not email_id:
            print(json.dumps({"status": "error", "message": "Missing 'email_id' parameter"}))
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

        # Fetch the full email
        status, msg_data = mail.fetch(email_id.encode(), '(RFC822)')

        if status != 'OK' or not msg_data or not msg_data[0]:
            print(json.dumps({"status": "error", "message": f"Email with ID {email_id} not found"}))
            sys.exit(1)

        msg = email.message_from_bytes(msg_data[0][1])

        # Parse date
        date_str = msg.get('Date', '')
        try:
            from email.utils import parsedate_to_datetime
            date_obj = parsedate_to_datetime(date_str)
            formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
        except:
            formatted_date = date_str[:20] if date_str else 'Unknown'

        # Get attachments info
        attachments = []
        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition", ""))
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        attachments.append(decode_mime_header(filename))

        result = {
            "status": "success",
            "email": {
                "id": email_id,
                "from": decode_mime_header(msg.get('From', '')),
                "to": decode_mime_header(msg.get('To', '')),
                "subject": decode_mime_header(msg.get('Subject', '(No subject)')),
                "date": formatted_date,
                "body": get_email_body(msg),
                "attachments": attachments
            }
        }

        mail.logout()
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
