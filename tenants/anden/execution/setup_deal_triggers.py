#!/usr/bin/env python3
"""
Setup Deal Triggers Tool - Creates pre-configured triggers for deal hunting automation.

Input:
  action: "setup_all" | "deal_scanner" | "liquidation_check" | "listing_expiry" | "list" | "status"

Output:
  success: True/False
  triggers_created: Array of created trigger names
  message: Status message
"""
import os
import sys
import json
import urllib.request
import urllib.error

# Pre-configured trigger definitions
TRIGGERS = {
    "deal_scanner": {
        "name": "Deal Scanner",
        "description": "Scans FB Marketplace, Craigslist, OfferUp every 30 min for deals",
        "trigger_type": "TIME",
        "config": {
            "cron_expr": "*/30 * * * *",
            "timezone": "America/Denver"
        },
        "task_prompt": """Run a deal scan following the deal_hunting directive:
1. Call scrape_marketplace for Facebook Marketplace
2. For each item, call get_sold_comps to check prices
3. Call calculate_arbitrage to check profitability
4. For items with 50%+ margin, call save_deal and notify me
5. Send a summary of deals found""",
        "autonomy": "AUTO",
        "cooldown_seconds": 1800
    },
    "liquidation_check": {
        "name": "Liquidation Check",
        "description": "Daily check of liquidation sites at 8am",
        "trigger_type": "TIME",
        "config": {
            "cron_expr": "0 8 * * *",
            "timezone": "America/Denver"
        },
        "task_prompt": """Check liquidation sites for new deals:
1. Browse B-Stock and Liquidation.com
2. Look for electronics, appliances, or general merchandise
3. Analyze lots under $500
4. Report any with estimated 50%+ profit margin
5. Include links and key details""",
        "autonomy": "NOTIFY",
        "cooldown_seconds": 86400
    },
    "listing_expiry": {
        "name": "Listing Expiry Check",
        "description": "Daily check for stale listings at 6pm",
        "trigger_type": "TIME",
        "config": {
            "cron_expr": "0 18 * * *",
            "timezone": "America/Denver"
        },
        "task_prompt": """Check inventory status following inventory_management directive:
1. Review all deals with status 'listed'
2. Flag any listed for more than 7 days
3. Suggest price drops for stale items
4. Provide inventory summary:
   - Deals awaiting approval
   - Items to list
   - Active listings
   - Recent sales""",
        "autonomy": "NOTIFY",
        "cooldown_seconds": 86400
    }
}

def create_trigger(trigger_config, tenant_id, sender_phone, api_base_url):
    """Create a trigger via the API."""
    payload = {
        "tenant_id": tenant_id,
        "sender_phone": sender_phone,
        **trigger_config
    }

    try:
        url = f"{api_base_url}/api/tools/create-trigger"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            return True, result

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else str(e)
        return False, {"error": f"API error ({e.code}): {error_body}"}

    except Exception as e:
        return False, {"error": str(e)}

def list_triggers(tenant_id, sender_phone, api_base_url):
    """List existing triggers."""
    try:
        query = f"tenant_id={tenant_id}&sender_phone={sender_phone}"
        url = f"{api_base_url}/api/tools/list-triggers?{query}"
        req = urllib.request.Request(url, method="GET")

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            return True, result.get("triggers", [])

    except Exception as e:
        return False, str(e)

def main():
    input_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}

    action = input_data.get('action', 'status')

    tenant_id = os.environ.get('TENANT_ID')
    sender_phone = os.environ.get('SENDER_PHONE')
    api_base_url = os.environ.get('API_BASE_URL', 'http://localhost:3000')

    if not tenant_id or not sender_phone:
        print(json.dumps({
            "success": False,
            "error": "Missing TENANT_ID or SENDER_PHONE environment variables"
        }))
        sys.exit(1)

    if action == 'list' or action == 'status':
        success, triggers = list_triggers(tenant_id, sender_phone, api_base_url)

        if success:
            # Filter to deal-related triggers
            deal_triggers = [t for t in triggers if any(
                name in t.get('name', '').lower()
                for name in ['deal', 'scanner', 'liquidation', 'listing', 'expiry']
            )]

            print(json.dumps({
                "success": True,
                "action": "status",
                "total_triggers": len(triggers),
                "deal_triggers": len(deal_triggers),
                "triggers": deal_triggers,
                "available_to_create": list(TRIGGERS.keys()),
            }, indent=2))
        else:
            print(json.dumps({
                "success": False,
                "error": triggers
            }))
        return

    if action == 'setup_all':
        results = []
        for trigger_name, trigger_config in TRIGGERS.items():
            success, result = create_trigger(trigger_config, tenant_id, sender_phone, api_base_url)
            results.append({
                "name": trigger_name,
                "success": success,
                "trigger_id": result.get("trigger_id") if success else None,
                "error": result.get("error") if not success else None,
            })

        created = [r["name"] for r in results if r["success"]]
        failed = [r["name"] for r in results if not r["success"]]

        print(json.dumps({
            "success": len(failed) == 0,
            "action": "setup_all",
            "triggers_created": created,
            "triggers_failed": failed,
            "results": results,
            "message": f"Created {len(created)} triggers, {len(failed)} failed",
        }, indent=2))
        return

    if action in TRIGGERS:
        trigger_config = TRIGGERS[action]
        success, result = create_trigger(trigger_config, tenant_id, sender_phone, api_base_url)

        if success:
            print(json.dumps({
                "success": True,
                "action": action,
                "trigger_id": result.get("trigger_id"),
                "message": f"Created {trigger_config['name']} trigger",
                "config": trigger_config,
            }, indent=2))
        else:
            print(json.dumps({
                "success": False,
                "action": action,
                "error": result.get("error"),
            }))
        return

    print(json.dumps({
        "success": False,
        "error": f"Unknown action: {action}",
        "valid_actions": ["setup_all", "deal_scanner", "liquidation_check", "listing_expiry", "list", "status"],
    }))
    sys.exit(1)

if __name__ == '__main__':
    main()
