#!/usr/bin/env python3
"""
Create a shareable link for a Drive file by setting "anyone with link" permissions.

Required environment variables:
- GOOGLE_DRIVE_CLIENT_ID
- GOOGLE_DRIVE_CLIENT_SECRET
- GOOGLE_DRIVE_REFRESH_TOKEN
"""

import json
import sys

from google_drive_utils import get_access_token, drive_get_json, drive_json_request


def main():
    try:
        input_data = json.loads(sys.stdin.read())

        file_id = input_data.get("file_id")
        role = input_data.get("role", "reader")
        allow_discovery = input_data.get("allow_discovery", False)

        if not file_id:
            print(json.dumps({"status": "error", "message": "Missing 'file_id' parameter"}))
            sys.exit(1)

        if role not in ("reader", "writer", "commenter"):
            print(json.dumps({"status": "error", "message": "Invalid role. Use reader, commenter, or writer."}))
            sys.exit(1)

        access_token = get_access_token()

        permission_payload = {
            "type": "anyone",
            "role": role,
            "allowFileDiscovery": bool(allow_discovery),
        }

        permission_result = drive_json_request(
            access_token,
            f"/files/{file_id}/permissions",
            payload=permission_payload,
            method="POST",
        )

        file_info = drive_get_json(
            access_token,
            f"/files/{file_id}",
            params={"fields": "id,name,mimeType,webViewLink,webContentLink"},
        )

        print(json.dumps({
            "status": "success",
            "permission": permission_result,
            "file": file_info,
        }))

    except json.JSONDecodeError as exc:
        print(json.dumps({"status": "error", "message": f"Invalid JSON input: {exc}"}))
        sys.exit(1)
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
