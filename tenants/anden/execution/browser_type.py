#!/usr/bin/env python3
"""
Browser Type Tool - Types text into an input element.
"""
import os
import sys
import json
import requests

def main():
    input_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}

    session_id = input_data.get('session_id')
    selector = input_data.get('selector')
    text = input_data.get('text')
    clear = input_data.get('clear', True)  # Default: clear field first

    if not session_id:
        print("Error: 'session_id' is required")
        sys.exit(1)
    if not selector:
        print("Error: 'selector' is required (CSS selector)")
        sys.exit(1)
    if text is None:
        print("Error: 'text' is required")
        sys.exit(1)

    tenant_id = os.environ.get('TENANT_ID')
    api_base = os.environ.get('API_BASE_URL', 'http://localhost:3000')

    if not tenant_id:
        print("Error: TENANT_ID environment variable not set")
        sys.exit(1)

    try:
        response = requests.post(
            f"{api_base}/api/tools/browser/type",
            json={
                'tenant_id': tenant_id,
                'session_id': session_id,
                'selector': selector,
                'text': text,
                'clear': clear,
            },
            timeout=30
        )

        data = response.json()

        if data.get('success'):
            print(data.get('message', f'Typed into: {selector}'))
        else:
            print(f"Error: {data.get('error', 'Unknown error')}")
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to connect to API - {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
