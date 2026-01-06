#!/usr/bin/env python3
"""
Shared tool: search_history
Searches conversation history for the current user.

Input (JSON via stdin):
{
    "query": "search term",
    "limit": 10  # optional, default: 10
}

Output (JSON to stdout):
{
    "success": true/false,
    "results": [...],
    "error": null | "error message"
}

Environment variables required:
- TENANT_ID: The tenant ID
- SENDER_PHONE: The phone number of the user
- API_BASE_URL: The server API base URL (default: http://localhost:3000)
"""

import sys
import json
import os
import urllib.request
import urllib.error
import urllib.parse


def main():
    # Read JSON input from stdin
    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        print(json.dumps({
            "success": False,
            "results": [],
            "error": f"Invalid JSON input: {str(e)}"
        }))
        sys.exit(1)

    # Get required environment variables
    tenant_id = os.environ.get("TENANT_ID")
    sender_phone = os.environ.get("SENDER_PHONE")
    api_base_url = os.environ.get("API_BASE_URL", "http://localhost:3000")

    if not tenant_id or not sender_phone:
        print(json.dumps({
            "success": False,
            "results": [],
            "error": "Missing required environment variables: TENANT_ID, SENDER_PHONE"
        }))
        sys.exit(1)

    # Validate input
    query = input_data.get("query")
    if not query:
        print(json.dumps({
            "success": False,
            "results": [],
            "error": "Missing required field: query"
        }))
        sys.exit(1)

    limit = input_data.get("limit", 10)

    # Build query string
    params = urllib.parse.urlencode({
        "tenantId": tenant_id,
        "senderPhone": sender_phone,
        "query": query,
        "limit": limit
    })

    # Make API request
    try:
        url = f"{api_base_url}/api/tools/search-history?{params}"
        req = urllib.request.Request(url, method="GET")

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))

        print(json.dumps({
            "success": True,
            "results": result.get("results", []),
            "error": None
        }))

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else str(e)
        print(json.dumps({
            "success": False,
            "results": [],
            "error": f"API error ({e.code}): {error_body}"
        }))
        sys.exit(1)

    except urllib.error.URLError as e:
        print(json.dumps({
            "success": False,
            "results": [],
            "error": f"Connection error: {str(e.reason)}"
        }))
        sys.exit(1)

    except Exception as e:
        print(json.dumps({
            "success": False,
            "results": [],
            "error": f"Unexpected error: {str(e)}"
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
