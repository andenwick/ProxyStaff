#!/usr/bin/env python3
"""
Browser Login Tool - Fills a login form using stored credentials.
Credentials must be pre-stored as {service}_email and {service}_password.
"""
import os
import sys
import json
import requests

def main():
    input_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}

    session_id = input_data.get('session_id')
    service = input_data.get('service')
    email_selector = input_data.get('email_selector')
    password_selector = input_data.get('password_selector')
    submit_selector = input_data.get('submit_selector')

    if not session_id:
        print("Error: 'session_id' is required (from browser_open)")
        sys.exit(1)
    if not service:
        print("Error: 'service' is required (e.g., 'imyfone')")
        sys.exit(1)

    tenant_id = os.environ.get('TENANT_ID')
    api_base = os.environ.get('API_BASE_URL', 'http://localhost:3000')

    if not tenant_id:
        print("Error: TENANT_ID environment variable not set")
        sys.exit(1)

    try:
        response = requests.post(
            f"{api_base}/api/tools/browser/login",
            json={
                'tenant_id': tenant_id,
                'session_id': session_id,
                'service': service,
                'email_selector': email_selector,
                'password_selector': password_selector,
                'submit_selector': submit_selector,
            },
            timeout=60
        )

        data = response.json()

        if data.get('success'):
            print(data.get('message', 'Login form filled'))
        else:
            print(f"Error: {data.get('error', 'Unknown error')}")
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to connect to API - {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
