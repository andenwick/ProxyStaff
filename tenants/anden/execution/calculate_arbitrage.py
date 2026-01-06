#!/usr/bin/env python3
"""
Calculate Arbitrage Tool - Calculates profit margin for a deal.

Input:
  buy_price: Purchase price
  estimated_sell: Expected sell price
  platform: "ebay" | "facebook" | "poshmark" (for fee calculation)
  shipping_cost: Estimated shipping cost (default: 0)
  other_costs: Any other costs (packaging, etc., default: 0)

Output:
  gross_profit: Sell price - buy price
  net_profit: Profit after all fees and costs
  margin_pct: Net profit as percentage of buy price
  roi: Return on investment percentage
  fees: Breakdown of fees
  is_profitable: True if margin >= 50% threshold
"""
import sys
import json

# Platform fee structures
PLATFORM_FEES = {
    "ebay": {
        "final_value_fee": 0.1315,  # 13.15% final value fee
        "payment_processing": 0.029,  # 2.9% payment processing
        "fixed_fee": 0.30,  # $0.30 per transaction
    },
    "facebook": {
        "final_value_fee": 0.05,  # 5% selling fee (if using shipping)
        "payment_processing": 0.029,  # 2.9% payment processing
        "fixed_fee": 0.30,  # $0.30 per transaction
    },
    "poshmark": {
        "final_value_fee": 0.20,  # 20% commission
        "payment_processing": 0.0,  # Included in commission
        "fixed_fee": 0.0,
    },
    "mercari": {
        "final_value_fee": 0.10,  # 10% selling fee
        "payment_processing": 0.029,
        "fixed_fee": 0.30,
    },
    "local": {
        "final_value_fee": 0.0,  # No fees for local pickup
        "payment_processing": 0.0,
        "fixed_fee": 0.0,
    },
}

MARGIN_THRESHOLD = 0.50  # 50% minimum margin

def calculate_fees(sell_price, platform):
    """Calculate platform fees."""
    fees = PLATFORM_FEES.get(platform, PLATFORM_FEES["ebay"])

    final_value = sell_price * fees["final_value_fee"]
    payment = sell_price * fees["payment_processing"]
    fixed = fees["fixed_fee"]

    total = final_value + payment + fixed

    return {
        "final_value_fee": round(final_value, 2),
        "payment_processing": round(payment, 2),
        "fixed_fee": round(fixed, 2),
        "total_fees": round(total, 2),
    }

def main():
    input_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}

    buy_price = input_data.get('buy_price')
    estimated_sell = input_data.get('estimated_sell')
    platform = input_data.get('platform', 'ebay')
    shipping_cost = input_data.get('shipping_cost', 0)
    other_costs = input_data.get('other_costs', 0)

    if buy_price is None or estimated_sell is None:
        print(json.dumps({"error": "buy_price and estimated_sell are required"}))
        sys.exit(1)

    try:
        buy_price = float(buy_price)
        estimated_sell = float(estimated_sell)
        shipping_cost = float(shipping_cost)
        other_costs = float(other_costs)
    except (ValueError, TypeError):
        print(json.dumps({"error": "Invalid numeric values"}))
        sys.exit(1)

    if buy_price <= 0:
        print(json.dumps({"error": "buy_price must be positive"}))
        sys.exit(1)

    # Calculate fees
    fees = calculate_fees(estimated_sell, platform)

    # Calculate profits
    gross_profit = estimated_sell - buy_price
    total_costs = buy_price + shipping_cost + other_costs + fees["total_fees"]
    net_profit = estimated_sell - total_costs

    # Calculate margins
    margin_pct = (net_profit / buy_price) * 100 if buy_price > 0 else 0
    roi = (net_profit / total_costs) * 100 if total_costs > 0 else 0

    result = {
        "success": True,
        "buy_price": round(buy_price, 2),
        "estimated_sell": round(estimated_sell, 2),
        "platform": platform,
        "gross_profit": round(gross_profit, 2),
        "net_profit": round(net_profit, 2),
        "margin_pct": round(margin_pct, 1),
        "roi": round(roi, 1),
        "fees": fees,
        "shipping_cost": round(shipping_cost, 2),
        "other_costs": round(other_costs, 2),
        "total_costs": round(total_costs, 2),
        "is_profitable": margin_pct >= (MARGIN_THRESHOLD * 100),
        "threshold": MARGIN_THRESHOLD * 100,
    }

    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
