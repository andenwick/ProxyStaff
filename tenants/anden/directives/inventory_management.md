# Inventory Management SOP

## Goal
Track all deals and listings from discovery through sale, providing visibility into inventory status and profit tracking.

## Data Locations
- `state/deals.json` - All discovered deals
- `state/listings.json` - All active listings
- `state/buyers.json` - Buyer network

## Deal Lifecycle

```
FOUND → APPROVED → PURCHASED → LISTED → SOLD
   ↓                              ↓
REJECTED                       EXPIRED
```

### Status Definitions

| Status | Description |
|--------|-------------|
| `found` | Deal discovered, awaiting review |
| `approved` | Anden approved the deal |
| `rejected` | Anden rejected the deal |
| `purchased` | Item has been acquired |
| `listed` | Item is listed for sale |
| `sold` | Item has been sold |
| `expired` | Listing expired without sale |

## Workflow Steps

### When a Deal is Found
1. Call `save_deal` with status "found"
2. Alert Anden via WhatsApp
3. Wait for approval/rejection

### When Anden Approves
1. Call `update_inventory` with status "approved"
2. Prompt: "Have you purchased the item?"
3. When confirmed, update to "purchased"

### When Item is Listed
1. Create listing via `list_ebay` or `list_fb_marketplace`
2. Call `update_inventory` with:
   - status: "listed"
   - listing_ids: [platform IDs]
   - listing_urls: [URLs]

### When Item Sells
1. Call `update_inventory` with:
   - status: "sold"
   - sold_price: actual sale price
   - sold_date: date of sale
   - platform: where it sold
2. Calculate actual profit
3. Update buyer profile if applicable

### When Listing Expires
1. Call `update_inventory` with status "expired"
2. Suggest: relist, reduce price, or remove

## Tools to Use
- `update_inventory` - Update deal/listing status
- `save_deal` - Create new deal record
- `manage_buyer` - Track buyer interactions

## Tracking Metrics

### Per Deal
- Days to sell
- Actual vs estimated profit
- Platform sold on
- Buyer type (marketplace vs network)

### Overall
- Total deals found
- Approval rate
- Sell-through rate
- Average profit margin
- Best performing categories

## Daily Summary

When asked "How's inventory?", provide:
1. Deals awaiting approval
2. Items purchased but not listed
3. Active listings count
4. Items sold this week
5. Total profit this week

**Example**:
```
📊 Inventory Status:
• 3 deals awaiting approval
• 1 item to list
• 5 active listings
• 2 sold this week (+$340 profit)
```

## Price Drop Strategy

If item not sold after:
- **7 days**: Suggest 5% price drop
- **14 days**: Suggest 10% price drop
- **21 days**: Suggest 15% drop or removal

## Edge Cases

### Partial Sale
- If selling multiple of same item, track quantity separately
- Update status to "sold" only when all units sold

### Refund/Return
- Mark as "returned"
- Relist or adjust profit tracking

### Cross-Posted Items
- Track all platforms in listing record
- Remove from other platforms when sold

## Success Criteria
- Real-time visibility into all inventory
- Accurate profit tracking
- No lost or forgotten items
- Quick status updates
