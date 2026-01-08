# Outbound Email SOP

## Goal
Generate personalized, high-converting outbound emails to book discovery calls with prospects.

## When to Use
- Processing campaign targets in "researched" stage
- Following up on non-responsive prospects
- Re-engaging nurture leads

## Process

### 1. Gather Research
Before writing ANY email, you MUST have:
- Company website research (use `research_website` tool)
- Any available reviews/ratings
- Understanding of their business type and likely pain points

**Never send a generic email. Every email must reference something specific.**

### 2. Email Structure

**Subject Line (3-7 words)**
- Reference their business or challenge
- Avoid spam triggers: "free", "guarantee", "limited time"
- Good: "Quick question about [Company Name]"
- Good: "[Industry] follow-up automation"

**Opening (1-2 sentences)**
- Reference something specific from research
- Show you know who they are
- NO: "I hope this email finds you well"

**Pain Point (1-2 sentences)**
- State a problem they likely have
- Use "you" language, not "I" or "we"
- Make it relatable

**Solution Hint (1-2 sentences)**
- Brief mention of how we help
- Focus on outcome, not features
- Don't oversell

**CTA (1 sentence)**
- Single, clear ask
- Low commitment: "Worth a quick chat?"
- Specific: "15 minutes this week?"

**Sign-off**
- Simple: "— Anden"
- Include unsubscribe line for CAN-SPAM

### 3. Email Examples

**Initial Outreach:**
```
Subject: Quick question about [Company Name]

Hi [First Name],

I noticed [specific observation from website/reviews - e.g., "you've got great reviews on Google" or "your website mentions you specialize in luxury properties"].

Running a [industry] business usually means drowning in messages—leads, follow-ups, scheduling requests. Does that sound familiar?

I help [industry] owners automate the routine stuff so they can focus on closing deals. Clients typically save 10+ hours a week.

Worth a quick 15-minute chat to see if this could help [Company Name]?

— Anden

P.S. If this isn't relevant, no worries—just reply "unsubscribe" and I'll remove you from my list.
```

**Follow-up #1 (3-5 days later):**
```
Subject: Re: Quick question about [Company Name]

Hi [First Name],

Following up on my last note. I know you're busy.

One thing I didn't mention: the AI assistant I build for businesses like yours handles [specific task relevant to their industry] automatically. One client told me it's like having a reliable assistant who never forgets a follow-up.

If that sounds useful, I'd love to show you how it works. 15 minutes, no pitch.

— Anden
```

**Follow-up #2 (value-add):**
```
Subject: Something that might help

Hi [First Name],

Still thinking about ways to help [Company Name]. Here's a quick tip:

[Relevant, actionable insight for their industry]

This is the kind of thing my AI handles automatically for clients. Happy to share more if you're curious.

— Anden
```

**Final follow-up:**
```
Subject: Should I close your file?

Hi [First Name],

I've reached out a few times about automating [Company Name]'s communications. I haven't heard back, which usually means one of three things:

1. You're swamped (I get it)
2. Not the right time
3. Not interested

Any of those is fine—I just don't want to keep emailing if you'd rather I didn't.

If you'd like to chat, just reply. Otherwise, I'll assume it's a "not now" and check back in a few months.

— Anden
```

### 4. CAN-SPAM Compliance

Every email MUST include:
- Clear "From" identity (Anden / ProxyStaff)
- Physical address: [Your address]
- Unsubscribe mechanism: "Reply 'unsubscribe' to be removed"

**If someone unsubscribes:**
1. Acknowledge immediately
2. Mark as unsubscribed in campaign
3. NEVER email again

### 5. Approval Workflow

ALL outbound emails require approval before sending:

1. Generate email using this SOP
2. Add to approval queue with:
   - Prospect name and email
   - Email subject and body
   - Research summary (why personalized this way)
3. Wait for approval via Telegram
4. Only send after explicit approval

### 6. Response Handling

When prospect replies, categorize and respond:

| Response Type | Action |
|---------------|--------|
| Interested | Qualify with 1-2 questions, offer to book call |
| Questions | Answer directly, pivot to call |
| "Not now" | Thank, offer to check back later, mark as nurture |
| "Not interested" | Thank professionally, mark as lost |
| "Unsubscribe" | Immediately comply, apologize briefly |

## Tools to Use

| Tool | Purpose |
|------|---------|
| `research_website` | Get info for personalization |
| `find_email` | Find prospect email |
| `gmail_send` | Send approved email |
| `calendar_get_availability` | Check open slots for booking |
| `calendar_create_event` | Book discovery call |

## Common Mistakes to Avoid

1. **Generic opening** - Never "I hope this finds you well"
2. **Too long** - Keep under 150 words
3. **Multiple CTAs** - One ask only
4. **Feature dump** - Focus on outcomes
5. **Pressure tactics** - Never "limited time" or urgency
6. **No research** - Every email must reference something specific
7. **Skipping approval** - Never send without approval
