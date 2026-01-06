#!/usr/bin/env python3
"""
Simple echo test tool - returns the input back with a timestamp.
Used to verify the DOE framework is working correctly.
"""

import sys
import json
from datetime import datetime


def main():
    try:
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())

        message = input_data.get("message", "No message provided")

        result = {
            "status": "success",
            "echo": message,
            "timestamp": datetime.now().isoformat(),
            "note": "DOE framework is working!"
        }

        print(json.dumps(result))

    except json.JSONDecodeError as e:
        print(json.dumps({"status": "error", "message": f"Invalid JSON input: {e}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
