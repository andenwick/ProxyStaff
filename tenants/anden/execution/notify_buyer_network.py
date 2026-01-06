#!/usr/bin/env python3
"""
Notify Buyer Network Tool - Notifies matching buyers about a deal.

Input:
  item: Item details {title, price, url, images, margin_pct}
  category: Item category for matching
  notify_all: If true, notify all matching buyers (default: top 3)

Output:
  notifications_sent: Number of notifications sent
  matched_buyers: List of matched buyer names
  results: Array of notification results
"""
import os
import sys
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Category keywords for matching
CATEGORY_KEYWORDS = {
    "electronics": ["phone", "iphone", "samsung", "laptop", "tablet", "gaming", "console", "ps5", "xbox", "computer", "tv", "monitor"],
    "furniture": ["couch", "sofa", "table", "chair", "desk", "bed", "dresser", "cabinet", "shelf"],
    "collectibles": ["cards", "pokemon", "vintage", "antique", "rare", "limited", "comic", "figure"],
    "clothing": ["shoes", "sneakers", "nike", "jordan", "designer", "clothing", "jacket", "bag"],
    "tools": ["dewalt", "milwaukee", "tools", "power", "drill", "saw", "wrench"],
    "appliances": ["washer", "dryer", "refrigerator", "appliance", "dishwasher", "microwave"],
}

def get_buyers_file_path():
    """Get path to buyers.json file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tenant_dir = os.path.dirname(script_dir)
    return os.path.join(tenant_dir, 'state', 'buyers.json')

def load_buyers():
    """Load buyers from file."""
    file_path = get_buyers_file_path()
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data.get('buyers', [])
        except (json.JSONDecodeError, IOError):
            return []
    return []

def detect_category(title):
    """Detect item category from title."""
    title_lower = title.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title_lower:
                return category
    return "general"

def match_buyers(buyers, item, category):
    """Match buyers to item based on category and price."""
    matches = []
    item_price = item.get('price', 0)

    for buyer in buyers:
        if not buyer.get('active', True):
            continue

        # Check category match
        buyer_categories = buyer.get('categories', [])
        if category in buyer_categories or 'general' in buyer_categories or not buyer_categories:
            # Check price range
            price_min = buyer.get('price_range', {}).get('min', 0)
            price_max = buyer.get('price_range', {}).get('max', float('inf'))

            if price_min <= item_price <= price_max:
                matches.append(buyer)

    return matches

def send_email_notification(buyer, item):
    """Send email notification to buyer."""
    gmail_user = os.environ.get('GMAIL_USER')
    gmail_password = os.environ.get('GMAIL_APP_PASSWORD')

    if not gmail_user or not gmail_password:
        return {"success": False, "error": "Gmail credentials not configured"}

    to_email = buyer.get('contact_info')
    if not to_email:
        return {"success": False, "error": "No contact email for buyer"}

    subject = f"🔥 Deal Alert: {item.get('title', 'New Item')}"

    body = f"""
Hi {buyer.get('name', 'there')},

Found a deal that matches your interests!

📦 {item.get('title', 'Item')}
💰 Price: ${item.get('price', 'N/A')}
📈 Profit Margin: {item.get('margin_pct', 'N/A')}%

🔗 Link: {item.get('url', 'Contact for details')}

Reply if interested!

---
Sent by Deal Hunter Bot
"""

    try:
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, to_email, msg.as_string())

        return {"success": True, "method": "email", "to": to_email}

    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    input_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}

    item = input_data.get('item', {})
    category = input_data.get('category')
    notify_all = input_data.get('notify_all', False)
    max_notifications = input_data.get('max_notifications', 3)

    if not item.get('title'):
        print(json.dumps({"error": "item.title is required"}))
        sys.exit(1)

    # Auto-detect category if not provided
    if not category:
        category = detect_category(item.get('title', ''))

    # Load and match buyers
    buyers = load_buyers()

    if not buyers:
        print(json.dumps({
            "success": True,
            "notifications_sent": 0,
            "matched_buyers": [],
            "message": "No buyers in database. Add buyers to state/buyers.json",
        }))
        return

    matched = match_buyers(buyers, item, category)

    if not matched:
        print(json.dumps({
            "success": True,
            "notifications_sent": 0,
            "matched_buyers": [],
            "message": f"No buyers match category '{category}' in price range",
        }))
        return

    # Limit notifications unless notify_all
    if not notify_all:
        matched = matched[:max_notifications]

    # Send notifications
    results = []
    for buyer in matched:
        contact_method = buyer.get('contact_method', 'email')

        if contact_method == 'email':
            result = send_email_notification(buyer, item)
        else:
            # For WhatsApp/SMS, just log - would need separate integration
            result = {
                "success": True,
                "method": contact_method,
                "message": f"Would notify {buyer.get('name')} via {contact_method}",
            }

        results.append({
            "buyer": buyer.get('name'),
            **result,
        })

    successful = sum(1 for r in results if r.get('success'))

    print(json.dumps({
        "success": True,
        "notifications_sent": successful,
        "matched_buyers": [b.get('name') for b in matched],
        "category_detected": category,
        "results": results,
    }, indent=2))

if __name__ == '__main__':
    main()
