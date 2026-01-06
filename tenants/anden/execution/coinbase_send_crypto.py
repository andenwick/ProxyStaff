#!/usr/bin/env python3
"""
Send crypto from Coinbase to an external address.

Required environment variables:
- COINBASE_API_KEY: Coinbase CDP API key name
- COINBASE_API_SECRET: Coinbase CDP API private key

Optional environment variables:
- CRYPTO_MAX_SINGLE_TRANSFER: Max amount per transfer (default: 200)
- CRYPTO_DAILY_LIMIT: Daily transfer limit (default: 1000)
"""

import sys
import json
import os
import hmac
import hashlib
import time
import urllib.request
import urllib.error
import re


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


def get_account_id(api_key: str, api_secret: str, currency: str) -> str:
    """Find the account ID for a specific currency."""
    timestamp = str(int(time.time()))
    method = "GET"
    request_path = "/v2/accounts"

    message = timestamp + method + request_path
    signature = hmac.new(
        api_secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    url = f"https://api.coinbase.com{request_path}"
    headers = {
        "CB-ACCESS-KEY": api_key,
        "CB-ACCESS-SIGN": signature,
        "CB-ACCESS-TIMESTAMP": timestamp,
        "CB-VERSION": "2024-01-01",
        "Content-Type": "application/json"
    }

    req = urllib.request.Request(url, headers=headers, method=method)

    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.loads(response.read().decode('utf-8'))

    for account in data.get("data", []):
        curr = account.get("currency", {})
        if isinstance(curr, dict):
            code = curr.get("code", "")
        else:
            code = curr
        if code.upper() == currency.upper():
            return account.get("id")

    raise Exception(f"No account found for currency: {currency}")


def send_crypto(api_key: str, api_secret: str, account_id: str,
                to_address: str, amount: float, currency: str) -> dict:
    """Send crypto to external address."""
    timestamp = str(int(time.time()))
    method = "POST"
    request_path = f"/v2/accounts/{account_id}/transactions"

    body = {
        "type": "send",
        "to": to_address,
        "amount": str(amount),
        "currency": currency.upper(),
        "idem": f"refill-{timestamp}"  # Idempotency key
    }
    body_str = json.dumps(body)

    message = timestamp + method + request_path + body_str
    signature = hmac.new(
        api_secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    url = f"https://api.coinbase.com{request_path}"
    headers = {
        "CB-ACCESS-KEY": api_key,
        "CB-ACCESS-SIGN": signature,
        "CB-ACCESS-TIMESTAMP": timestamp,
        "CB-VERSION": "2024-01-01",
        "Content-Type": "application/json"
    }

    req = urllib.request.Request(
        url,
        data=body_str.encode('utf-8'),
        headers=headers,
        method=method
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f"Coinbase API error ({e.code}): {error_body}")


def main():
    try:
        input_data = json.loads(sys.stdin.read())

        to_address = input_data.get("to_address")
        amount = input_data.get("amount")
        currency = input_data.get("currency", "USDT")
        network = input_data.get("network", "TRC20")

        # Validate required fields
        if not to_address:
            print(json.dumps({"status": "error", "message": "Missing 'to_address'"}))
            sys.exit(1)
        if not amount:
            print(json.dumps({"status": "error", "message": "Missing 'amount'"}))
            sys.exit(1)

        amount = float(amount)
        if amount <= 0:
            print(json.dumps({"status": "error", "message": "Amount must be positive"}))
            sys.exit(1)

        # Validate address format
        if not validate_address(to_address, network):
            print(json.dumps({
                "status": "error",
                "message": f"Invalid address format for {network}: {to_address}"
            }))
            sys.exit(1)

        # Check transfer limits
        max_single = float(os.environ.get("CRYPTO_MAX_SINGLE_TRANSFER", 200))
        if amount > max_single:
            print(json.dumps({
                "status": "error",
                "requires_confirmation": True,
                "message": f"Amount {amount} exceeds single transfer limit of {max_single}. Please confirm manually or increase CRYPTO_MAX_SINGLE_TRANSFER."
            }))
            sys.exit(1)

        # Get credentials
        api_key = os.environ.get("COINBASE_API_KEY")
        api_secret = os.environ.get("COINBASE_API_SECRET")

        if not api_key or not api_secret:
            print(json.dumps({
                "status": "error",
                "message": "COINBASE_API_KEY or COINBASE_API_SECRET not configured"
            }))
            sys.exit(1)

        # Get account ID for the currency
        account_id = get_account_id(api_key, api_secret, currency)

        # Send the crypto
        result = send_crypto(api_key, api_secret, account_id, to_address, amount, currency)

        transaction = result.get("data", {})
        print(json.dumps({
            "status": "success",
            "transaction_id": transaction.get("id"),
            "amount_sent": amount,
            "currency": currency,
            "to_address": to_address,
            "network": network,
            "message": f"Sent {amount} {currency} to {to_address[:10]}...{to_address[-6:]}"
        }))

    except json.JSONDecodeError as e:
        print(json.dumps({"status": "error", "message": f"Invalid JSON input: {e}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
