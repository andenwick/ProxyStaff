# Daily Email Check SOP

## Goal
Check Gmail for important emails and provide a concise summary via WhatsApp.

## When to Use
This directive runs automatically every day at 9 AM.

## Process

### 1. Search for Recent Important Emails
Use `gmail_search` with the following query:
```
is:unread newer_than:1d
```

This finds unread emails from the last 24 hours.

### 2. Filter for Priority
Look for emails that are likely important:
- From known contacts (check life/knowledge/contacts.md if needed)
- Time-sensitive keywords: "urgent", "asap", "important", "deadline", "action required"
- Business-related subjects
- Meeting invitations or calendar items

### 3. Summarize Findings

**If important emails found:**
Send a concise message (2-3 sentences max):
```
Morning! You have [X] unread emails. Important: [brief summary of 1-2 most critical items]. Want me to read any?
```

**If no important emails:**
```
Morning! Email is clear - no urgent items in the last 24 hours.
```

**If no unread emails at all:**
```
Morning! Inbox is clean - all caught up.
```

## Tips
- Keep it brief - this is a morning check-in, not a full report
- Only mention the most important 1-2 emails
- Offer to read full details if user wants more info
- Don't overwhelm with too much information

## Example Output

Good example:
```
Morning! You have 3 unread emails. Important: Invoice from Acme Corp due Friday, and meeting request from Sarah for tomorrow. Want details?
```

Bad example (too long):
```
Good morning! I checked your email and found 3 unread messages. The first one is from Acme Corp about an invoice that's due on Friday. The second is from Sarah requesting a meeting tomorrow at 2pm. The third is a newsletter from TechNews. Let me know if you'd like me to read any of these in full detail.
```
