#!/usr/bin/env python3
"""
Read text content from a Google Drive file.

Supports Google Docs export and plain text files.

Required environment variables:
- GOOGLE_DRIVE_CLIENT_ID
- GOOGLE_DRIVE_CLIENT_SECRET
- GOOGLE_DRIVE_REFRESH_TOKEN
"""

import json
import sys

from google_drive_utils import get_access_token, drive_get_json, drive_request


TEXT_MIME_TYPES = {
    "application/json",
    "application/xml",
    "application/javascript",
    "application/x-javascript",
    "application/x-yaml",
    "text/plain",
    "text/csv",
    "text/markdown",
    "text/html",
    "text/xml",
}

GOOGLE_DOC_EXPORTS = {
    "application/vnd.google-apps.document": "text/plain",
    "application/vnd.google-apps.spreadsheet": "text/csv",
}


def is_text_mime(mime_type):
    if not mime_type:
        return False
    if mime_type.startswith("text/"):
        return True
    return mime_type in TEXT_MIME_TYPES


def clamp_bytes(value, max_bytes):
    if max_bytes and len(value) > max_bytes:
        return value[:max_bytes], True
    return value, False


def main():
    try:
        input_data = json.loads(sys.stdin.read())

        file_id = input_data.get("file_id")
        max_bytes = input_data.get("max_bytes", 50000)
        export_mime = input_data.get("export_mime")

        if not file_id:
            print(json.dumps({"status": "error", "message": "Missing 'file_id' parameter"}))
            sys.exit(1)

        try:
            max_bytes = int(max_bytes)
        except (TypeError, ValueError):
            max_bytes = 50000

        access_token = get_access_token()

        metadata = drive_get_json(
            access_token,
            f"/files/{file_id}",
            params={"fields": "id,name,mimeType,size,webViewLink"},
        )

        mime_type = metadata.get("mimeType", "")
        content_bytes = None

        if mime_type.startswith("application/vnd.google-apps."):
            if not export_mime:
                export_mime = GOOGLE_DOC_EXPORTS.get(mime_type)
            if not export_mime:
                print(json.dumps({
                    "status": "error",
                    "message": f"Unsupported Google Docs mime type for export: {mime_type}",
                }))
                sys.exit(1)

            content_bytes = drive_request(
                access_token,
                f"/files/{file_id}/export",
                params={"mimeType": export_mime},
            )
        else:
            if not is_text_mime(mime_type):
                print(json.dumps({
                    "status": "error",
                    "message": f"File mime type is not text-readable: {mime_type}",
                }))
                sys.exit(1)

            content_bytes = drive_request(
                access_token,
                f"/files/{file_id}",
                params={"alt": "media"},
            )

        content_bytes, truncated = clamp_bytes(content_bytes, max_bytes)
        text = content_bytes.decode("utf-8", errors="replace")

        print(json.dumps({
            "status": "success",
            "file": metadata,
            "text": text,
            "truncated": truncated,
            "bytes": len(content_bytes),
        }))

    except json.JSONDecodeError as exc:
        print(json.dumps({"status": "error", "message": f"Invalid JSON input: {exc}"}))
        sys.exit(1)
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
