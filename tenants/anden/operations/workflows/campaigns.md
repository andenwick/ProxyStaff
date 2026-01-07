# Campaigns SOP

## Goal
Manage outbound sales campaigns with automated outreach across email, LinkedIn, SMS, and calls.

## Campaign Stages
```
Identified → Researched → Contacted → Replied → Qualified → Booked → Won/Lost
```

## Available Tools

### Campaign Management (Python - call via bash)
| Tool | Purpose |
|------|---------|
| `campaign_read.py` | List campaigns, read campaign data |
| `campaign_write.py` | Create campaigns, add targets, update stages |

### Approval Queue (Python - call via bash)
| Tool | Purpose |
|------|---------|
| `list_pending_actions.py` | View actions awaiting approval |
| `approve_actions.py` | Approve actions for sending |
| `execute_approved_actions.py` | Send approved messages |

### Reply Processing (Python - call via bash)
| Tool | Purpose |
|------|---------|
| `process_campaign_replies.py` | Check Gmail for replies, analyze intent, update stages |

### Channel Tools (Python - call via bash)
| Tool | Purpose |
|------|---------|
| `send_email.py` | Send email via Gmail |
| `linkedin_send.py` | Send LinkedIn message (requires setup) |
| `sms_send.py` | Send SMS via Twilio |
| `call_initiate.py` | Initiate phone call via Twilio |

## When to Use

| User Request | Action |
|--------------|--------|
| "Create a campaign" | Create campaign folder with config |
| "Add targets to campaign" | Add targets to targets.md |
| "Activate campaign" | Update status to "active" |
| "Show pending approvals" | List actions in approval queue |
| "Approve all" | Approve pending actions |
| "Send approved messages" | Execute approved actions |
| "Campaign status" | Read campaign metrics and targets |
| "Check for replies" | Process campaign replies, update stages |
| "Any responses?" | Check for and analyze target replies |

## Campaign Workflow

### 1. Create Campaign
```bash
echo '{"operation": "create", "campaign": "q1-outreach", "data": {"goal": "Book 10 meetings", "owner_phone": "+1234567890"}}' | python src/tools/python/campaign_write.py
```

### 2. Add Targets
```bash
echo '{"operation": "add_target", "campaign": "q1-outreach", "data": {"name": "John Smith", "email": "john@acme.com", "company": "Acme Inc", "title": "CTO"}}' | python src/tools/python/campaign_write.py
```

### 3. Activate Campaign
```bash
echo '{"operation": "update_config", "campaign": "q1-outreach", "data": {"status": "active"}}' | python src/tools/python/campaign_write.py
```

### 4. Check Pending Actions
Every 15 minutes, the system processes active campaigns and queues actions for approval.

```bash
echo '{}' | python src/tools/python/list_pending_actions.py
```

### 5. Review and Approve
```bash
# Approve all pending
echo '{"approve_all": true}' | python src/tools/python/approve_actions.py

# Or approve specific ones
echo '{"action_ids": ["uuid1", "uuid2"]}' | python src/tools/python/approve_actions.py
```

### 6. Execute Approved Actions
```bash
echo '{}' | python src/tools/python/execute_approved_actions.py

# Dry run first
echo '{"dry_run": true}' | python src/tools/python/execute_approved_actions.py
```

## Campaign File Structure

Campaigns are stored in `operations/campaigns/{name}/`:
```
operations/campaigns/q1-outreach/
├── config.md      # Campaign settings and channels
├── targets.md     # Target list with stages
├── sequence.md    # Outreach sequences
├── metrics.md     # Campaign metrics
└── log.md         # Event log
```

## Reading Campaign Data

### List All Campaigns
```bash
echo '{}' | python src/tools/python/campaign_read.py
```

### Read Campaign Config
```bash
echo '{"campaign": "q1-outreach", "file": "config"}' | python src/tools/python/campaign_read.py
```

### Read Targets
```bash
echo '{"campaign": "q1-outreach", "file": "targets"}' | python src/tools/python/campaign_read.py
```

### Search Targets
```bash
echo '{"campaign": "q1-outreach", "file": "targets", "query": "acme"}' | python src/tools/python/campaign_read.py
```

## Updating Targets

### Update Target Stage
```bash
echo '{"operation": "update_target", "campaign": "q1-outreach", "target_id": "uuid", "data": {"stage": "contacted"}}' | python src/tools/python/campaign_write.py
```

