#!/usr/bin/env python3
"""
Analyze Buyer Demand Tool - Analyzes market demand for an item.

Input:
  keywords: Item keywords to analyze
  category: Optional category filter

Output:
  demand_score: 1-10 rating of demand
  avg_days_to_sell: Average days items stay listed
  search_volume: Relative search popularity
  price_sensitivity: How price-sensitive buyers are
  recommended_price: Suggested listing price
  buyer_insights: Key observations about buyers
"""
import os
import sys
import json
import requests
import re
from urllib.parse import quote

def build_ebay_search_url(keywords):
    """Build eBay active listings search URL."""
    base = "https://www.ebay.com/sch/i.html"
    params = [
        f"_nkw={quote(keywords)}",
        "_sop=12",  # Sort by: Best Match
    ]
    return f"{base}?{'&'.join(params)}"

def analyze_listing_data(content, keywords):
    """Analyze listing data to determine demand."""

    # Count active listings
    listing_count_match = re.search(r'([\d,]+)\s*results', content.lower())
    active_listings = 0
    if listing_count_match:
        active_listings = int(listing_count_match.group(1).replace(',', ''))

    # Extract prices
    price_pattern = r'\$[\d,]+(?:\.\d{2})?'
    prices = []
    for price_str in re.findall(price_pattern, content)[:30]:
        try:
            price = float(price_str.replace('$', '').replace(',', ''))
            if 1 < price < 50000:
                prices.append(price)
        except ValueError:
            continue

    # Calculate demand indicators
    if not prices:
        return {
            "demand_score": 5,
            "active_listings": active_listings,
            "avg_price": 0,
            "price_range": {"min": 0, "max": 0},
            "search_volume": "unknown",
            "buyer_insights": ["Insufficient data to analyze demand"],
        }

    avg_price = sum(prices) / len(prices)
    min_price = min(prices)
    max_price = max(prices)
    price_spread = (max_price - min_price) / avg_price if avg_price > 0 else 0

    # Determine demand score based on listings count
    # Fewer listings with high prices = high demand
    # Many listings with low prices = saturated market
    if active_listings < 100:
        base_demand = 8  # Low supply = potential high demand
    elif active_listings < 500:
        base_demand = 6
    elif active_listings < 2000:
        base_demand = 5
    else:
        base_demand = 3  # Very saturated market

    # Adjust for price consistency
    if price_spread < 0.3:
        demand_score = min(10, base_demand + 1)  # Consistent pricing = stable demand
        price_sensitivity = "low"
    elif price_spread < 0.6:
        demand_score = base_demand
        price_sensitivity = "medium"
    else:
        demand_score = max(1, base_demand - 1)  # Wild price variation = unstable
        price_sensitivity = "high"

    # Generate insights
    insights = []
    if active_listings < 50:
        insights.append("Low competition - rare item or niche market")
    elif active_listings > 1000:
        insights.append("High competition - price competitively")

    if price_spread > 0.5:
        insights.append("Wide price range - condition matters a lot")

    if avg_price > 500:
        insights.append("High-value item - buyers may negotiate")
    elif avg_price < 50:
        insights.append("Low-value item - impulse buy potential")

    return {
        "demand_score": demand_score,
        "active_listings": active_listings,
        "avg_price": round(avg_price, 2),
        "price_range": {"min": round(min_price, 2), "max": round(max_price, 2)},
        "price_sensitivity": price_sensitivity,
        "recommended_price": round(avg_price * 0.95, 2),  # Slightly below average
        "buyer_insights": insights if insights else ["Standard market conditions"],
    }

def main():
    input_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}

    keywords = input_data.get('keywords')
    category = input_data.get('category', '')

    if not keywords:
        print(json.dumps({"error": "keywords is required"}))
        sys.exit(1)

    tenant_id = os.environ.get('TENANT_ID')
    api_base = os.environ.get('API_BASE_URL', 'http://localhost:3000')

    if not tenant_id:
        print(json.dumps({"error": "TENANT_ID not set"}))
        sys.exit(1)

    search_query = f"{keywords} {category}".strip()
    url = build_ebay_search_url(search_query)

    try:
        # Open browser
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

        # Wait for page
        requests.post(
            f"{api_base}/api/tools/browser/wait",
            json={
                'tenant_id': tenant_id,
                'session_id': session_id,
                'timeout': 5000,
            },
            timeout=30
        )

        # Read content
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

        # Close browser
        requests.post(
            f"{api_base}/api/tools/browser/close",
            json={
                'tenant_id': tenant_id,
                'session_id': session_id,
            },
            timeout=10
        )

        # Analyze demand
        analysis = analyze_listing_data(content, keywords)

        result = {
            "success": True,
            "keywords": keywords,
            "category": category,
            "url": url,
            **analysis,
        }

        print(json.dumps(result, indent=2))

    except requests.exceptions.RequestException as e:
        print(json.dumps({"error": f"API request failed: {str(e)}"}))
        sys.exit(1)

if __name__ == '__main__':
    main()
