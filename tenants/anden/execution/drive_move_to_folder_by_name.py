#!/usr/bin/env python3
"""
Move a Drive file into a folder resolved by name.

Required environment variables:
- GOOGLE_DRIVE_CLIENT_ID
- GOOGLE_DRIVE_CLIENT_SECRET
- GOOGLE_DRIVE_REFRESH_TOKEN
"""

import json
import sys

from google_drive_utils import get_access_token, drive_get_json, drive_json_request


def find_folder(access_token, folder_name, parent_id=None):
    safe_name = folder_name.replace("'", "\\'")
    query_parts = [
        "mimeType = 'application/vnd.google-apps.folder'",
        f"name = '{safe_name}'",
        "trashed = false",
    ]
    if parent_id:
        query_parts.append(f"'{parent_id}' in parents")

    params = {
        "q": " and ".join(query_parts),
        "fields": "files(id,name,parents),nextPageToken",
        "pageSize": 10,
    }
    return drive_get_json(access_token, "/files", params=params)


def main():
    try:
        input_data = json.loads(sys.stdin.read())

        file_id = input_data.get("file_id")
        folder_name = input_data.get("folder_name")
        parent_id = input_data.get("parent_id")
        create_if_missing = bool(input_data.get("create_if_missing", False))
        keep_existing_parents = bool(input_data.get("keep_existing_parents", False))

        if not file_id:
            print(json.dumps({"status": "error", "message": "Missing 'file_id' parameter"}))
            sys.exit(1)
        if not folder_name:
            print(json.dumps({"status": "error", "message": "Missing 'folder_name' parameter"}))
            sys.exit(1)

        access_token = get_access_token()

        search_result = find_folder(access_token, folder_name, parent_id=parent_id)
        folders = search_result.get("files", [])

        if len(folders) == 0:
            if not create_if_missing:
                print(json.dumps({
                    "status": "error",
                    "message": f"Folder not found: {folder_name}",
                }))
                sys.exit(1)

            folder_payload = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder",
            }
            if parent_id:
                folder_payload["parents"] = [parent_id]

            created = drive_json_request(
                access_token,
                "/files",
                payload=folder_payload,
                method="POST",
            )
            folder_id = created.get("id")
        elif len(folders) > 1:
            print(json.dumps({
                "status": "error",
                "message": f"Multiple folders found named '{folder_name}'. Use folder_id instead.",
                "folders": folders,
            }))
            sys.exit(1)
        else:
            folder_id = folders[0].get("id")

        if not folder_id:
            print(json.dumps({"status": "error", "message": "Unable to resolve folder ID"}))
            sys.exit(1)

        params = {"addParents": folder_id, "fields": "id,name,parents,webViewLink,mimeType"}
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
            payload={},
        )

        print(json.dumps({
            "status": "success",
            "folder_id": folder_id,
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
