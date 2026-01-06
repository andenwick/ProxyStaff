# Deal Automation SOP

## Goal
Set up automated triggers to scan for deals, check liquidation sites, and manage the deal-hunting workflow without manual intervention.

## Available Triggers

### 1. Deal Scanner (Every 30 Minutes)
Automatically scans marketplaces for deals matching criteria.

**Trigger Configuration:**
```json
{
  "name": "Deal Scanner",
  "description": "Scans FB Marketplace, Craigslist, OfferUp every 30 min",
  "trigger_type": "TIME",
  "config": {
    "cron_expr": "*/30 * * * *",
    "timezone": "America/Denver"
  },
  "task_prompt": "Run a deal scan. Load the deal_hunting directive and scan Facebook Marketplace for deals. For any items with 50%+ profit margin, save the deal and notify me.",
  "autonomy": "AUTO",
  "cooldown_seconds": 1800
}
```

### 2. Liquidation Check (Daily 8am)
Checks wholesale/liquidation sites for new lots.

**Trigger Configuration:**
```json
{
  "name": "Liquidation Check",
  "description": "Daily check of liquidation sites at 8am",
  "trigger_type": "TIME",
  "config": {
    "cron_expr": "0 8 * * *",
    "timezone": "America/Denver"
  },
  "task_prompt": "Check B-Stock and Liquidation.com for new lots. Analyze any electronics or general merchandise pallets under $500. Report deals with estimated 50%+ margin.",
  "autonomy": "NOTIFY",
  "cooldown_seconds": 86400
}
```

### 3. Price Drop Monitor (Optional)
Monitors competitor prices and alerts on drops.

**Trigger Configuration:**
```json
{
  "name": "Price Monitor",
  "description": "Alerts when similar items drop in price",
  "trigger_type": "CONDITION",
  "config": {
    "poll_interval_minutes": 60,
    "data_source": {
      "type": "tool",
      "tool": "get_sold_comps",
      "input": { "keywords": "{{item_keywords}}" }
    },
    "condition": {
      "expression": "avg_price < previous_avg_price * 0.9"
    }
  },
  "task_prompt": "Price drop detected for tracked items. Review if any listed items need repricing.",
  "autonomy": "NOTIFY",
  "cooldown_seconds": 3600
}
```

### 4. Listing Expiry Check (Daily)
Checks for expired or stale listings.

**Trigger Configuration:**
```json
{
  "name": "Listing Expiry",
  "description": "Daily check for stale listings",
  "trigger_type": "TIME",
  "config": {
    "cron_expr": "0 18 * * *",
    "timezone": "America/Denver"
  },
  "task_prompt": "Check inventory for listings older than 7 days. Suggest price drops for stale items. Report inventory status summary.",
  "autonomy": "NOTIFY",
  "cooldown_seconds": 86400
}
```

## Setting Up Triggers

To create a trigger, tell me:
> "Set up the deal scanner trigger"

I'll run the create_trigger shared tool with the configuration above.

To list active triggers:
> "Show my triggers"

To pause or delete a trigger:
> "Pause the deal scanner"
> "Delete the liquidation check trigger"

## Autonomy Levels Explained

| Level | Behavior |
|-------|----------|
| **NOTIFY** | Send WhatsApp message about the event, no action taken |
| **CONFIRM** | Ask for approval before taking action |
| **AUTO** | Execute immediately without asking |

**Recommended Settings:**
- Deal Scanner: AUTO (finds deals, saves them, notifies you)
- Liquidation Check: NOTIFY (just reports findings)
- Price Monitor: NOTIFY (alerts only)
- Listing Expiry: NOTIFY (suggests actions)

## Workflow When Trigger Fires

### Deal Scanner (AUTO)
1. Trigger fires every 30 min
2. Claude loads deal_hunting directive
3. Calls scrape_marketplace for each platform
4. For each listing found:
   - Calls get_sold_comps
   - Calls calculate_arbitrage
   - If 50%+ margin: calls save_deal
5. Sends WhatsApp summary of good deals found
6. Awaits your APPROVE/REJECT responses

### Liquidation Check (NOTIFY)
1. Trigger fires at 8am daily
2. Claude analyzes liquidation sites
3. Sends WhatsApp with:
   - New lots available
   - Estimated value and profit
   - Link to view
4. You decide whether to investigate further

## Manual Override Commands

You can always run scans manually:
- "Scan for deals now"
- "Check liquidation sites"
- "How's my inventory?"

These work even if triggers are paused.

## Troubleshooting

### Trigger Not Firing
- Check if trigger is ACTIVE (not paused)
- Verify cooldown period hasn't blocked it
- Check server logs for errors

### Too Many Notifications
- Increase cooldown_seconds
- Change autonomy to CONFIRM
- Add filters to reduce noise

### Missed Deals
- Decrease scan interval
- Add more search terms
- Check if marketplace is blocking

## Quick Setup Commands

Tell me any of these to get started:
1. "Set up automated deal scanning" → Creates deal scanner trigger
2. "Set up daily liquidation alerts" → Creates liquidation check trigger
3. "Set up all deal automation" → Creates all recommended triggers
4. "Show automation status" → Lists all active triggers

## Cron Expression Reference

| Pattern | Meaning |
|---------|---------|
| `*/30 * * * *` | Every 30 minutes |
| `0 * * * *` | Every hour |
| `0 8 * * *` | Daily at 8am |
| `0 8 * * 1-5` | Weekdays at 8am |
| `0 */4 * * *` | Every 4 hours |
