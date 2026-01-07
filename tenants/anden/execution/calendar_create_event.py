#!/usr/bin/env python3
"""
Create a Google Calendar event for discovery calls.
Sends calendar invite to the prospect.

Required env vars:
- GOOGLE_CALENDAR_CLIENT_ID (or GOOGLE_DRIVE_CLIENT_ID)
- GOOGLE_CALENDAR_CLIENT_SECRET (or GOOGLE_DRIVE_CLIENT_SECRET)
- GOOGLE_CALENDAR_REFRESH_TOKEN
"""
import sys
import json
from datetime import datetime, timedelta

from google_calendar_utils import get_access_token, calendar_post_json


def create_calendar_event(
    title: str,
    start_datetime: str,
    duration_minutes: int = 30,
    attendee_email: str = None,
    attendee_name: str = None,
    description: str = None,
    location: str = None,
    timezone: str = "America/Denver",
    send_invite: bool = True
) -> dict:
    """
    Create a Google Calendar event.

    Args:
        title: Event title
        start_datetime: Start time (ISO format or "YYYY-MM-DD HH:MM")
        duration_minutes: Duration in minutes
        attendee_email: Email to invite
        attendee_name: Display name for attendee
        description: Event description
        location: Event location (can be a video call link)
        timezone: Timezone
        send_invite: Whether to send calendar invite

    Returns:
        Dictionary with event details and link
    """
    try:
        access_token = get_access_token()
    except RuntimeError as e:
        return {"error": str(e)}

    # Parse start time
    try:
        if 'T' in start_datetime:
            start_dt = datetime.fromisoformat(start_datetime.replace('Z', ''))
        else:
            start_dt = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M')
    except ValueError:
        return {"error": f"Invalid datetime format: {start_datetime}. Use YYYY-MM-DD HH:MM or ISO format."}

    end_dt = start_dt + timedelta(minutes=duration_minutes)

    # Build event body
    event = {
        'summary': title,
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': timezone,
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                {'method': 'popup', 'minutes': 30},  # 30 min before
            ],
        },
    }

    if description:
        event['description'] = description

    if location:
        event['location'] = location

    # Add attendee
    if attendee_email:
        attendee = {'email': attendee_email}
        if attendee_name:
            attendee['displayName'] = attendee_name
        event['attendees'] = [attendee]

    # Add Google Meet conference
    event['conferenceData'] = {
        'createRequest': {
            'requestId': f"proxystaff-{int(start_dt.timestamp())}",
            'conferenceSolutionKey': {'type': 'hangoutsMeet'}
        }
    }

    # Create event via API
    params = {
        'conferenceDataVersion': 1,
        'sendUpdates': 'all' if send_invite and attendee_email else 'none'
    }

    try:
        created_event = calendar_post_json(access_token, "/calendars/primary/events", event, params=params)
    except RuntimeError as e:
        return {"error": f"Calendar API error: {str(e)}"}

    # Extract meeting link
    meet_link = None
    if 'conferenceData' in created_event:
        for entry in created_event.get('conferenceData', {}).get('entryPoints', []):
            if entry.get('entryPointType') == 'video':
                meet_link = entry.get('uri')
                break

    return {
        "success": True,
        "event_id": created_event.get('id'),
        "event_link": created_event.get('htmlLink'),
        "meet_link": meet_link,
        "title": title,
        "start": start_dt.isoformat(),
        "end": end_dt.isoformat(),
        "timezone": timezone,
        "attendee": attendee_email,
        "invite_sent": send_invite and attendee_email is not None,
        "message": f"Event created successfully. {'Calendar invite sent to ' + attendee_email if send_invite and attendee_email else 'No invite sent.'}"
    }


def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        input_data = {}

    title = input_data.get("title")
    start_datetime = input_data.get("start_datetime") or input_data.get("datetime")

    if not title:
        print(json.dumps({"error": "title parameter is required"}))
        return

    if not start_datetime:
        print(json.dumps({"error": "start_datetime parameter is required (YYYY-MM-DD HH:MM or ISO format)"}))
        return

    result = create_calendar_event(
        title=title,
        start_datetime=start_datetime,
        duration_minutes=input_data.get("duration_minutes", 30),
        attendee_email=input_data.get("attendee_email"),
        attendee_name=input_data.get("attendee_name"),
        description=input_data.get("description"),
        location=input_data.get("location"),
        timezone=input_data.get("timezone", "America/Denver"),
        send_invite=input_data.get("send_invite", True)
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
