#!/usr/bin/env python3
"""
Manage Buyer Tool - Add, update, or remove buyers from the network.

Input:
  action: "add" | "update" | "remove" | "list"
  name: Buyer name (required for add/update/remove)
  categories: Array of categories they buy (for add/update)
  price_range: {min, max} price range (for add/update)
  contact_method: "email" | "whatsapp" | "sms" (for add/update)
  contact_info: Email or phone number (for add/update)
  notes: Additional notes (for add/update)

Output:
  success: True/False
  message: Status message
  buyers: Updated list of buyers (for list action)
"""
import os
import sys
import json
from datetime import datetime

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
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"buyers": []}
    return {"buyers": []}

def save_buyers(data):
    """Save buyers to file."""
    file_path = get_buyers_file_path()
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    input_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}

    action = input_data.get('action', 'list')
    name = input_data.get('name')

    data = load_buyers()
    buyers = data.get('buyers', [])

    if action == 'list':
        print(json.dumps({
            "success": True,
            "count": len(buyers),
            "buyers": buyers,
        }, indent=2))
        return

    if action == 'add':
        if not name:
            print(json.dumps({"error": "name is required for add action"}))
            sys.exit(1)

        # Check if buyer already exists
        for buyer in buyers:
            if buyer.get('name', '').lower() == name.lower():
                print(json.dumps({"error": f"Buyer '{name}' already exists"}))
                sys.exit(1)

        new_buyer = {
            "name": name,
            "categories": input_data.get('categories', []),
            "price_range": input_data.get('price_range', {"min": 0, "max": 10000}),
            "contact_method": input_data.get('contact_method', 'email'),
            "contact_info": input_data.get('contact_info', ''),
            "notes": input_data.get('notes', ''),
            "active": True,
            "created_at": datetime.now().isoformat(),
        }

        buyers.append(new_buyer)
        data['buyers'] = buyers
        save_buyers(data)

        print(json.dumps({
            "success": True,
            "message": f"Added buyer: {name}",
            "buyer": new_buyer,
        }, indent=2))
        return

    if action == 'update':
        if not name:
            print(json.dumps({"error": "name is required for update action"}))
            sys.exit(1)

        found = False
        for buyer in buyers:
            if buyer.get('name', '').lower() == name.lower():
                # Update fields if provided
                if 'categories' in input_data:
                    buyer['categories'] = input_data['categories']
                if 'price_range' in input_data:
                    buyer['price_range'] = input_data['price_range']
                if 'contact_method' in input_data:
                    buyer['contact_method'] = input_data['contact_method']
                if 'contact_info' in input_data:
                    buyer['contact_info'] = input_data['contact_info']
                if 'notes' in input_data:
                    buyer['notes'] = input_data['notes']
                if 'active' in input_data:
                    buyer['active'] = input_data['active']

                buyer['updated_at'] = datetime.now().isoformat()
                found = True

                data['buyers'] = buyers
                save_buyers(data)

                print(json.dumps({
                    "success": True,
                    "message": f"Updated buyer: {name}",
                    "buyer": buyer,
                }, indent=2))
                return

        if not found:
            print(json.dumps({"error": f"Buyer '{name}' not found"}))
            sys.exit(1)

    if action == 'remove':
        if not name:
            print(json.dumps({"error": "name is required for remove action"}))
            sys.exit(1)

        original_count = len(buyers)
        buyers = [b for b in buyers if b.get('name', '').lower() != name.lower()]

        if len(buyers) == original_count:
            print(json.dumps({"error": f"Buyer '{name}' not found"}))
            sys.exit(1)

        data['buyers'] = buyers
        save_buyers(data)

        print(json.dumps({
            "success": True,
            "message": f"Removed buyer: {name}",
        }, indent=2))
        return

    print(json.dumps({"error": f"Unknown action: {action}"}))
    sys.exit(1)

if __name__ == '__main__':
    main()
