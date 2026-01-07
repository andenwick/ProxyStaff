#!/usr/bin/env python3
"""
Get availability from Google Calendar for booking discovery calls.
Uses refresh token pattern from environment variables.

Required env vars:
- GOOGLE_CALENDAR_CLIENT_ID (or GOOGLE_DRIVE_CLIENT_ID)
- GOOGLE_CALENDAR_CLIENT_SECRET (or GOOGLE_DRIVE_CLIENT_SECRET)
- GOOGLE_CALENDAR_REFRESH_TOKEN
"""
import sys
import json
from datetime import datetime, timedelta

from google_calendar_utils import get_access_token, calendar_post_json


def get_busy_times(start_date: str, end_date: str, timezone: str = "America/Denver") -> list:
    """
    Get busy time blocks from Google Calendar using freebusy API.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        timezone: Timezone for results

    Returns:
        List of busy time blocks
    """
    try:
        access_token = get_access_token()
    except RuntimeError as e:
        return {"error": str(e)}

    # Parse dates and add time component
    time_min = f"{start_date}T00:00:00Z"
    time_max = f"{end_date}T23:59:59Z"

    # Query freebusy API
    body = {
        "timeMin": time_min,
        "timeMax": time_max,
        "timeZone": timezone,
        "items": [{"id": "primary"}]
    }

    try:
        result = calendar_post_json(access_token, "/freeBusy", body)
    except RuntimeError as e:
        return {"error": f"Calendar API error: {str(e)}"}

    busy_times = []
    for busy in result.get('calendars', {}).get('primary', {}).get('busy', []):
        busy_times.append({
            "start": busy['start'],
            "end": busy['end']
        })

    return busy_times


def get_available_slots(
    start_date: str,
    end_date: str,
    slot_duration_minutes: int = 30,
    day_start_hour: int = 9,
    day_end_hour: int = 17,
    timezone: str = "America/Denver"
) -> dict:
    """
    Get available time slots for booking.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        slot_duration_minutes: Duration of each slot
        day_start_hour: Business day start (24h)
        day_end_hour: Business day end (24h)
        timezone: Timezone

    Returns:
        Dictionary with available slots by day
    """
    busy_times = get_busy_times(start_date, end_date, timezone)

    if isinstance(busy_times, dict) and "error" in busy_times:
        return busy_times

    # Parse busy times into datetime objects
    busy_periods = []
    for busy in busy_times:
        try:
            start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
            end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
            busy_periods.append((start, end))
        except:
            pass

    # Generate slots
    start_dt = datetime.fromisoformat(start_date)
    end_dt = datetime.fromisoformat(end_date)

    available_slots = {}
    current_date = start_dt

    while current_date <= end_dt:
        # Skip weekends
        if current_date.weekday() >= 5:
            current_date += timedelta(days=1)
            continue

        date_str = current_date.strftime('%Y-%m-%d')
        day_name = current_date.strftime('%A')
        available_slots[date_str] = {
            "day": day_name,
            "slots": []
        }

        # Generate time slots for this day
        slot_start = current_date.replace(hour=day_start_hour, minute=0, second=0, microsecond=0)
        day_end = current_date.replace(hour=day_end_hour, minute=0, second=0, microsecond=0)

        while slot_start + timedelta(minutes=slot_duration_minutes) <= day_end:
            slot_end = slot_start + timedelta(minutes=slot_duration_minutes)

            # Check if slot overlaps with any busy period
            is_available = True
            for busy_start, busy_end in busy_periods:
                # Make naive for comparison (simplified)
                busy_start_naive = busy_start.replace(tzinfo=None)
                busy_end_naive = busy_end.replace(tzinfo=None)

                if not (slot_end <= busy_start_naive or slot_start >= busy_end_naive):
                    is_available = False
                    break

            if is_available:
                available_slots[date_str]["slots"].append({
                    "start": slot_start.strftime('%H:%M'),
                    "end": slot_end.strftime('%H:%M'),
                    "datetime": slot_start.isoformat()
                })

            slot_start = slot_end

        current_date += timedelta(days=1)

    # Count total available
    total_slots = sum(len(day["slots"]) for day in available_slots.values())

    return {
        "start_date": start_date,
        "end_date": end_date,
        "timezone": timezone,
        "slot_duration_minutes": slot_duration_minutes,
        "business_hours": f"{day_start_hour}:00-{day_end_hour}:00",
        "total_available_slots": total_slots,
        "availability": available_slots
    }


def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        input_data = {}

    # Default to next 5 business days
    today = datetime.now()
    default_start = today.strftime('%Y-%m-%d')
    default_end = (today + timedelta(days=7)).strftime('%Y-%m-%d')

    start_date = input_data.get("start_date", default_start)
    end_date = input_data.get("end_date", default_end)
    slot_duration = input_data.get("slot_duration_minutes", 30)
    day_start = input_data.get("day_start_hour", 9)
    day_end = input_data.get("day_end_hour", 17)
    timezone = input_data.get("timezone", "America/Denver")

    result = get_available_slots(
        start_date, end_date, slot_duration, day_start, day_end, timezone
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
