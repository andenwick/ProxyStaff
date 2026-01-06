#!/usr/bin/env python3
"""
Save a crypto deposit address for a platform (e.g., Rainbet).
Addresses are stored in life/knowledge/deposit_addresses.json for future use.
"""

import sys
import json
import os
import re


# File path relative to tenant folder
ADDRESSES_FILE = "life/knowledge/deposit_addresses.json"


def validate_address(address: str, network: str) -> bool:
    """Basic address validation."""
    if network.upper() in ["TRC20", "TRON", "TRX"]:
        return address.startswith("T") and len(address) == 34
    elif network.upper() in ["ERC20", "ETH", "ETHEREUM"]:
        return address.startswith("0x") and len(address) == 42
    elif network.upper() in ["BEP20", "BSC", "BNB"]:
        return address.startswith("0x") and len(address) == 42
    # Default: allow if looks like a valid crypto address
    return len(address) >= 26 and re.match(r'^[a-zA-Z0-9]+$', address)


def load_addresses() -> dict:
    """Load existing addresses from file."""
    if os.path.exists(ADDRESSES_FILE):
        try:
            with open(ADDRESSES_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_addresses(addresses: dict) -> None:
    """Save addresses to file."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(ADDRESSES_FILE), exist_ok=True)
    with open(ADDRESSES_FILE, 'w') as f:
        json.dump(addresses, f, indent=2)


def main():
    try:
        input_data = json.loads(sys.stdin.read())

        platform = input_data.get("platform", "").lower()
        address = input_data.get("address")
        network = input_data.get("network", "TRC20")
        currency = input_data.get("currency", "USDT")

        # Validate required fields
        if not platform:
            print(json.dumps({"status": "error", "message": "Missing 'platform' (e.g., rainbet)"}))
            sys.exit(1)
        if not address:
            print(json.dumps({"status": "error", "message": "Missing 'address'"}))
            sys.exit(1)

        # Validate address format
        if not validate_address(address, network):
            print(json.dumps({
                "status": "error",
                "message": f"Invalid address format for {network}: {address}"
            }))
            sys.exit(1)

        # Load existing addresses
        addresses = load_addresses()

        # Save the new address
        addresses[platform] = {
            "address": address,
            "network": network.upper(),
            "currency": currency.upper(),
            "updated_at": __import__('datetime').datetime.now().isoformat()
        }

        save_addresses(addresses)

        print(json.dumps({
            "status": "success",
            "platform": platform,
            "address": address,
            "network": network.upper(),
            "currency": currency.upper(),
            "message": f"Saved {platform} deposit address: {address[:10]}...{address[-6:]}"
        }))

    except json.JSONDecodeError as e:
        print(json.dumps({"status": "error", "message": f"Invalid JSON input: {e}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
