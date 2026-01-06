#!/usr/bin/env python3
"""
Scrape Marketplace Tool - Scrapes listings from local marketplaces.
Supports: Facebook Marketplace, Craigslist, OfferUp

Input:
  platform: "facebook" | "craigslist" | "offerup"
  location: City/area name (e.g., "Denver")
  radius_miles: Search radius (default: 50)
  search_terms: Optional search query
  max_results: Max listings to return (default: 20)

Output:
  items: Array of {title, price, url, image, location, posted_at}
"""
import os
import sys
import json
import requests
import re
from urllib.parse import quote

def build_marketplace_url(platform, location, search_terms, radius_miles):
    """Build the marketplace search URL."""

    if platform == "facebook":
        # Facebook Marketplace URL structure
        base = "https://www.facebook.com/marketplace"
        if search_terms:
            return f"{base}/search?query={quote(search_terms)}&exact=false"
        return f"{base}/category/propertyrentals"  # Default to browsing

    elif platform == "craigslist":
        # Craigslist URL - use city subdomain
        city = location.lower().replace(" ", "")
        base = f"https://{city}.craigslist.org/search/sss"
        if search_terms:
            return f"{base}?query={quote(search_terms)}"
        return base

    elif platform == "offerup":
        # OfferUp URL
        base = "https://offerup.com/search"
        if search_terms:
            return f"{base}?q={quote(search_terms)}"
        return base

    else:
        return None

def parse_listings(content, platform):
    """Parse listings from page content based on platform."""
    items = []

    # Simple text-based parsing - Claude can enhance with AI understanding
    # This extracts basic patterns from the page text

    # Look for price patterns: $XX, $XXX, $X,XXX
    price_pattern = r'\$[\d,]+(?:\.\d{2})?'
    prices = re.findall(price_pattern, content)

    # For now, return raw content for Claude to parse intelligently
    # In production, would use proper HTML parsing with BeautifulSoup

    return {
        "raw_content": content[:10000],  # First 10k chars for Claude to parse
        "price_hints": prices[:20],  # First 20 prices found
        "needs_ai_parsing": True
    }

def main():
    input_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}

    platform = input_data.get('platform', 'facebook')
    location = input_data.get('location', 'Denver')
    radius_miles = input_data.get('radius_miles', 50)
    search_terms = input_data.get('search_terms', '')
    max_results = input_data.get('max_results', 20)

    tenant_id = os.environ.get('TENANT_ID')
    api_base = os.environ.get('API_BASE_URL', 'http://localhost:3000')

    if not tenant_id:
        print(json.dumps({"error": "TENANT_ID not set"}))
        sys.exit(1)

    # Build marketplace URL
    url = build_marketplace_url(platform, location, search_terms, radius_miles)
    if not url:
        print(json.dumps({"error": f"Unknown platform: {platform}"}))
        sys.exit(1)

    try:
        # Step 1: Open browser and navigate
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

        # Step 2: Wait for page to load (give JS time to render)
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
                'max_length': 50000,
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

        # Step 5: Parse listings
        parsed = parse_listings(content, platform)

        result = {
            "success": True,
            "platform": platform,
            "url": url,
            "location": location,
            "search_terms": search_terms,
            "page_title": read_data.get('title', ''),
            **parsed
        }

        print(json.dumps(result, indent=2))

    except requests.exceptions.RequestException as e:
        print(json.dumps({"error": f"API request failed: {str(e)}"}))
        sys.exit(1)

if __name__ == '__main__':
    main()
