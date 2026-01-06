#!/usr/bin/env python3
"""
Save Deal Tool - Saves a deal to the deals database.

Input:
  title: Item title
  source: "facebook" | "craigslist" | "offerup" | "bstock"
  url: Listing URL
  buy_price: Purchase price
  estimated_sell: Expected sell price
  margin_pct: Profit margin percentage
  images: Array of image URLs (optional)
  notes: Additional notes (optional)

Output:
  success: True/False
  deal_id: Generated deal ID
  message: Status message
"""
import os
import sys
import json
from datetime import datetime
import uuid

def get_deals_file_path():
    """Get path to deals.json file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tenant_dir = os.path.dirname(script_dir)
    state_dir = os.path.join(tenant_dir, 'state')

    # Create state directory if it doesn't exist
    if not os.path.exists(state_dir):
        os.makedirs(state_dir)

    return os.path.join(state_dir, 'deals.json')

def load_deals():
    """Load existing deals from file."""
    file_path = get_deals_file_path()

    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"deals": []}

    return {"deals": []}

def save_deals(data):
    """Save deals to file."""
    file_path = get_deals_file_path()

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    input_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}

    # Required fields
    title = input_data.get('title')
    source = input_data.get('source')
    url = input_data.get('url')
    buy_price = input_data.get('buy_price')
    estimated_sell = input_data.get('estimated_sell')
    margin_pct = input_data.get('margin_pct')

    # Optional fields
    images = input_data.get('images', [])
    notes = input_data.get('notes', '')

    # Validate required fields
    if not all([title, source, buy_price, estimated_sell, margin_pct]):
        print(json.dumps({
            "error": "Missing required fields: title, source, buy_price, estimated_sell, margin_pct"
        }))
        sys.exit(1)

    # Generate deal ID
    deal_id = f"deal_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"

    # Create deal object
    deal = {
        "id": deal_id,
        "title": title,
        "source": source,
        "url": url or "",
        "buy_price": float(buy_price),
        "estimated_sell": float(estimated_sell),
        "margin_pct": float(margin_pct),
        "status": "found",  # found | approved | purchased | listed | sold | rejected
        "images": images,
        "notes": notes,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    # Load existing deals and add new one
    data = load_deals()
    data["deals"].append(deal)
    save_deals(data)

    result = {
        "success": True,
        "deal_id": deal_id,
        "message": f"Deal saved: {title}",
        "deal": deal,
    }

    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
