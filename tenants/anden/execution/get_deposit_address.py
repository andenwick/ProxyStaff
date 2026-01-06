#!/usr/bin/env python3
"""
Get a saved crypto deposit address for a platform (e.g., Rainbet).
Reads from life/knowledge/deposit_addresses.json.
"""

import sys
import json
import os


# File path relative to tenant folder
ADDRESSES_FILE = "life/knowledge/deposit_addresses.json"


def load_addresses() -> dict:
    """Load existing addresses from file."""
    if os.path.exists(ADDRESSES_FILE):
        try:
            with open(ADDRESSES_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        platform = input_data.get("platform", "").lower()

        addresses = load_addresses()

        if platform:
            # Return specific platform
            if platform in addresses:
                addr_info = addresses[platform]
                print(json.dumps({
                    "status": "success",
                    "platform": platform,
                    "address": addr_info.get("address"),
                    "network": addr_info.get("network"),
                    "currency": addr_info.get("currency")
                }))
            else:
                print(json.dumps({
                    "status": "not_found",
                    "platform": platform,
                    "message": f"No deposit address saved for {platform}. Ask the user for their {platform} deposit address."
                }))
        else:
            # Return all platforms
            if addresses:
                print(json.dumps({
                    "status": "success",
                    "addresses": addresses
                }))
            else:
                print(json.dumps({
                    "status": "empty",
                    "message": "No deposit addresses saved yet."
                }))

    except json.JSONDecodeError as e:
        print(json.dumps({"status": "error", "message": f"Invalid JSON input: {e}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
