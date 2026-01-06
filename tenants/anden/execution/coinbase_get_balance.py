#!/usr/bin/env python3
"""
Check Coinbase wallet balance.

Required environment variables:
- COINBASE_API_KEY: Coinbase CDP API key name
- COINBASE_API_SECRET: Coinbase CDP API private key
"""

import sys
import json
import os
import hmac
import hashlib
import time
import urllib.request
import urllib.error


def get_coinbase_balances(api_key: str, api_secret: str) -> dict:
    """Fetch account balances from Coinbase API."""
    timestamp = str(int(time.time()))
    method = "GET"
    request_path = "/v2/accounts"

    # Create signature
    message = timestamp + method + request_path
    signature = hmac.new(
        api_secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # Make request
    url = f"https://api.coinbase.com{request_path}"
    headers = {
        "CB-ACCESS-KEY": api_key,
        "CB-ACCESS-SIGN": signature,
        "CB-ACCESS-TIMESTAMP": timestamp,
        "CB-VERSION": "2024-01-01",
        "Content-Type": "application/json"
    }

    req = urllib.request.Request(url, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f"Coinbase API error ({e.code}): {error_body}")


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        currency_filter = input_data.get("currency")  # Optional filter

        # Get credentials
        api_key = os.environ.get("COINBASE_API_KEY")
        api_secret = os.environ.get("COINBASE_API_SECRET")

        if not api_key or not api_secret:
            print(json.dumps({
                "status": "error",
                "message": "COINBASE_API_KEY or COINBASE_API_SECRET not configured"
            }))
            sys.exit(1)

        # Fetch balances
        response = get_coinbase_balances(api_key, api_secret)

        # Parse accounts
        balances = {}
        for account in response.get("data", []):
            currency = account.get("currency", {}).get("code", account.get("currency"))
            amount = float(account.get("balance", {}).get("amount", 0))

            # Skip zero balances unless specifically requested
            if amount > 0 or (currency_filter and currency == currency_filter):
                balances[currency] = amount

        # Filter if specific currency requested
        if currency_filter:
            if currency_filter in balances:
                print(json.dumps({
                    "status": "success",
                    "currency": currency_filter,
                    "balance": balances[currency_filter]
                }))
            else:
                print(json.dumps({
                    "status": "success",
                    "currency": currency_filter,
                    "balance": 0,
                    "message": f"No {currency_filter} balance found"
                }))
        else:
            print(json.dumps({
                "status": "success",
                "balances": balances
            }))

    except json.JSONDecodeError as e:
        print(json.dumps({"status": "error", "message": f"Invalid JSON input: {e}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
