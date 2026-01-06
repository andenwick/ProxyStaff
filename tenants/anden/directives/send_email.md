# Send Email SOP

## Goal
Send email notifications to users via SendGrid.

## When to Use
- User explicitly asks to send an email
- User wants to notify someone about something
- Scheduled reminder needs to be sent

## Required Information
Before sending, you MUST have:
1. **Recipient email** - Valid email address
2. **Subject** - Brief, clear subject line
3. **Body** - The message content

## Steps

1. **Gather information** - Ask user for missing details:
   - "Who should I send this to?" (if no recipient)
   - "What should the subject be?" (if no subject)
   - "What message do you want to send?" (if no body)

2. **Confirm before sending** - Always confirm with user:
   - "I'll send an email to [recipient] with subject '[subject]'. Should I proceed?"

3. **Send the email** - Use the `send_email` tool:
   ```json
   {
     "to": "recipient@example.com",
     "subject": "Your subject here",
     "body": "Your message here"
   }
   ```

4. **Report result** - Tell user if it succeeded or failed

## Tools to Use
- `send_email` - Sends email via SendGrid

## Edge Cases

| Situation | Action |
|-----------|--------|
| Invalid email format | Ask user to provide a valid email |
| User cancels | Acknowledge and don't send |
| Send fails | Explain error, suggest retry or alternative |
| No recipient specified | Ask who to send to |

## Example Conversation

**User:** Send an email to john@example.com saying the meeting is tomorrow at 3pm

**Assistant:** I'll send an email to john@example.com with subject "Meeting Reminder" and the message about tomorrow's 3pm meeting. Should I proceed?

**User:** Yes

**Assistant:** [Uses send_email tool] Done! Email sent to john@example.com.
