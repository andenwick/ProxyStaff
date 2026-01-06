# Buyer Matching SOP

## Goal
Identify ideal buyers for deals and notify them when matching items are found.

## Buyer Profile Structure

Each buyer in `state/buyers.json` has:
- **name**: Buyer name or identifier
- **categories**: What they buy (electronics, furniture, collectibles, etc.)
- **price_range**: Min/max they typically spend
- **contact_method**: "email" | "whatsapp" | "sms"
- **contact_info**: Email address or phone number
- **preferences**: Specific brands, conditions, or features they want
- **notes**: Any special requirements

## Workflow Steps

### Step 1: Analyze Item Category
Determine the item's category based on:
- Title keywords
- Price range
- Common marketplace categories

### Step 2: Check Buyer Database
Load buyers from `state/buyers.json` and filter by:
- Matching categories
- Price within their range
- Active status

### Step 3: Analyze Market Demand
Call `analyze_buyer_demand` to understand:
- How fast similar items sell on eBay
- Common buyer keywords/searches
- Peak buying times

### Step 4: Score Buyer Match
Rank matching buyers by:
1. Category match strength
2. Price range fit
3. Past purchase history (if tracked)
4. Responsiveness (if tracked)

### Step 5: Notify Matching Buyers
For top matches, call `notify_buyer_network` with:
- Item details (title, price, images)
- Deal margin/value proposition
- Link to listing or contact info
- Urgency indicator (hot deal, limited time)

## Tools to Use
- `analyze_buyer_demand` - Check market demand patterns
- `notify_buyer_network` - Send notifications to buyers
- `gmail_send` - For email notifications

## Adding New Buyers

When Anden mentions a new buyer contact:
1. Ask for their name and categories of interest
2. Ask for price range preferences
3. Get contact method and info
4. Add to `state/buyers.json`

Example conversation:
> User: "Add John as a buyer, he's into electronics"
> You: "Got it. What's John's price range and contact email?"

## Matching Logic

### Category Keywords
- **Electronics**: phone, iphone, samsung, laptop, tablet, gaming, console, ps5, xbox
- **Furniture**: couch, sofa, table, chair, desk, bed, dresser
- **Collectibles**: cards, pokemon, vintage, antique, rare, limited
- **Clothing**: shoes, sneakers, nike, jordan, designer, clothing
- **Tools**: dewalt, milwaukee, tools, power tools, drill
- **Appliances**: washer, dryer, refrigerator, appliance

### Price Range Matching
- Budget buyers: $0-$100
- Mid-range: $100-$500
- Premium: $500-$2000
- High-value: $2000+

## Edge Cases

### No Matching Buyers
- Suggest categories to build buyer network
- Consider listing on open marketplace instead

### Multiple Matches
- Notify top 3 matching buyers
- First responder gets priority

### Buyer Not Responsive
- After 2 unanswered notifications, reduce priority
- Track responsiveness in buyer profile

## Success Criteria
- Deals matched to relevant buyers within 10 minutes
- High response rate from notified buyers
- Quick turnaround from deal found to sold
