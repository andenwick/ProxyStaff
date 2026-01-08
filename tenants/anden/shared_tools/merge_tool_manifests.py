#!/usr/bin/env python3
"""
Merge Tool Manifests - Combines split tool manifests into a single file.

This utility reads all JSON files from execution/tools/ and merges them into
a single tool_manifest.json file. It's used by the MCP server to load tools.

Usage:
    python shared_tools/merge_tool_manifests.py

Output:
    Writes to execution/tool_manifest_merged.json
    Prints summary to stdout
"""

import sys
import json
from pathlib import Path


def merge_manifests():
    """Merge all tool manifests from execution/tools/ directory."""
    tools_dir = Path("execution/tools")

    if not tools_dir.exists():
        print(json.dumps({
            "status": "error",
            "message": "execution/tools/ directory not found"
        }))
        sys.exit(1)

    all_tools = []
    categories = {}

    # Read all JSON files
    for manifest_file in sorted(tools_dir.glob("*.json")):
        try:
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)

            category = manifest.get("category", "unknown")
            tools = manifest.get("tools", [])

            categories[category] = {
                "description": manifest.get("description", ""),
                "count": len(tools)
            }

            all_tools.extend(tools)

        except Exception as e:
            print(json.dumps({
                "status": "error",
                "message": f"Failed to load {manifest_file}: {str(e)}"
            }))
            sys.exit(1)

    # Write merged manifest
    merged_manifest = {
        "tools": all_tools
    }

    output_path = Path("execution/tool_manifest_merged.json")

    with open(output_path, 'w') as f:
        json.dump(merged_manifest, f, indent=2)

    # Print summary
    result = {
        "status": "success",
        "output_file": str(output_path),
        "total_tools": len(all_tools),
        "categories": categories
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    merge_manifests()
