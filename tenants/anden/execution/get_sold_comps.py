#!/usr/bin/env python3
"""
Get Sold Comps Tool - Fetches eBay sold listings for price comparison.

Input:
  keywords: Search keywords (e.g., "iPhone 12 Pro 128GB")
  condition: "new" | "used" | "refurbished" | "any" (default: "any")
  days_back: How many days to look back (default: 30)

Output:
  avg_price: Average sold price
  median_price: Median sold price
  min_price: Lowest sold price
  max_price: Highest sold price
  sold_count: Number of sales found
  comps: Array of {title, price, date, url}
"""
import os
import sys
import json
import requests
import re
from urllib.parse import quote

def build_ebay_sold_url(keywords, condition):
    """Build eBay sold listings search URL."""
    base = "https://www.ebay.com/sch/i.html"

    # LH_Sold=1 and LH_Complete=1 show sold listings only
    params = [
        f"_nkw={quote(keywords)}",
        "LH_Sold=1",
        "LH_Complete=1",
        "_sop=13",  # Sort by date: newest first
    ]

    # Condition filter
    if condition == "new":
        params.append("LH_ItemCondition=1000")
    elif condition == "used":
        params.append("LH_ItemCondition=3000")
    elif condition == "refurbished":
        params.append("LH_ItemCondition=2500")

    return f"{base}?{'&'.join(params)}"

def parse_sold_prices(content):
    """Parse sold prices from eBay page content."""
    prices = []

    # Look for sold price patterns
    # eBay shows: "$XXX.XX" or "$X,XXX.XX" for sold items
    price_pattern = r'\$[\d,]+(?:\.\d{2})?'
    found_prices = re.findall(price_pattern, content)

    for price_str in found_prices[:50]:  # Limit to 50 prices
        try:
            # Remove $ and commas, convert to float
            price = float(price_str.replace('$', '').replace(',', ''))
            if price > 0 and price < 100000:  # Sanity check
                prices.append(price)
        except ValueError:
            continue

    return prices

def calculate_stats(prices):
    """Calculate price statistics."""
    if not prices:
        return {
            "avg_price": 0,
            "median_price": 0,
            "min_price": 0,
            "max_price": 0,
            "sold_count": 0,
        }

    sorted_prices = sorted(prices)
    count = len(sorted_prices)

    return {
        "avg_price": round(sum(sorted_prices) / count, 2),
        "median_price": round(sorted_prices[count // 2], 2),
        "min_price": round(sorted_prices[0], 2),
        "max_price": round(sorted_prices[-1], 2),
        "sold_count": count,
    }

def main():
    input_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}

    keywords = input_data.get('keywords')
    condition = input_data.get('condition', 'any')
    days_back = input_data.get('days_back', 30)

    if not keywords:
        print(json.dumps({"error": "keywords is required"}))
        sys.exit(1)

    tenant_id = os.environ.get('TENANT_ID')
    api_base = os.environ.get('API_BASE_URL', 'http://localhost:3000')

    if not tenant_id:
        print(json.dumps({"error": "TENANT_ID not set"}))
        sys.exit(1)

    url = build_ebay_sold_url(keywords, condition)

    try:
        # Step 1: Open browser
        open_response = requests.post(
            f"{api_base}/api/tools/browser/open",
            json={
                'tenant_id': tenant_id,
                'url': url,
                'persistent': False,
            },
            timeout=60
        )

        open_data = open_response.json()
        if not open_data.get('success'):
            print(json.dumps({"error": f"Failed to open browser: {open_data.get('error')}"}))
            sys.exit(1)

        session_id = open_data['session_id']

        # Step 2: Wait for page
        requests.post(
            f"{api_base}/api/tools/browser/wait",
            json={
                'tenant_id': tenant_id,
                'session_id': session_id,
                'timeout': 5000,
            },
            timeout=30
        )

        # Step 3: Read page content
        read_response = requests.post(
            f"{api_base}/api/tools/browser/read",
            json={
                'tenant_id': tenant_id,
                'session_id': session_id,
                'max_length': 100000,
            },
            timeout=30
        )

        read_data = read_response.json()
        content = read_data.get('content', '')

        # Step 4: Close browser
        requests.post(
            f"{api_base}/api/tools/browser/close",
            json={
                'tenant_id': tenant_id,
                'session_id': session_id,
            },
            timeout=10
        )

        # Step 5: Parse prices and calculate stats
        prices = parse_sold_prices(content)
        stats = calculate_stats(prices)

        result = {
            "success": True,
            "keywords": keywords,
            "condition": condition,
            "url": url,
            **stats,
            "raw_prices": prices[:20],  # First 20 prices for verification
            "needs_ai_verification": len(prices) < 5,  # Flag if few results
        }

        print(json.dumps(result, indent=2))

    except requests.exceptions.RequestException as e:
        print(json.dumps({"error": f"API request failed: {str(e)}"}))
        sys.exit(1)

if __name__ == '__main__':
    main()
