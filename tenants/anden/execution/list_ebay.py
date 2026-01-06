#!/usr/bin/env python3
"""
List on eBay Tool - Creates an eBay listing via browser automation.

Input:
  title: Listing title (max 80 chars)
  description: Item description
  price: Buy It Now price
  condition: "new" | "like_new" | "good" | "acceptable"
  category: eBay category (optional, auto-detected)
  images: Array of image URLs (optional)
  shipping_cost: Shipping price (default: 0 for free shipping)
  quantity: Number of items (default: 1)
  accept_offers: Enable Best Offer (default: true)
  deal_id: Associated deal ID for tracking (optional)

Output:
  success: True/False
  listing_id: eBay listing ID
  url: Listing URL
  message: Status message
"""
import os
import sys
import json
import requests
from datetime import datetime

# eBay condition mapping
CONDITION_MAP = {
    "new": "New",
    "like_new": "Open box",
    "good": "Pre-owned",
    "acceptable": "For parts or not working",
}

def get_listings_file_path():
    """Get path to listings.json file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tenant_dir = os.path.dirname(script_dir)
    return os.path.join(tenant_dir, 'state', 'listings.json')

def load_listings():
    """Load listings from file."""
    file_path = get_listings_file_path()
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"listings": []}
    return {"listings": []}

def save_listings(data):
    """Save listings to file."""
    file_path = get_listings_file_path()
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def create_ebay_listing(session_id, tenant_id, api_base, listing_data):
    """Navigate eBay and create listing via browser automation."""

    # This is a simplified version - in production would need full form automation
    # For now, we'll navigate to the sell page and provide instructions

    steps = []

    # Step 1: Navigate to eBay sell page
    response = requests.post(
        f"{api_base}/api/tools/browser/open",
        json={
            'tenant_id': tenant_id,
            'url': 'https://www.ebay.com/sl/sell',
            'session_id': session_id,
        },
        timeout=60
    )

    if not response.json().get('success'):
        return None, "Failed to open eBay sell page"

    steps.append("Opened eBay sell page")

    # Wait for page load
    requests.post(
        f"{api_base}/api/tools/browser/wait",
        json={
            'tenant_id': tenant_id,
            'session_id': session_id,
            'timeout': 5000,
        },
        timeout=30
    )

    # Read page to check if logged in
    read_response = requests.post(
        f"{api_base}/api/tools/browser/read",
        json={
            'tenant_id': tenant_id,
            'session_id': session_id,
            'max_length': 10000,
        },
        timeout=30
    )

    content = read_response.json().get('content', '')

    # Check if we need to log in
    if 'sign in' in content.lower() or 'log in' in content.lower():
        return None, "eBay login required. Please log in first using browser_login with service='ebay'"

    steps.append("Verified logged in to eBay")

    # For MVP, return the listing data formatted for manual entry
    # Full automation would require filling forms via browser_type and browser_click

    return {
        "steps_completed": steps,
        "listing_data": listing_data,
        "next_action": "Complete listing form with provided data",
    }, None

def main():
    input_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}

    # Required fields
    title = input_data.get('title')
    description = input_data.get('description', '')
    price = input_data.get('price')

    # Optional fields
    condition = input_data.get('condition', 'good')
    category = input_data.get('category', '')
    images = input_data.get('images', [])
    shipping_cost = input_data.get('shipping_cost', 0)
    quantity = input_data.get('quantity', 1)
    accept_offers = input_data.get('accept_offers', True)
    deal_id = input_data.get('deal_id', '')

    if not title or price is None:
        print(json.dumps({"error": "title and price are required"}))
        sys.exit(1)

    # Truncate title to 80 chars
    if len(title) > 80:
        title = title[:77] + "..."

    tenant_id = os.environ.get('TENANT_ID')
    api_base = os.environ.get('API_BASE_URL', 'http://localhost:3000')

    if not tenant_id:
        print(json.dumps({"error": "TENANT_ID not set"}))
        sys.exit(1)

    # Prepare listing data
    listing_data = {
        "title": title,
        "description": description,
        "price": float(price),
        "condition": CONDITION_MAP.get(condition, "Pre-owned"),
        "category": category,
        "images": images,
        "shipping": "Free" if shipping_cost == 0 else f"${shipping_cost}",
        "quantity": quantity,
        "best_offer": accept_offers,
    }

    try:
        # Open browser session
        open_response = requests.post(
            f"{api_base}/api/tools/browser/open",
            json={
                'tenant_id': tenant_id,
                'url': 'https://www.ebay.com/sl/sell',
                'persistent': True,  # Keep session for form filling
            },
            timeout=60
        )

        open_data = open_response.json()
        if not open_data.get('success'):
            print(json.dumps({"error": f"Failed to open browser: {open_data.get('error')}"}))
            sys.exit(1)

        session_id = open_data['session_id']

        # Attempt to create listing
        result, error = create_ebay_listing(session_id, tenant_id, api_base, listing_data)

        if error:
            print(json.dumps({
                "success": False,
                "error": error,
                "session_id": session_id,
                "listing_data": listing_data,
            }))
            sys.exit(1)

        # Generate a placeholder listing ID (in production, would extract from eBay)
        listing_id = f"ebay_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Save to listings database
        data = load_listings()
        new_listing = {
            "id": listing_id,
            "platform": "ebay",
            "deal_id": deal_id,
            "title": title,
            "price": float(price),
            "status": "draft",  # draft until confirmed live
            "url": f"https://www.ebay.com/itm/{listing_id}",
            "created_at": datetime.now().isoformat(),
            "session_id": session_id,  # For continuing the listing
        }
        data['listings'].append(new_listing)
        save_listings(data)

        print(json.dumps({
            "success": True,
            "listing_id": listing_id,
            "status": "draft",
            "session_id": session_id,
            "message": "eBay sell page opened. Complete the listing form with the provided data.",
            "listing_data": listing_data,
            "next_steps": [
                "1. Enter title in the search box",
                "2. Select category",
                "3. Fill in condition and description",
                "4. Set price and shipping",
                "5. Upload photos",
                "6. Click 'List it'",
            ],
        }, indent=2))

    except requests.exceptions.RequestException as e:
        print(json.dumps({"error": f"API request failed: {str(e)}"}))
        sys.exit(1)

if __name__ == '__main__':
    main()
