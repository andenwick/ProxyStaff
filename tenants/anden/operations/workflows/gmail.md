# Gmail SOP

## Goal
Read, search, and send emails via Gmail.

## Available Tools
- `gmail_search` - Search emails by query
- `gmail_read` - Read a specific email's content
- `gmail_send` - Send an email

## When to Use

| User Request | Tool to Use |
|--------------|-------------|
| "Check my emails" | `gmail_search` (recent) |
| "Any emails from John?" | `gmail_search` with from filter |
| "Search for invoices" | `gmail_search` with subject/keyword |
| "What does that email say?" | `gmail_read` with email ID |
| "Send an email to..." | `gmail_send` |

## Searching Emails

Use `gmail_search` with a query string. Supports Gmail search syntax:

| Query | Meaning |
|-------|---------|
| `from:john@example.com` | Emails from John |
| `subject:invoice` | Subject contains "invoice" |
| `after:2024/01/01` | Emails after date |
| `before:2024/12/31` | Emails before date |
| `is:unread` | Unread emails only |
| `has:attachment` | Has attachments |
| `newer_than:7d` | Last 7 days |

Combine queries: `from:john@example.com subject:meeting newer_than:30d`

**Example:**
```json
{
  "query": "from:support@company.com newer_than:7d",
  "max_results": 10
}
```

## Reading Emails

After searching, use `gmail_read` with the email ID to get full content:

```json
{
  "email_id": "12345"
}
```

## Sending Emails

Use `gmail_send` with recipient, subject, and body:

```json
{
  "to": "recipient@example.com",
  "subject": "Meeting tomorrow",
  "body": "Hi, just confirming our meeting tomorrow at 3pm."
}
```

## Workflow

### For "Check my emails":
1. Use `gmail_search` with `query: "is:unread newer_than:1d"` or similar
2. Summarize results: sender, subject, date
3. Ask if user wants to read any specific email

### For "Find emails about X":
1. Use `gmail_search` with relevant query
2. List matching emails
3. Offer to read specific ones

### For "Read that email":
1. Use `gmail_read` with the email ID from previous search
2. Present the content clearly

### For "Send email to X":
1. Gather: recipient, subject, body
2. Confirm with user before sending
3. Use `gmail_send`
4. Report success/failure

## Edge Cases

| Situation | Action |
|-----------|--------|
| No emails found | Tell user, suggest broader search |
| Too many results | Ask user to narrow search criteria |
| Invalid email ID | Ask user which email they meant |
| Send fails | Explain error, check recipient address |

## Tips
- Always summarize search results concisely
- Offer to read full content only when user wants details
- Confirm before sending emails
- Use date filters to narrow large result sets
