# Deal Hunting SOP

## Goal
Find discounted or free items on local marketplaces and wholesale/liquidation sites, evaluate profitability, and alert Anden on deals with 50%+ profit margin.

## Configuration
- **Margin Threshold**: 50%+ profit margin required
- **Location Radius**: 50 miles
- **Categories**: General flipping (no restrictions)
- **Platforms**: Facebook Marketplace, Craigslist, OfferUp, B-Stock, Liquidation.com

## Workflow Steps

### Step 1: Scan Marketplaces
For each platform, call `scrape_marketplace` with:
- `platform`: "facebook" | "craigslist" | "offerup"
- `location`: User's location (Salt Lake Valley)
- `radius_miles`: 50
- `search_terms`: Optional category filter

### Step 2: Get Sold Comparables
For each item found, call `get_sold_comps` with:
- `keywords`: Item title keywords
- `condition`: "new" | "used" | "refurbished"

### Step 3: Calculate Profitability
Call `calculate_arbitrage` with:
- `buy_price`: Listing price
- `estimated_sell`: Average sold comp price
- `platform_fees`: 13% for eBay, 0% for FB Marketplace
- `shipping_estimate`: Based on item size/weight

### Step 4: Filter Good Deals
Only proceed if:
- `margin_pct` >= 50%
- Item is legitimate (not scam/fake)
- Seller appears reliable

### Step 5: Save and Alert
If deal passes threshold:
1. Call `save_deal` to store in state/deals.json
2. Send WhatsApp notification with:
   - Item title and image
   - Buy price vs. estimated sell price
   - Profit margin percentage
   - Link to listing
   - "Reply APPROVE or REJECT"

## Tools to Use
- `scrape_marketplace` - Scrape listing data
- `get_sold_comps` - Get eBay sold prices
- `calculate_arbitrage` - Calculate profit
- `save_deal` - Store deal data
- `browser_open` / `browser_read` - For detailed scraping

## Edge Cases

### No Sold Comps Found
- Try broader keywords
- Check alternative platforms (Mercari, Poshmark)
- Flag as "needs manual research"

### Price Seems Too Good
- Flag for verification (possible scam)
- Check seller history if available
- Look for red flags in description

### Item Already Sold
- Skip silently
- Mark as unavailable if previously saved

### Rate Limiting
- Space requests 2-3 seconds apart
- Use proxy rotation if available
- Fall back to alternative platforms

## Success Criteria
- Deals found with 50%+ margin
- Anden notified within 5 minutes of discovery
- No false positives (scams, unavailable items)
