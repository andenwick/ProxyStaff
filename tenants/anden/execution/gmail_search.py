#!/usr/bin/env python3
"""
Search Gmail inbox using IMAP.

Required environment variables (or .env file in cwd):
- GMAIL_ADDRESS: Your Gmail address
- GMAIL_APP_PASSWORD: Gmail App Password (not your regular password)
"""

import sys
import json
import os
import imaplib
import email
from email.header import decode_header
from datetime import datetime

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
                    value = value.strip()
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    os.environ[key] = value

# Load .env from cwd (tenant folder)
load_env_from_cwd()


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


def convert_query_to_imap(query):
    """Convert Gmail-style query to IMAP search criteria."""
    # Simple conversion for common Gmail search operators
    criteria = []

    # Handle common Gmail operators
    if 'is:unread' in query:
        criteria.append('UNSEEN')
        query = query.replace('is:unread', '')
    if 'is:read' in query:
        criteria.append('SEEN')
        query = query.replace('is:read', '')

    # Handle from:
    import re
    from_match = re.search(r'from:(\S+)', query)
    if from_match:
        criteria.append(f'FROM "{from_match.group(1)}"')
        query = re.sub(r'from:\S+', '', query)

    # Handle to:
    to_match = re.search(r'to:(\S+)', query)
    if to_match:
        criteria.append(f'TO "{to_match.group(1)}"')
        query = re.sub(r'to:\S+', '', query)

    # Handle subject:
    subject_match = re.search(r'subject:(\S+)', query)
    if subject_match:
        criteria.append(f'SUBJECT "{subject_match.group(1)}"')
        query = re.sub(r'subject:\S+', '', query)

    # Handle newer_than:Xd (days)
    newer_match = re.search(r'newer_than:(\d+)d', query)
    if newer_match:
        from datetime import timedelta
        days = int(newer_match.group(1))
        since_date = (datetime.now() - timedelta(days=days)).strftime('%d-%b-%Y')
        criteria.append(f'SINCE {since_date}')
        query = re.sub(r'newer_than:\d+d', '', query)

    # Handle after:YYYY/MM/DD
    after_match = re.search(r'after:(\d{4})/(\d{2})/(\d{2})', query)
    if after_match:
        date_str = datetime(int(after_match.group(1)), int(after_match.group(2)), int(after_match.group(3))).strftime('%d-%b-%Y')
        criteria.append(f'SINCE {date_str}')
        query = re.sub(r'after:\d{4}/\d{2}/\d{2}', '', query)

    # Handle before:YYYY/MM/DD
    before_match = re.search(r'before:(\d{4})/(\d{2})/(\d{2})', query)
    if before_match:
        date_str = datetime(int(before_match.group(1)), int(before_match.group(2)), int(before_match.group(3))).strftime('%d-%b-%Y')
        criteria.append(f'BEFORE {date_str}')
        query = re.sub(r'before:\d{4}/\d{2}/\d{2}', '', query)

    # Any remaining text becomes a body/text search
    remaining = query.strip()
    if remaining:
        criteria.append(f'TEXT "{remaining}"')

    # Default to ALL if no criteria
    if not criteria:
        criteria.append('ALL')

    return ' '.join(criteria)


def main():
    try:
        input_data = json.loads(sys.stdin.read())

        query = input_data.get("query", "")
        max_results = input_data.get("max_results", 10)

        if not query:
            print(json.dumps({"status": "error", "message": "Missing 'query' parameter"}))
            sys.exit(1)

        # Get credentials
        gmail_address = os.environ.get("GMAIL_ADDRESS")
        gmail_password = os.environ.get("GMAIL_APP_PASSWORD")
        tenant_folder = os.environ.get("TENANT_FOLDER", "NOT_SET")

        if not gmail_address or not gmail_password:
            # Debug: show what env vars we have
            env_keys = [k for k in os.environ.keys() if k.startswith(("GMAIL", "TENANT"))]
            print(json.dumps({
                "status": "error",
                "message": "GMAIL_ADDRESS or GMAIL_APP_PASSWORD not configured",
                "debug": {
                    "TENANT_FOLDER": tenant_folder,
                    "relevant_env_keys": env_keys,
                    "GMAIL_ADDRESS_set": gmail_address is not None,
                    "GMAIL_APP_PASSWORD_set": gmail_password is not None
                }
            }))
            sys.exit(1)

        # Connect to Gmail IMAP
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(gmail_address, gmail_password)
        mail.select('INBOX')

        # Convert query to IMAP format and search
        imap_criteria = convert_query_to_imap(query)
        status, messages = mail.search(None, imap_criteria)

        if status != 'OK':
            print(json.dumps({"status": "error", "message": "Search failed"}))
            sys.exit(1)

        email_ids = messages[0].split()

        # Get most recent emails (last N)
        email_ids = email_ids[-max_results:] if len(email_ids) > max_results else email_ids
        email_ids = list(reversed(email_ids))  # Most recent first

        results = []
        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, '(RFC822.HEADER)')
            if status != 'OK':
                continue

            msg = email.message_from_bytes(msg_data[0][1])

            # Parse date
            date_str = msg.get('Date', '')
            try:
                from email.utils import parsedate_to_datetime
                date_obj = parsedate_to_datetime(date_str)
                formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
            except:
                formatted_date = date_str[:20] if date_str else 'Unknown'

            results.append({
                "id": email_id.decode(),
                "from": decode_mime_header(msg.get('From', '')),
                "subject": decode_mime_header(msg.get('Subject', '(No subject)')),
                "date": formatted_date
            })

        mail.logout()

        print(json.dumps({
            "status": "success",
            "count": len(results),
            "emails": results
        }))

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
