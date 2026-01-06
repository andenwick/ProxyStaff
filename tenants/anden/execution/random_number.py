#!/usr/bin/env python3
import sys
import json
import random

def main():
    input_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}

    min_val = input_data.get("min", 1)
    max_val = input_data.get("max", 10)

    result = random.randint(min_val, max_val)
    print(json.dumps({"number": result}))

if __name__ == "__main__":
    main()
