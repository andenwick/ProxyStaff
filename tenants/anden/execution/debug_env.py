#!/usr/bin/env python3
"""Debug script to check environment variables passed to tools."""
import json
import os
import sys

def main():
    # Read stdin (required by tool contract)
    try:
        input_data = json.loads(sys.stdin.read())
    except:
        input_data = {}

    # Get all relevant env vars
    tenant_folder = os.environ.get("TENANT_FOLDER", "NOT_SET")
    gmail_addr = os.environ.get("GMAIL_ADDRESS", "NOT_SET")
    gmail_pass = os.environ.get("GMAIL_APP_PASSWORD", "NOT_SET")

    # Check if .env file exists
    env_path = os.path.join(tenant_folder, ".env") if tenant_folder != "NOT_SET" else "N/A"
    env_exists = os.path.exists(env_path) if tenant_folder != "NOT_SET" else False

    # Read .env content if exists
    env_content = ""
    if env_exists:
        try:
            with open(env_path, 'r') as f:
                # Show first 500 chars, mask passwords
                content = f.read()
                # Mask any password values
                lines = []
                for line in content.split('\n'):
                    if 'PASSWORD' in line and '=' in line:
                        key = line.split('=')[0]
                        lines.append(f"{key}=***MASKED***")
                    else:
                        lines.append(line)
                env_content = '\n'.join(lines)
        except Exception as e:
            env_content = f"Error reading: {e}"

    # List all env vars with GMAIL or TENANT
    relevant_vars = {k: v[:20] + "..." if len(v) > 20 else v
                     for k, v in os.environ.items()
                     if any(x in k for x in ["GMAIL", "TENANT", "PATH"])}

    result = {
        "status": "debug",
        "TENANT_FOLDER": tenant_folder,
        "env_path": env_path,
        "env_exists": env_exists,
        "env_content": env_content,
        "GMAIL_ADDRESS": gmail_addr[:5] + "..." if gmail_addr not in ["NOT_SET", ""] else gmail_addr,
        "GMAIL_APP_PASSWORD_set": gmail_pass not in ["NOT_SET", ""],
        "relevant_env_vars": list(relevant_vars.keys())
    }

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
