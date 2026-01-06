#!/usr/bin/env python3
"""
Move and/or rename a Google Drive file.

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
        new_name = input_data.get("new_name")
        new_parent_id = input_data.get("new_parent_id")
        keep_existing_parents = input_data.get("keep_existing_parents", False)

        if not file_id:
            print(json.dumps({"status": "error", "message": "Missing 'file_id' parameter"}))
            sys.exit(1)

        if not new_name and not new_parent_id:
            print(json.dumps({"status": "error", "message": "Provide 'new_name' and/or 'new_parent_id'"}))
            sys.exit(1)

        access_token = get_access_token()

        params = {"fields": "id,name,mimeType,webViewLink,parents"}
        payload = {}

        if new_name:
            payload["name"] = new_name

        if new_parent_id:
            params["addParents"] = new_parent_id
            if not keep_existing_parents:
                metadata = drive_get_json(access_token, f"/files/{file_id}", params={"fields": "parents"})
                parents = metadata.get("parents", [])
                if parents:
                    params["removeParents"] = ",".join(parents)

        result = drive_json_request(
            access_token,
            f"/files/{file_id}",
            params=params,
            method="PATCH",
            payload=payload,
        )

        print(json.dumps({
            "status": "success",
            "file": result,
        }))

    except json.JSONDecodeError as exc:
        print(json.dumps({"status": "error", "message": f"Invalid JSON input: {exc}"}))
        sys.exit(1)
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
