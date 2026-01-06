#!/usr/bin/env python3
"""
List folders in Google Drive.

Required environment variables:
- GOOGLE_DRIVE_CLIENT_ID
- GOOGLE_DRIVE_CLIENT_SECRET
- GOOGLE_DRIVE_REFRESH_TOKEN
"""

import json
import sys

from google_drive_utils import get_access_token, drive_get_json


def main():
    try:
        input_data = json.loads(sys.stdin.read())

        parent_id = input_data.get("parent_id")
        page_size = input_data.get("page_size", 25)
        page_token = input_data.get("page_token")
        include_trashed = input_data.get("include_trashed", False)
        order_by = input_data.get("order_by", "name")

        try:
            page_size = int(page_size)
        except (TypeError, ValueError):
            page_size = 25

        if page_size < 1:
            page_size = 1
        if page_size > 1000:
            page_size = 1000

        query_parts = ["mimeType = 'application/vnd.google-apps.folder'"]
        if not include_trashed:
            query_parts.append("trashed = false")
        if parent_id:
            query_parts.append(f"'{parent_id}' in parents")

        params = {
            "q": " and ".join(query_parts),
            "pageSize": page_size,
            "fields": "files(id,name,modifiedTime,webViewLink,parents),nextPageToken",
        }
        if order_by:
            params["orderBy"] = order_by
        if page_token:
            params["pageToken"] = page_token

        access_token = get_access_token()
        result = drive_get_json(access_token, "/files", params=params)

        files = result.get("files", [])
        next_token = result.get("nextPageToken")

        print(json.dumps({
            "status": "success",
            "count": len(files),
            "folders": files,
            "next_page_token": next_token,
        }))

    except json.JSONDecodeError as exc:
        print(json.dumps({"status": "error", "message": f"Invalid JSON input: {exc}"}))
        sys.exit(1)
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
