#!/usr/bin/env python3
"""
Export a Drive file to PDF and save it back to Drive as a new file.

Supports Google Docs, Sheets, and Slides. If the source is already a PDF,
it will be copied as a new PDF file.

Required environment variables:
- GOOGLE_DRIVE_CLIENT_ID
- GOOGLE_DRIVE_CLIENT_SECRET
- GOOGLE_DRIVE_REFRESH_TOKEN
"""

import json
import sys
import uuid

from google_drive_utils import get_access_token, drive_get_json, drive_request, UPLOAD_API_BASE


def is_google_doc(mime_type):
    return mime_type.startswith("application/vnd.google-apps.")


def build_output_name(base_name):
    if base_name.lower().endswith(".pdf"):
        return base_name
    return f"{base_name}.pdf"


def main():
    try:
        input_data = json.loads(sys.stdin.read())

        file_id = input_data.get("file_id")
        output_name = input_data.get("output_name")
        parent_id = input_data.get("parent_id")

        if not file_id:
            print(json.dumps({"status": "error", "message": "Missing 'file_id' parameter"}))
            sys.exit(1)

        access_token = get_access_token()

        metadata = drive_get_json(
            access_token,
            f"/files/{file_id}",
            params={"fields": "id,name,mimeType"},
        )

        source_name = metadata.get("name", "Drive File")
        mime_type = metadata.get("mimeType", "")

        if not output_name:
            output_name = build_output_name(source_name)

        if is_google_doc(mime_type):
            content_bytes = drive_request(
                access_token,
                f"/files/{file_id}/export",
                params={"mimeType": "application/pdf"},
            )
        elif mime_type == "application/pdf":
            content_bytes = drive_request(
                access_token,
                f"/files/{file_id}",
                params={"alt": "media"},
            )
        else:
            print(json.dumps({
                "status": "error",
                "message": f"File type not supported for PDF export: {mime_type}",
            }))
            sys.exit(1)

        upload_metadata = {
            "name": output_name,
            "mimeType": "application/pdf",
        }
        if parent_id:
            upload_metadata["parents"] = [parent_id]

        boundary = f"=============={uuid.uuid4().hex}=="
        delimiter = f"--{boundary}\r\n".encode("utf-8")
        close_delim = f"--{boundary}--\r\n".encode("utf-8")

        body = b"".join([
            delimiter,
            b"Content-Type: application/json; charset=utf-8\r\n\r\n",
            json.dumps(upload_metadata).encode("utf-8"),
            b"\r\n",
            delimiter,
            b"Content-Type: application/pdf\r\n\r\n",
            content_bytes,
            b"\r\n",
            close_delim,
        ])

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
            "source": metadata,
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
