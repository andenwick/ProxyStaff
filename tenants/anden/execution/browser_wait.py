#!/usr/bin/env python3
"""
Browser Wait Tool - Waits for an element or page state.
"""
import os
import sys
import json
import requests

def main():
    input_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}

    session_id = input_data.get('session_id')
    selector = input_data.get('selector')  # Optional
    state = input_data.get('state', 'visible')  # visible, hidden, attached, detached
    timeout = input_data.get('timeout', 30000)  # ms

    if not session_id:
        print("Error: 'session_id' is required")
        sys.exit(1)

    tenant_id = os.environ.get('TENANT_ID')
    api_base = os.environ.get('API_BASE_URL', 'http://localhost:3000')

    if not tenant_id:
        print("Error: TENANT_ID environment variable not set")
        sys.exit(1)

    try:
        response = requests.post(
            f"{api_base}/api/tools/browser/wait",
            json={
                'tenant_id': tenant_id,
                'session_id': session_id,
                'selector': selector,
                'state': state,
                'timeout': timeout,
            },
            timeout=max(timeout/1000 + 10, 60)  # Convert ms to seconds + buffer
        )

        data = response.json()

        if data.get('success'):
            print(data.get('message', 'Wait completed'))
        else:
            print(f"Error: {data.get('error', 'Unknown error')}")
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to connect to API - {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
