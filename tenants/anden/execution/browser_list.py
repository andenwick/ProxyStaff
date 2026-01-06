#!/usr/bin/env python3
"""
Browser List Tool - Lists active browser sessions.
"""
import os
import sys
import json
import requests

def main():
    tenant_id = os.environ.get('TENANT_ID')
    api_base = os.environ.get('API_BASE_URL', 'http://localhost:3000')

    if not tenant_id:
        print("Error: TENANT_ID environment variable not set")
        sys.exit(1)

    try:
        response = requests.post(
            f"{api_base}/api/tools/browser/list",
            json={
                'tenant_id': tenant_id,
            },
            timeout=10
        )

        data = response.json()

        if data.get('success'):
            sessions = data.get('sessions', [])
            if not sessions:
                print("No active browser sessions")
            else:
                print(f"Active browser sessions ({len(sessions)}):")
                for s in sessions:
                    print(f"  - {s['id']} (persistent: {s.get('persistent', False)})")
        else:
            print(f"Error: {data.get('error', 'Unknown error')}")
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to connect to API - {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
