# Seahawks News Digest Workflow

## Overview
Automated workflow to scrape the latest Seahawks news from multiple authoritative sources and send a formatted HTML email digest.

## News Sources (Ranked by Authority)

**Tier 1: Official Team Source**
- Seahawks.com - Official team announcements

**Tier 2: Beat Reporters (Closest to Source)**
- Seattle Times - Bob Condotta (@bcondotta)
- Seattle Sports / MyNorthwest - Local radio/digital outlet

**Tier 3: Fan Analysis**
- Field Gulls - SB Nation fan perspective

**Tier 4: National Coverage**
- ESPN - National NFL coverage with Seahawks section

## How It Works

### Tools Created

1. **scrape_seahawks_news.py** - Scrapes news from all sources
   - Uses RSS feeds when available (Seattle Times, Field Gulls)
   - Falls back to HTML scraping for sites without RSS
   - Removes duplicate articles
   - Returns up to 20 articles by default

2. **format_news_email.py** - Formats articles into HTML email
   - Clean, mobile-friendly design
   - Seahawks colors (Navy #002244, Action Green #69BE28)
   - Shows source badge for each article
   - Includes summary and "Read more" link

3. **gmail_send_html.py** - Sends HTML emails via Gmail SMTP
   - Requires GMAIL_USER and GMAIL_APP_PASSWORD in .env

4. **send_seahawks_digest.py** - Main workflow (combines all three)
   - Scrapes news
   - Formats email
   - Sends to specified recipient

## Manual Usage

To send a digest now:

```bash
echo '{"to_email": "anden@aspenautomations.com", "max_articles": 15}' | python3 execution/send_seahawks_digest.py
```

Or via the MCP tool:

```json
{
  "tool": "send_seahawks_digest",
  "to_email": "anden@aspenautomations.com",
  "max_articles": 15
}
```

## Scheduling the Digest

To receive the digest automatically, use the schedule_task tool:

### Daily Morning Digest (8am)
```bash
echo '{"task": "send seahawks news digest to anden@aspenautomations.com", "schedule": "every day at 8:00", "task_type": "execute"}' | python shared_tools/schedule_task.py
```

### Twice Daily (Morning + Evening)
```bash
# Morning
echo '{"task": "send seahawks news digest to anden@aspenautomations.com", "schedule": "every day at 8:00", "task_type": "execute"}' | python shared_tools/schedule_task.py

# Evening
echo '{"task": "send seahawks news digest to anden@aspenautomations.com", "schedule": "every day at 18:00", "task_type": "execute"}' | python shared_tools/schedule_task.py
```

### Every 4 Hours (During Season)
```bash
echo '{"task": "send seahawks news digest to anden@aspenautomations.com", "schedule": "every 4 hours", "task_type": "execute"}' | python shared_tools/schedule_task.py
```

## Managing Scheduled Tasks

### List all scheduled digests
```bash
echo '{}' | python shared_tools/list_schedules.py
```

### Cancel a scheduled task
```bash
echo '{"task_id": "uuid-here"}' | python shared_tools/cancel_schedule.py
```

## Troubleshooting

### No articles found
- Some sources may have changed their HTML structure
- RSS feeds may be temporarily unavailable
- Try running the scraper with verbose output to see which sources failed

### Email not sending
- Verify GMAIL_USER and GMAIL_APP_PASSWORD are set in .env
- Gmail requires an "App Password" (not your regular password)
- Generate at: https://myaccount.google.com/apppasswords

### Duplicate articles
- The scraper has built-in deduplication based on title matching
- Articles with identical titles (normalized) will be filtered

## Improving Article Coverage

To get more articles, you can:

1. **Refine HTML selectors** - Update scrape_seahawks_news.py with better CSS selectors
2. **Add more sources** - Add functions like `scrape_si_seahawks()` for Sports Illustrated
3. **Use Twitter API** - Add beat reporter tweets (requires Twitter API key)

## Example Schedule for Peak Coverage

During regular season (Sept-Jan):
- **Gameday**: Every 2 hours
- **Non-gameday**: Once daily at 8am

During off-season (Feb-Aug):
- **Draft week**: Twice daily (8am, 6pm)
- **Free agency**: Twice daily (8am, 6pm)
- **Regular off-season**: Once weekly on Monday at 8am
