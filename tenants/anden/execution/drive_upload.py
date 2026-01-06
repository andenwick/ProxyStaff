#!/usr/bin/env python3
"""
Upload a file to Google Drive.

Required environment variables:
- GOOGLE_DRIVE_CLIENT_ID
- GOOGLE_DRIVE_CLIENT_SECRET
- GOOGLE_DRIVE_REFRESH_TOKEN
"""

import json
import mimetypes
import os
import sys
import uuid

from google_drive_utils import get_access_token, drive_request, UPLOAD_API_BASE


def main():
    try:
        input_data = json.loads(sys.stdin.read())

        file_path = input_data.get("file_path")
        name = input_data.get("name")
        parent_id = input_data.get("parent_id")
        mime_type = input_data.get("mime_type")
        drive_mime_type = input_data.get("drive_mime_type")

        if not file_path:
            print(json.dumps({"status": "error", "message": "Missing 'file_path' parameter"}))
            sys.exit(1)

        if not os.path.isfile(file_path):
            print(json.dumps({"status": "error", "message": f"File not found: {file_path}"}))
            sys.exit(1)

        if not name:
            name = os.path.basename(file_path)

        if not mime_type:
            guessed, _ = mimetypes.guess_type(file_path)
            mime_type = guessed or "application/octet-stream"

        with open(file_path, "rb") as handle:
            file_bytes = handle.read()

        metadata = {"name": name}
        if parent_id:
            metadata["parents"] = [parent_id]
        if drive_mime_type:
            metadata["mimeType"] = drive_mime_type

        boundary = f"=============={uuid.uuid4().hex}=="
        delimiter = f"--{boundary}\r\n".encode("utf-8")
        close_delim = f"--{boundary}--".encode("utf-8")

        body = b"".join([
            delimiter,
            b"Content-Type: application/json; charset=utf-8\r\n\r\n",
            json.dumps(metadata).encode("utf-8"),
            b"\r\n",
            delimiter,
            f"Content-Type: {mime_type}\r\n\r\n".encode("utf-8"),
            file_bytes,
            b"\r\n",
            close_delim,
        ])

        access_token = get_access_token()
        raw = drive_request(
            access_token,
            "/files",
            params={"uploadType": "multipart", "fields": "id,name,mimeType,webViewLink,parents"},
            method="POST",
            data=body,
            headers={"Content-Type": f"multipart/related; boundary={boundary}"},
            api_base=UPLOAD_API_BASE,
        )

        result = json.loads(raw.decode("utf-8"))
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
