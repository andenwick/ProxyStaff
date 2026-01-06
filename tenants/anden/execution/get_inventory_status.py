#!/usr/bin/env python3
"""
Get Inventory Status Tool - Provides a summary of current deal hunting inventory.

Input:
  detailed: If true, include full deal/listing details (default: false)

Output:
  summary: Quick stats
  deals_by_status: Breakdown of deals
  recent_activity: Recent changes
  profit_tracking: Profit stats
"""
import os
import sys
import json
from datetime import datetime, timedelta

def get_state_path(filename):
    """Get path to state file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tenant_dir = os.path.dirname(script_dir)
    return os.path.join(tenant_dir, 'state', filename)

def load_json(filename):
    """Load JSON file from state directory."""
    path = get_state_path(filename)
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def calculate_age(created_at):
    """Calculate days since creation."""
    try:
        created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        now = datetime.now(created.tzinfo) if created.tzinfo else datetime.now()
        return (now - created).days
    except:
        return 0

def main():
    input_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    detailed = input_data.get('detailed', False)

    # Load state files
    deals_data = load_json('deals.json')
    listings_data = load_json('listings.json')
    buyers_data = load_json('buyers.json')
    config_data = load_json('config.json')

    deals = deals_data.get('deals', [])
    listings = listings_data.get('listings', [])
    buyers = buyers_data.get('buyers', [])

    # Count deals by status
    status_counts = {}
    for deal in deals:
        status = deal.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1

    # Calculate profits
    total_profit = 0
    sold_count = 0
    for deal in deals:
        if deal.get('status') == 'sold' and 'actual_profit' in deal:
            total_profit += deal['actual_profit']
            sold_count += 1

    # Find stale listings (> 7 days)
    stale_listings = []
    for deal in deals:
        if deal.get('status') == 'listed':
            listed_at = deal.get('listed_at', deal.get('created_at', ''))
            if listed_at and calculate_age(listed_at) > 7:
                stale_listings.append({
                    "id": deal.get('id'),
                    "title": deal.get('title'),
                    "days_listed": calculate_age(listed_at),
                })

    # Pending actions
    pending_approval = [d for d in deals if d.get('status') == 'found']
    pending_listing = [d for d in deals if d.get('status') == 'purchased']

    # Build summary
    summary = {
        "total_deals": len(deals),
        "awaiting_approval": len(pending_approval),
        "need_to_list": len(pending_listing),
        "active_listings": status_counts.get('listed', 0),
        "total_sold": sold_count,
        "total_profit": round(total_profit, 2),
        "buyer_network_size": len(buyers),
        "stale_listings": len(stale_listings),
    }

    # Recent activity (last 7 days)
    recent = []
    week_ago = datetime.now() - timedelta(days=7)
    for deal in deals:
        updated = deal.get('updated_at', deal.get('created_at', ''))
        try:
            updated_dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
            if updated_dt.replace(tzinfo=None) > week_ago:
                recent.append({
                    "id": deal.get('id'),
                    "title": deal.get('title'),
                    "status": deal.get('status'),
                    "updated": updated,
                })
        except:
            pass

    result = {
        "success": True,
        "summary": summary,
        "deals_by_status": status_counts,
        "stale_listings": stale_listings[:5],  # Top 5 stale
        "pending_approval": [{"id": d.get('id'), "title": d.get('title'), "margin": d.get('margin_pct')} for d in pending_approval[:5]],
        "pending_listing": [{"id": d.get('id'), "title": d.get('title')} for d in pending_listing[:5]],
        "recent_activity": recent[:10],
        "config": config_data.get('deal_hunting', {}),
    }

    if detailed:
        result["all_deals"] = deals
        result["all_listings"] = listings
        result["all_buyers"] = buyers

    # Generate human-readable summary
    msg = f"""📊 Inventory Status:
• {summary['awaiting_approval']} deals awaiting approval
• {summary['need_to_list']} items to list
• {summary['active_listings']} active listings
• {summary['total_sold']} sold (+${summary['total_profit']} profit)
• {summary['stale_listings']} stale listings (>7 days)"""

    result["message"] = msg

    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
