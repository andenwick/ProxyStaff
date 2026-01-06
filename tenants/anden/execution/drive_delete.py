#!/usr/bin/env python3
"""
Delete a file from Google Drive.

Required environment variables:
- GOOGLE_DRIVE_CLIENT_ID
- GOOGLE_DRIVE_CLIENT_SECRET
- GOOGLE_DRIVE_REFRESH_TOKEN
"""

import json
import sys

from google_drive_utils import get_access_token, drive_request


def main():
    try:
        input_data = json.loads(sys.stdin.read())

        file_id = input_data.get("file_id")
        if not file_id:
            print(json.dumps({"status": "error", "message": "Missing 'file_id' parameter"}))
            sys.exit(1)

        access_token = get_access_token()
        drive_request(access_token, f"/files/{file_id}", method="DELETE")

        print(json.dumps({
            "status": "success",
            "file_id": file_id,
            "message": "File deleted",
        }))

    except json.JSONDecodeError as exc:
        print(json.dumps({"status": "error", "message": f"Invalid JSON input: {exc}"}))
        sys.exit(1)
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
