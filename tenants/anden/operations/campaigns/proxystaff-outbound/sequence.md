---json
{
  "version": 1,
  "lastUpdated": "2026-01-06T00:00:00.000Z",
  "ai_instructions": {
    "mode": "autonomous",
    "guidelines": [
      "Personalize every email based on research",
      "Reference specific company details or reviews",
      "Keep emails under 150 words",
      "Wait at least 3 days between touches",
      "Maximum 5 touches before stopping",
      "Always include unsubscribe option"
    ],
    "tone": "professional but approachable",
    "forbidden_phrases": [
      "I hope this finds you well",
      "just checking in",
      "touching base",
      "circle back",
      "limited time",
      "act now",
      "guaranteed"
    ]
  }
}
---
# Sequence Strategy

## AI Decision Guidelines

For each target, the AI should:
1. Read research data from target profile
2. Identify best personalization angle
3. Generate email following the `outbound_email` directive
4. Queue for approval with reasoning

## Sequence Touches

### Touch 1: Initial Outreach
**Timing:** Immediately after research complete
**Goal:** Get on their radar, spark curiosity
**Template approach:**
- Open with specific observation
- State their likely pain point
- Hint at solution
- Ask for 15-min chat

### Touch 2: Follow-up
**Timing:** 3-5 days after Touch 1
**Goal:** Add new information, stay top of mind
**Template approach:**
- Reference previous email
- Add one new insight or capability
- Softer ask

### Touch 3: Value-Add
**Timing:** 3-5 days after Touch 2
**Goal:** Provide value even if they don't respond
**Template approach:**
- Share a tip relevant to their industry
- Connect it to what we do
- No hard ask

### Touch 4: Different Angle
**Timing:** 5-7 days after Touch 3
**Goal:** Try new approach if previous didn't work
**Template approach:**
- Try different pain point or angle
- Mention a specific outcome/result
- Direct ask

### Touch 5: Breakup
**Timing:** 7 days after Touch 4
**Goal:** Last chance, give them easy out
**Template approach:**
- Acknowledge they're busy
- Ask if should stop emailing
- Leave door open

## Response Handling

### Interested Response
1. Thank them for replying
2. Ask 1-2 qualifying questions:
   - "What's your biggest challenge with [X] right now?"
   - "How are you currently handling [Y]?"
3. Propose specific times for a call

### Question Response
1. Answer their question directly
2. Keep answer concise
3. Pivot to "Happy to explain more on a quick call"

### Not Now Response
1. Thank them
2. Ask if OK to check back in 2-3 months
3. Mark as "nurture" stage

### Not Interested Response
1. Thank them for letting you know
2. No pushback
3. Mark as "lost"

### Unsubscribe Response
1. Immediately acknowledge
2. Brief apology for any inconvenience
3. Confirm removal
4. Mark as "lost" with unsubscribe flag
