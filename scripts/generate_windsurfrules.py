#!/usr/bin/env python3
"""
Script to generate a .windsurfrules file in the repo root by concatenating all files in the .cursor/rules directory.
Overwrites any existing .windsurfrules file.
"""

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_DIR = os.path.join(REPO_ROOT, ".cursor", "rules")
OUTPUT_FILE = os.path.join(REPO_ROOT, ".windsurfrules")


def main():
    if not os.path.isdir(RULES_DIR):
        print(f"Rules directory not found: {RULES_DIR}", file=sys.stderr)
        sys.exit(1)

    rule_files = sorted(
        [f for f in os.listdir(RULES_DIR) if os.path.isfile(os.path.join(RULES_DIR, f))]
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        for filename in rule_files:
            filepath = os.path.join(RULES_DIR, filename)
            with open(filepath, encoding="utf-8") as infile:
                outfile.write(infile.read())
                outfile.write("\n")  # Separate files with a newline
    print(f".windsurfrules generated at {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
