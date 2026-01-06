#!/usr/bin/env python3
"""
Update Inventory Tool - Updates deal or listing status.

Input:
  deal_id: Deal ID to update (required)
  status: New status (found, approved, rejected, purchased, listed, sold, expired)
  listing_ids: Array of platform listing IDs (for 'listed' status)
  listing_urls: Array of listing URLs (for 'listed' status)
  sold_price: Actual sale price (for 'sold' status)
  sold_platform: Where it sold (for 'sold' status)
  notes: Additional notes

Output:
  success: True/False
  deal: Updated deal object
  message: Status message
"""
import os
import sys
import json
from datetime import datetime

VALID_STATUSES = ['found', 'approved', 'rejected', 'purchased', 'listed', 'sold', 'expired']

def get_deals_file_path():
    """Get path to deals.json file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tenant_dir = os.path.dirname(script_dir)
    return os.path.join(tenant_dir, 'state', 'deals.json')

def get_listings_file_path():
    """Get path to listings.json file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tenant_dir = os.path.dirname(script_dir)
    return os.path.join(tenant_dir, 'state', 'listings.json')

def load_deals():
    """Load deals from file."""
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

def calculate_profit(deal, sold_price):
    """Calculate actual profit from sale."""
    buy_price = deal.get('buy_price', 0)
    # Estimate fees at 15% for eBay, 5% for FB
    estimated_fees = sold_price * 0.13
    actual_profit = sold_price - buy_price - estimated_fees
    actual_margin = (actual_profit / buy_price * 100) if buy_price > 0 else 0

    return {
        "actual_profit": round(actual_profit, 2),
        "actual_margin_pct": round(actual_margin, 1),
        "estimated_fees": round(estimated_fees, 2),
    }

def main():
    input_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}

    deal_id = input_data.get('deal_id')
    status = input_data.get('status')

    if not deal_id:
        print(json.dumps({"error": "deal_id is required"}))
        sys.exit(1)

    if status and status not in VALID_STATUSES:
        print(json.dumps({"error": f"Invalid status. Valid: {VALID_STATUSES}"}))
        sys.exit(1)

    # Load deals
    data = load_deals()
    deals = data.get('deals', [])

    # Find the deal
    deal = None
    deal_index = None
    for i, d in enumerate(deals):
        if d.get('id') == deal_id:
            deal = d
            deal_index = i
            break

    if deal is None:
        print(json.dumps({"error": f"Deal not found: {deal_id}"}))
        sys.exit(1)

    # Update deal fields
    old_status = deal.get('status')

    if status:
        deal['status'] = status
        deal['status_updated_at'] = datetime.now().isoformat()

        # Track status history
        if 'status_history' not in deal:
            deal['status_history'] = []
        deal['status_history'].append({
            "from": old_status,
            "to": status,
            "at": datetime.now().isoformat(),
        })

    # Handle status-specific updates
    if status == 'listed':
        listing_ids = input_data.get('listing_ids', [])
        listing_urls = input_data.get('listing_urls', [])
        deal['listing_ids'] = listing_ids
        deal['listing_urls'] = listing_urls
        deal['listed_at'] = datetime.now().isoformat()

    elif status == 'sold':
        sold_price = input_data.get('sold_price')
        sold_platform = input_data.get('sold_platform', 'unknown')

        if sold_price:
            deal['sold_price'] = float(sold_price)
            deal['sold_platform'] = sold_platform
            deal['sold_at'] = datetime.now().isoformat()

            # Calculate actual profit
            profit_data = calculate_profit(deal, float(sold_price))
            deal.update(profit_data)

            # Update associated listings
            listings_data = load_listings()
            for listing in listings_data.get('listings', []):
                if listing.get('deal_id') == deal_id:
                    listing['status'] = 'sold'
                    listing['sold_at'] = datetime.now().isoformat()
            save_listings(listings_data)

    elif status == 'approved':
        deal['approved_at'] = datetime.now().isoformat()

    elif status == 'rejected':
        deal['rejected_at'] = datetime.now().isoformat()
        deal['rejection_reason'] = input_data.get('notes', '')

    elif status == 'purchased':
        deal['purchased_at'] = datetime.now().isoformat()

    # Add notes if provided
    if 'notes' in input_data:
        if 'notes' not in deal:
            deal['notes'] = ''
        deal['notes'] += f"\n[{datetime.now().strftime('%Y-%m-%d')}] {input_data['notes']}"

    # Update timestamp
    deal['updated_at'] = datetime.now().isoformat()

    # Save updated deal
    deals[deal_index] = deal
    data['deals'] = deals
    save_deals(data)

    # Generate summary message
    message = f"Deal '{deal.get('title')}' updated to {status}"
    if status == 'sold' and 'actual_profit' in deal:
        message += f" | Profit: ${deal['actual_profit']} ({deal['actual_margin_pct']}%)"

    print(json.dumps({
        "success": True,
        "deal": deal,
        "message": message,
    }, indent=2))

if __name__ == '__main__':
    main()
