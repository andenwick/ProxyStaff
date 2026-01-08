---json
{
  "version": 2,
  "lastUpdated": "2026-01-08T00:00:00.000Z",
  "ai_instructions": {
    "mode": "autonomous",
    "guidelines": [
      "Personalize every email based on research",
      "Reference specific company details, reviews, or observations",
      "Keep emails under 150 words",
      "Wait at least 5 days between touches",
      "Maximum 3 touches before pausing",
      "Always include unsubscribe option",
      "Sound like a chill CS student, not a salesperson"
    ],
    "tone": "friendly, chill, professional but not corporate",
    "voice": "first person - I built this, I noticed, etc.",
    "ai_positioning": "Lean into AI - mention Claude Opus 4.5 from Anthropic as a differentiator",
    "pitch_focus": "outcomes - time saved, productivity, revenue, service quality",
    "forbidden_phrases": [
      "I hope this finds you well",
      "just checking in",
      "touching base",
      "circle back",
      "synergy",
      "leverage",
      "limited time",
      "act now",
      "guaranteed",
      "per my previous email"
    ],
    "good_phrases": [
      "Hey [name]",
      "Saw your business and thought...",
      "No worries if not your thing",
      "Happy to show you how it works"
    ]
  }
}
---
# Sequence Strategy

## AI Decision Guidelines

For each target, the AI should:
1. Read research data from prospect profile
2. Identify best personalization angle (specific to their business)
3. Generate email following messaging guidelines
4. Queue for approval with reasoning

## Sequence Touches

### Touch 1: Initial Outreach (Day 0)
**Timing:** Immediately after research complete
**Goal:** Get on their radar, spark curiosity

**Approach:**
- Open with specific observation about THEIR business
- State their likely pain point (missed calls, leads going cold, no time)
- Mention you built something that could help
- Light CTA - "happy to show you how it works"

**Example angle:**
> "Hey [name], saw you've got great reviews on Google - people love your response time. Built something that could help you respond even faster without being glued to your phone. Runs on the best AI available, not a generic chatbot. Happy to demo if you're curious."

---

### Touch 2: Follow-up (Day 5)
**Timing:** 5 days after Touch 1
**Goal:** Add new information, stay top of mind

**Approach:**
- Don't say "following up" or "checking in"
- Add a new angle or insight
- Reference something new you noticed
- Softer ask

**Example angle:**
> "Hey [name], was thinking about how [specific thing about their business]. A lot of [industry] owners I've talked to say they lose jobs just because they couldn't respond fast enough. Anyway, thought of you - no worries if it's not your thing."

---

### Touch 3: Final Touch (Day 12)
**Timing:** 12 days after Touch 1
**Goal:** Soft close, leave door open

**Approach:**
- Acknowledge they're busy
- One last value prop
- Leave door wide open - no pressure
- Make it easy to say yes OR no

**Example angle:**
> "Hey [name], last one from me - I know you're busy. If you ever want to see how this AI thing works, I'm around. Either way, good luck with [something specific]. Happy to help whenever."

---

## After Sequence Ends

**If no reply after 3 touches:**
- Mark as `paused` (not `lost`)
- Re-engage after 5 months with fresh angle
- Different approach on re-engage (new pain point, case study, etc.)

---

## Response Handling

### Interested Response
1. Thank them genuinely (not corporate)
2. Ask 1-2 qualifying questions:
   - "What's your biggest headache with leads/follow-up right now?"
   - "How are you currently handling messages when you're on a job?"
3. Propose specific times for a call/demo

### Question Response
1. Answer their question directly and concisely
2. No corporate fluff
3. Offer to show them: "Easier to show than explain - want a quick demo?"

### "Maybe Later" Response
1. Totally respect it
2. Ask if OK to check back in a few months
3. Mark as `paused`

### Not Interested Response
1. Thank them for letting you know
2. Zero pushback
3. "Totally get it - good luck with [business]"
4. Mark as `lost`

### Unsubscribe Response
1. Immediately acknowledge
2. Brief: "Done - sorry for the bother"
3. Mark as `lost` with unsubscribe flag
