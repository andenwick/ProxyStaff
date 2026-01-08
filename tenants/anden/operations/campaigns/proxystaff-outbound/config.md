---json
{
  "version": 2,
  "id": "proxystaff-outbound-001",
  "name": "ProxyStaff Outbound",
  "status": "active",
  "created_at": "2026-01-06T00:00:00.000Z",
  "lastUpdated": "2026-01-08T00:00:00.000Z",
  "owner_phone": "",
  "goal": "Book discovery calls with busy business owners who can benefit from AI automation",
  "audience": {
    "description": "Owner-operated small businesses drowning in messages and follow-ups",
    "industries": ["realtors", "plumbers", "hvac", "electricians", "general-contractors"],
    "company_size": "1-3 employees",
    "locations": ["Salt Lake City, UT"]
  },
  "icp": {
    "good_fit_signals": [
      "Owner-operated (contacting owner directly)",
      "Active Google listing with reviews",
      "Evidence of active operation",
      "Open to automation/technology"
    ],
    "disqualifiers": [
      "Franchises",
      "Multi-location businesses",
      "Dedicated office staff or receptionist",
      "Large corporate chains",
      "Not owner-operated"
    ]
  },
  "channels": {
    "email": { "enabled": true, "provider": "gmail" },
    "linkedin": { "enabled": false, "planned": true },
    "social": { "enabled": false, "planned": true },
    "sms": { "enabled": false },
    "calls": { "enabled": false }
  },
  "settings": {
    "max_daily_outreach": 10,
    "min_days_between_touches": 5,
    "max_touches_per_target": 3,
    "require_approval": true,
    "approval_mode": "individual",
    "after_sequence": "pause",
    "reengage_after_months": 5
  },
  "timing": {
    "response_mode": "delayed",
    "response_delay_min_hours": 1,
    "response_delay_max_hours": 1,
    "business_hours_only": true,
    "business_hours_start": "07:00",
    "business_hours_end": "21:00",
    "business_hours_timezone": "America/Denver",
    "send_on_weekends": true
  },
  "metrics_snapshot": {
    "total_targets": 0,
    "by_stage": {
      "identified": 0,
      "researched": 0,
      "contacted": 0,
      "replied": 0,
      "qualified": 0,
      "booked": 0,
      "won": 0,
      "lost": 0
    }
  }
}
---
# Campaign: ProxyStaff Outbound

## Objective

Book discovery calls with busy business owners who can benefit from AI automation. Success = getting replies that lead to calls.

## Ideal Customer Profile (ICP)

**Who:**
- Owner-operated small businesses (1-3 people)
- Industries: Realtors, Plumbers, HVAC, Electricians, General Contractors
- Location: Salt Lake City, UT
- Pain: Drowning in messages, leads falling through cracks, no time for follow-up

**Good fit signals:**
- Owner-operated (we're contacting the owner directly)
- Active Google listing with reviews
- Evidence of active operation
- Open to automation/technology (chatbots on site = good sign)

**Disqualifiers:**
- Franchises (ServiceMaster, Keller Williams teams with admin, etc.)
- Multi-location businesses
- Dedicated office staff or receptionist
- Large corporate chains
- Not owner-operated

## Messaging Guidelines

**Tone:** Friendly, chill, professional but not corporate - like a helpful CS student

**Voice:** First person ("I built this...", "I noticed...")

**AI Positioning:** Lean into it - "Powered by Claude Opus 4.5 from Anthropic, the most capable AI model available"

**Main Pitch:** Outcomes
- Time saved
- Productivity increased
- Revenue increased
- Quality of service increased

**Pain points to hit:**
- Missed calls = missed revenue
- Spending nights/weekends on follow-up
- Leads going cold while you're on a job
- Can't be in two places at once

**Phrases that fit:**
- "Hey [name]"
- "Saw your business and thought..."
- "No worries if not your thing"
- "Happy to show you how it works"

**Avoid:**
- "I hope this email finds you well"
- "Per my previous email"
- Corporate buzzwords (synergy, leverage, circle back)
- Pushy/salesy language

**Your angle:**
> "I'm a local developer who built this specifically for busy business owners. It runs on the best AI available - not some generic chatbot. Happy to demo it, no pitch."

## Sequence Strategy

| Touch | Timing | Focus |
|-------|--------|-------|
| 1 | Day 0 | Personalized intro, specific observation about their business |
| 2 | Day 5 | Friendly follow-up, add a new angle or insight |
| 3 | Day 12 | Final touch, soft close, leave door open |

After sequence: Park for 5 months, then re-engage with fresh angle.

## Compliance

- CAN-SPAM compliant (unsubscribe option in every email)
- Physical address included
- Immediate unsubscribe honoring
- No misleading subject lines

## Notes

- All emails require approval before sending
- 1 hour delay after approval before send
- Sends 7 AM - 9 PM Mountain, including weekends
- LinkedIn and social channels planned for future
