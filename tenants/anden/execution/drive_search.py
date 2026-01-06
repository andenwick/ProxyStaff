#!/usr/bin/env python3
"""
Search Google Drive files using Drive API query syntax.

Required environment variables:
- GOOGLE_DRIVE_CLIENT_ID
- GOOGLE_DRIVE_CLIENT_SECRET
- GOOGLE_DRIVE_REFRESH_TOKEN
"""

import json
import os
import sys

from google_drive_utils import get_access_token, drive_get_json


def sanitize_text(value):
    return value.replace("'", "\\'")


def main():
    try:
        input_data = json.loads(sys.stdin.read())

        query = input_data.get("query")
        text = input_data.get("text")
        folder_id = input_data.get("folder_id") or os.environ.get("GOOGLE_DRIVE_ROOT_FOLDER_ID")
        page_size = input_data.get("page_size", 10)
        include_trashed = input_data.get("include_trashed", False)
        order_by = input_data.get("order_by", "modifiedTime desc")
        page_token = input_data.get("page_token")

        try:
            page_size = int(page_size)
        except (TypeError, ValueError):
            page_size = 10

        if page_size < 1:
            page_size = 1
        if page_size > 1000:
            page_size = 1000

        query_parts = []
        if not include_trashed:
            query_parts.append("trashed = false")
        if folder_id:
            query_parts.append(f"'{folder_id}' in parents")
        if query:
            query_parts.append(f"({query})")
        elif text:
            safe_text = sanitize_text(str(text))
            query_parts.append(f"(name contains '{safe_text}' or fullText contains '{safe_text}')")

        q = " and ".join(query_parts) if query_parts else None

        params = {
            "pageSize": page_size,
            "fields": "files(id,name,mimeType,modifiedTime,size,webViewLink,parents),nextPageToken",
        }
        if q:
            params["q"] = q
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
            "files": files,
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