### Record Touch
```bash
echo '{"operation": "record_touch", "campaign": "q1-outreach", "target_id": "uuid", "data": {"channel": "email", "subject": "Quick question", "status": "sent"}}' | python src/tools/python/campaign_write.py
```

## Channel Configuration

### Email (Default)
Uses Gmail tools. Requires Gmail credentials in .env.

### LinkedIn (Requires Setup)
Set in .env:
```
LINKEDIN_EMAIL=your@email.com
LINKEDIN_PASSWORD=yourpassword
```

### SMS (Requires Twilio)
Set in .env:
```
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_PHONE_NUMBER=+1234567890
```

### Calls (Requires Twilio + TwiML)
Same Twilio credentials plus:
```
TWILIO_TWIML_URL=https://your-server.com/twiml
```

## Automatic Processing

The CampaignScheduler runs every 15 minutes:
1. Gets all tenants with active campaigns
2. For each campaign, finds targets needing action
3. Checks unsubscribe list
4. Generates personalized messages
5. Queues actions for approval

**Actions expire after 3 days if not approved.**

## Unsubscribe Detection

The system automatically detects unsubscribe requests in replies:
- "unsubscribe"
- "stop emailing"
- "opt out"
- "remove me"
- "not interested"
- etc.

Detected unsubscribes are added to global opt-out list.

## Reply Processing

The system automatically detects and processes replies from campaign targets.

### Check for Replies
```bash
# Check last 24 hours (default)
echo '{}' | python src/tools/python/process_campaign_replies.py

# Check specific time window
echo '{"hours_back": 48}' | python src/tools/python/process_campaign_replies.py

# Dry run (analyze but don't update)
echo '{"dry_run": true}' | python src/tools/python/process_campaign_replies.py

# Filter to specific campaign
echo '{"campaign": "q1-outreach"}' | python src/tools/python/process_campaign_replies.py
```

### Reply Intent Detection

The system analyzes reply content to detect intent:

| Intent | Keywords | Suggested Stage |
|--------|----------|-----------------|
| Interested | "tell me more", "sounds good", "let's chat" | replied |
| Meeting Request | "schedule a call", "calendar", "available" | qualified |
| Not Interested | "not interested", "no thanks", "pass" | lost |
| Unsubscribe | "unsubscribe", "stop emailing", "remove me" | lost |
| Out of Office | "out of office", "on vacation", "auto-reply" | (wait) |
| Question | "how does", "pricing", "features" | replied |

### Reply Processing Flow

```
Reply received
      │
      ▼
Check for unsubscribe keywords
      │
  ┌───┴───┐
  │       │
Unsub   Not unsub
  │       │
  ▼       ▼
Mark    Analyze intent
lost    & sentiment
  │       │
  ▼       ▼
Add to  Update target
optout  stage if needed
  │       │
  ▼       ▼
Log to  Queue follow-up
timeline action
```

### Automatic Stage Updates

When a reply is detected:
1. **Positive reply** → Stage advances to `replied` or `qualified`
2. **Meeting request** → Stage advances to `qualified` (ready for booking)
3. **Negative reply** → Stage set to `lost`
4. **Unsubscribe** → Stage set to `lost`, added to opt-out list
5. **Out of office** → No change, will retry later
6. **Question** → Stage advances to `replied`, needs follow-up

### Reply Tracking

Processed replies are tracked in `state/processed_replies.json` to avoid re-processing:
- Email IDs are stored after processing
- Last 1000 IDs kept to manage file size
- Duplicate detection prevents double-processing

## Best Practices

1. **Always review before approving** - Check message content and reasoning
2. **Use dry_run first** - Test execution without actually sending
3. **Respect daily limits** - Default: 20 outreach/day per campaign
4. **Wait between touches** - Default: 3 days minimum between contacts
5. **Monitor replies** - Check for unsubscribes and responses
6. **Update stages promptly** - Keep target stages current

## Edge Cases

| Situation | Action |
|-----------|--------|
| No targets to process | Campaign waits for new targets |
| Daily limit reached | Processing pauses until next day |
| Target unsubscribed | Skip target, mark in targets.md |
| Action expired | Remove from queue, re-process if needed |
| Email bounced | Add to unsubscribe list |
| Target replied | Update stage to "replied" |
