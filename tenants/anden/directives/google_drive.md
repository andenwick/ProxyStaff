# Google Drive SOP

## Goal
Find and read Google Drive files for the user.

## Available Tools
- `drive_search` - Search files by query or plain text
- `drive_read_text` - Read text content from a file by ID
- `drive_list_recent` - List recently modified files
- `drive_list_folders` - List folders (optionally within a parent)
- `drive_upload` - Upload a local file to Drive
- `drive_create_doc` - Create a Google Doc (optional content)
- `drive_move_rename` - Move and/or rename a file
- `drive_share_link` - Create a shareable link
- `drive_export_pdf` - Export a file to PDF in Drive
- `drive_delete` - Delete a file
- `drive_move_to_folder_by_name` - Move a file into a folder by name
- `docs_format` - Format Google Docs content (fonts, colors, headings, bullets, etc.)

## When to Use

| User Request | Tool to Use |
|--------------|-------------|
| "Find the latest listing agreement" | `drive_search` + `drive_read_text` |
| "Search Drive for my notes on X" | `drive_search` |
| "Open that doc" | `drive_read_text` with file ID |
| "Show my recent files" | `drive_list_recent` |
| "List my Drive folders" | `drive_list_folders` |
| "Upload this file to Drive" | `drive_upload` |
| "Create a doc called X" | `drive_create_doc` |
| "Rename/move this file" | `drive_move_rename` |
| "Share this file" | `drive_share_link` |
| "Export this to PDF" | `drive_export_pdf` |
| "Delete this file" | `drive_delete` |
| "Move to folder named X" | `drive_move_to_folder_by_name` |
| "Make the title bigger and blue" | `docs_format` |

## Searching Files

Use `drive_search` with either:
- `text` for simple searches, or
- `query` for advanced Drive query syntax

Examples:
```json
{ "text": "listing agreement", "page_size": 10 }
```

```json
{
  "query": "name contains 'listing' and mimeType = 'application/vnd.google-apps.document'",
  "page_size": 10
}
```

If the user mentions a specific folder and you have the ID, include:
```json
{ "text": "notes", "folder_id": "<folder-id>" }
```

## Reading Files

Use `drive_read_text` with the file ID from search results:
```json
{ "file_id": "abc123" }
```

If the file is a Google Sheet, `drive_read_text` exports CSV by default.

## Listing Recent Files

Use `drive_list_recent` to show recently modified files:
```json
{ "page_size": 10 }
```

## Listing Folders

Use `drive_list_folders` to list folders:
```json
{ "page_size": 25 }
```

To list folders inside a parent folder:
```json
{ "parent_id": "folder123" }
```

## Uploading Files

Use `drive_upload` with a local file path:
```json
{ "file_path": "C:\\path\\to\\file.pdf", "parent_id": "folder123" }
```

## Creating Docs

Use `drive_create_doc` with a title and optional content:
```json
{ "title": "New Listing Notes", "content": "Draft notes go here." }
```

## Rename or Move

Use `drive_move_rename`:
```json
{ "file_id": "abc123", "new_name": "Updated Name" }
```

```json
{ "file_id": "abc123", "new_parent_id": "folder123" }
```

## Share Links

Use `drive_share_link` to create a shareable link:
```json
{ "file_id": "abc123", "role": "reader" }
```

## Export to PDF

Use `drive_export_pdf` to create a PDF in Drive:
```json
{ "file_id": "abc123", "output_name": "Listing.pdf" }
```

## Delete

Use `drive_delete` for removals:
```json
{ "file_id": "abc123" }
```

## Move to Folder by Name

Use `drive_move_to_folder_by_name`:
```json
{ "file_id": "abc123", "folder_name": "Listings" }
```

To create the folder if missing:
```json
{ "file_id": "abc123", "folder_name": "Listings", "create_if_missing": true }
```

## Format Google Docs

Use `docs_format` for typography, colors, headings, alignment, bullets, and text insert/replace.
Prefer `match` to target a specific phrase; use `target: "document"` for whole-doc formatting.

Example:
```json
{
  "doc_id": "abc123",
  "operations": [
    { "type": "style_text", "match": "Listing Summary", "font_size_pt": 20, "bold": true, "color_rgb": [0, 102, 204] },
    { "type": "paragraph_style", "match": "Listing Summary", "named_style_type": "HEADING_1", "alignment": "CENTER" },
    { "type": "replace_text", "find": "TBD", "replace": "Finalized" }
  ]
}
```

## Workflow

1. Use `drive_search` to find matching files
2. Present name + modified date, ask which file to open
3. Use `drive_read_text` for the selected file
4. Summarize or quote key sections as requested

## Edge Cases

| Situation | Action |
|-----------|--------|
| No results | Ask for different keywords or a folder |
| Too many results | Ask the user to narrow the search |
| Non-text file (PDF/image) | Explain it cannot be read as text and ask for another file |
| Truncated output | Offer to read a specific section or rerun with a larger limit |
| Share/delete request | Confirm intent before running the tool |
