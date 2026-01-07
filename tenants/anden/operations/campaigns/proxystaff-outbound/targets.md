---json
{
  "version": 1,
  "lastUpdated": "2026-01-06T00:00:00.000Z",
  "targets": []
}
---
# Campaign Targets

## Stage Definitions

| Stage | Description |
|-------|-------------|
| **Identified** | Added to campaign, not yet researched |
| **Researched** | Background research completed, ready for outreach |
| **Contacted** | At least one outreach email sent |
| **Replied** | Received any response (positive or negative) |
| **Qualified** | Confirmed interest and fit |
| **Booked** | Discovery call scheduled |
| **Won** | Became a customer |
| **Lost** | Declined, unsubscribed, or not a fit |

## Pipeline Flow

```
Identified → Researched → Contacted → Replied → Qualified → Booked → Won
                                  ↓                              ↓
                               (Lost)                         (Lost)
```

## Notes

- Targets added via `scrape_google_maps` or manual entry
- Research via `research_website` and `find_email`
- Move to "Researched" only when we have enough for personalization
- Move to "Contacted" after first email sent
- Move to "Lost" if unsubscribed or explicitly not interested
