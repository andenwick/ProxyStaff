#!/usr/bin/env python3
"""
Browser Open Tool - Opens a browser and navigates to a URL.
Returns a session_id that must be used for subsequent browser operations.
"""
import os
import sys
import json
import requests

def main():
    # Get input from stdin (JSON)
    input_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}

    url = input_data.get('url')
    session_id = input_data.get('session_id')
    persistent = input_data.get('persistent', False)

    if not url:
        print("Error: 'url' is required")
        sys.exit(1)

    tenant_id = os.environ.get('TENANT_ID')
    api_base = os.environ.get('API_BASE_URL', 'http://localhost:3000')

    if not tenant_id:
        print("Error: TENANT_ID environment variable not set")
        sys.exit(1)

    try:
        response = requests.post(
            f"{api_base}/api/tools/browser/open",
            json={
                'tenant_id': tenant_id,
                'url': url,
                'session_id': session_id,
                'persistent': persistent,
            },
            timeout=60
        )

        data = response.json()

        if data.get('success'):
            print(f"Browser opened successfully.")
            print(f"Session ID: {data['session_id']}")
            print(f"Page title: {data.get('title', 'N/A')}")
            print(f"Current URL: {data.get('url', url)}")
        else:
            print(f"Error: {data.get('error', 'Unknown error')}")
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to connect to API - {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
