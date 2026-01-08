#!/usr/bin/env python3
"""
Send an HTML email via Gmail SMTP.
"""
import sys
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

# Load .env file from tenant folder
tenant_folder = os.environ.get('TENANT_FOLDER', '/app/tenants/anden')
env_file = Path(tenant_folder) / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                # Remove quotes if present
                value = value.strip().strip('"').strip("'")
                # Handle escaped quotes
                value = value.replace('\\"', '')
                os.environ[key] = value

def main():
    try:
        input_data = json.loads(sys.stdin.read())

        to = input_data.get('to')
        subject = input_data.get('subject')
        html_body = input_data.get('html_body')

        if not all([to, subject, html_body]):
            raise Exception("Missing required fields: to, subject, html_body")

        # Get Gmail credentials from environment
        gmail_user = os.environ.get('GMAIL_USER') or os.environ.get('GMAIL_ADDRESS')
        gmail_password = os.environ.get('GMAIL_APP_PASSWORD')

        if not gmail_user or not gmail_password:
            raise Exception("GMAIL_USER/GMAIL_ADDRESS and GMAIL_APP_PASSWORD must be set in .env")

        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = gmail_user
        msg['To'] = to
        msg['Subject'] = subject

        # Attach HTML body
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)

        # Send via Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_user, gmail_password)
            server.send_message(msg)

        result = {
            'success': True,
            'message': f'HTML email sent to {to}'
        }

        print(json.dumps(result, indent=2))

    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e)
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
