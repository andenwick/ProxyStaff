# Crypto Refill SOP

## Goal
Send USDT from Coinbase to Rainbet (or other platforms) on user request.

## Available Tools
- `get_deposit_address` - Check if deposit address is saved
- `save_deposit_address` - Save a new deposit address
- `coinbase_get_balance` - Check Coinbase balance
- `coinbase_send_crypto` - Send crypto to external address

## Trigger Phrases
- "refill rainbet 100"
- "send 50 usdt to rainbet"
- "top up my rainbet"
- "put 200 in rainbet"

## Workflow

### Step 1: Check Saved Address
First, check if we have a saved address for the platform:
```json
get_deposit_address({"platform": "rainbet"})
```

### Step 2: Get Address if Needed
If no address saved, ask the user:
> "What's your Rainbet USDT deposit address? TRC20 recommended for low fees."

Then save it:
```json
save_deposit_address({"platform": "rainbet", "address": "USER_ADDRESS", "network": "TRC20"})
```

### Step 3: Verify Coinbase Balance
Check if we have enough:
```json
coinbase_get_balance({"currency": "USDT"})
```

If insufficient: "You only have X USDT in Coinbase but need Y. Please deposit more first."

### Step 4: Send the Crypto
```json
coinbase_send_crypto({
  "to_address": "SAVED_ADDRESS",
  "amount": REQUESTED_AMOUNT,
  "currency": "USDT",
  "network": "TRC20"
})
```

### Step 5: Confirm
> "Sent 100 USDT to your Rainbet. Transaction ID: abc123. Should arrive in a few minutes."

## Safety Limits
- Max single transfer: 200 USDT (default)
- If user requests more, ask for confirmation

## Example Conversation

**User:** refill rainbet 150

**You:**
1. Call `get_deposit_address({"platform": "rainbet"})`
2. If found, call `coinbase_get_balance({"currency": "USDT"})`
3. If enough balance, call `coinbase_send_crypto({...})`
4. Respond: "Sent 150 USDT to your Rainbet. Transaction: abc123"

## Edge Cases

| Situation | Response |
|-----------|----------|
| No saved address | Ask for their Rainbet USDT deposit address |
| Insufficient Coinbase balance | Tell them their balance and ask them to deposit more |
| Amount over limit | Ask for confirmation before sending |
| Invalid address format | "That doesn't look like a valid TRC20 address. Please double-check." |

## Tips
- Always use `get_deposit_address` first to avoid asking for address repeatedly
- TRC20 has lowest fees, recommend it
- Confirm large amounts (over 200 USDT) before sending
