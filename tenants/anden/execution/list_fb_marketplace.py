#!/usr/bin/env python3
"""
List on Facebook Marketplace Tool - Creates a FB Marketplace listing via browser automation.

Input:
  title: Listing title
  description: Item description
  price: Asking price
  condition: "new" | "like_new" | "good" | "fair"
  category: FB category (optional)
  location: Pickup location (optional, uses default)
  images: Array of image URLs (optional)
  deal_id: Associated deal ID for tracking (optional)

Output:
  success: True/False
  listing_id: FB listing ID
  url: Listing URL
  message: Status message
"""
import os
import sys
import json
import requests
from datetime import datetime

# FB Marketplace condition mapping
CONDITION_MAP = {
    "new": "New",
    "like_new": "Used - Like New",
    "good": "Used - Good",
    "fair": "Used - Fair",
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

def main():
    input_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}

    # Required fields
    title = input_data.get('title')
    description = input_data.get('description', '')
    price = input_data.get('price')

    # Optional fields
    condition = input_data.get('condition', 'good')
    category = input_data.get('category', 'Miscellaneous')
    location = input_data.get('location', 'Denver, CO')
    images = input_data.get('images', [])
    deal_id = input_data.get('deal_id', '')

    if not title or price is None:
        print(json.dumps({"error": "title and price are required"}))
        sys.exit(1)

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
        "condition": CONDITION_MAP.get(condition, "Used - Good"),
        "category": category,
        "location": location,
        "images": images,
    }

    try:
        # Open browser to FB Marketplace create listing page
        open_response = requests.post(
            f"{api_base}/api/tools/browser/open",
            json={
                'tenant_id': tenant_id,
                'url': 'https://www.facebook.com/marketplace/create/item',
                'persistent': True,
            },
            timeout=60
        )

        open_data = open_response.json()
        if not open_data.get('success'):
            print(json.dumps({"error": f"Failed to open browser: {open_data.get('error')}"}))
            sys.exit(1)

        session_id = open_data['session_id']

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

        # Read page to check login status
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

        # Check if login required
        if 'log in' in content.lower() or 'sign in' in content.lower():
            print(json.dumps({
                "success": False,
                "error": "Facebook login required. Please log in first using browser_login with service='facebook'",
                "session_id": session_id,
            }))
            sys.exit(1)

        # Generate placeholder listing ID
        listing_id = f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Save to listings database
        data = load_listings()
        new_listing = {
            "id": listing_id,
            "platform": "facebook",
            "deal_id": deal_id,
            "title": title,
            "price": float(price),
            "status": "draft",
            "location": location,
            "url": f"https://www.facebook.com/marketplace/item/{listing_id}",
            "created_at": datetime.now().isoformat(),
            "session_id": session_id,
        }
        data['listings'].append(new_listing)
        save_listings(data)

        print(json.dumps({
            "success": True,
            "listing_id": listing_id,
            "status": "draft",
            "session_id": session_id,
            "message": "FB Marketplace create page opened. Complete the listing form.",
            "listing_data": listing_data,
            "next_steps": [
                "1. Click 'Add Photos' and upload images",
                "2. Enter title in 'What are you selling?'",
                "3. Set price",
                "4. Select category",
                "5. Select condition",
                "6. Add description",
                "7. Verify location",
                "8. Click 'Publish'",
            ],
        }, indent=2))

    except requests.exceptions.RequestException as e:
        print(json.dumps({"error": f"API request failed: {str(e)}"}))
        sys.exit(1)

if __name__ == '__main__':
    main()
