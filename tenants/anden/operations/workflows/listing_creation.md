# Listing Creation SOP

## Goal
Create optimized listings that sell quickly at maximum profit across multiple platforms.

## Platforms Supported
- **eBay** - Largest audience, 13% fees, best for electronics/collectibles
- **Facebook Marketplace** - Local sales, 5% fees (shipped) or 0% (local), best for furniture/bulky items
- **Custom Buyer Network** - Direct sales, 0% fees, fastest turnaround

## Workflow Steps

### Step 1: Gather Item Details
From the deal record, extract:
- Title/name
- Condition (new, like new, good, fair)
- Original price paid
- Target sell price
- Images
- Any defects or notes

### Step 2: Generate Optimized Title
Create a title that:
- Includes brand name first
- Has key model/specs
- Uses searchable keywords
- Stays under 80 characters (eBay limit)

**Good**: "Apple iPhone 12 Pro 128GB Pacific Blue Unlocked Excellent Condition"
**Bad**: "Great Phone For Sale!!!"

### Step 3: Generate Description
Create a description that:
- Opens with key selling points
- Lists specifications clearly
- Notes condition honestly
- Includes any accessories
- Ends with call to action

**Template**:
```
[CONDITION] [BRAND] [MODEL] - [KEY FEATURE]

SPECIFICATIONS:
• [Spec 1]
• [Spec 2]
• [Spec 3]

CONDITION:
[Honest description of condition, any wear/defects]

INCLUDES:
• [Item]
• [Accessories if any]

Ships within 1 business day. Message with questions!
```

### Step 4: Set Pricing Strategy
Based on sold comps:
- **Quick sale**: Price at median sold - 5%
- **Max profit**: Price at 75th percentile
- **Auction**: Start at 50% of median, no reserve

### Step 5: Select Categories
Match to platform categories:
- eBay: Use specific subcategory for visibility
- FB Marketplace: Choose most relevant category

### Step 6: Create Listings
Call appropriate listing tool:
- `list_ebay` for eBay
- `list_fb_marketplace` for Facebook
- `notify_buyer_network` for direct buyers

### Step 7: Track Listing
Call `update_inventory` to:
- Mark deal as "listed"
- Store listing IDs/URLs
- Set reminder for price drops if not sold

## Tools to Use
- `list_ebay` - Create eBay listing
- `list_fb_marketplace` - Create FB Marketplace listing
- `notify_buyer_network` - Alert buyer network
- `update_inventory` - Update deal status

## Platform-Specific Tips

### eBay
- Use "Buy It Now" for quick sales
- Enable "Best Offer" to negotiate
- Free shipping converts better (build into price)
- Schedule listings to end Sunday evening

### Facebook Marketplace
- Use all 10 photo slots
- Price slightly higher (buyers negotiate)
- Respond quickly to messages
- Mark as "available" to boost visibility

## Pricing Formula

```
Target Price = (Buy Price / (1 - Target Margin)) + Fees + Shipping

Example for 50% margin on eBay:
- Buy Price: $100
- Target Margin: 50%
- eBay Fees: ~15%
- Shipping: $10

Target = ($100 / 0.50) + fees built in = ~$235
```

## Edge Cases

### Low-Quality Images
- Use `browser_screenshot` to capture from original listing
- Note "stock photo" if using manufacturer images

### Unknown Condition
- Default to "Good" and note "Condition as shown"
- Price conservatively

### Listing Fails
- Retry once after 5 minutes
- If still fails, alert Anden for manual listing
- Log error for debugging

## Success Criteria
- Listings created within 5 minutes of approval
- Title SEO-optimized for platform search
- Accurate condition descriptions
- Competitive pricing based on comps
