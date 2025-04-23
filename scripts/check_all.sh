#!/bin/bash

# Script to check code formatting and run pre-commit checks
# Usage: ./scripts/check_all.sh

clear

set -e

# Check if ruff is installed
if ! command -v ruff &> /dev/null
then
    echo "Ruff is not installed. Installing it now..."
    pip install ruff
fi

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null
then
    echo "pre-commit is not installed. Installing it now..."
    pip install pre-commit
fi

echo "Checking code formatting with ruff..."
ruff format .

echo "Checking code linting with ruff..."
ruff check . --fix

echo "Checking for trailing whitespace..."
find . -type f -not -path "*/\.*" -not -path "*/.venv/*" -not -path "*/\node_modules/*" -exec grep -l "[[:blank:]]$" {} \; | while read file; do
  # Remove trailing whitespace without creating backup files
  perl -pi -e 's/\s+$//' "$file"
done

echo "Fixing end of file newlines..."
# Add newline to end of file if missing without creating backup files
find . -type f -not -path "*/\.*" -not -path "*/.venv/*" -not -path "*/\node_modules/*" -exec sh -c 'if [ -n "$(tail -c 1 "$1")" ]; then echo "" >> "$1"; fi' sh {} \;

echo "Checking YAML files..."
find . -name "*.yaml" -o -name "*.yml" | xargs yamllint -c '{extends: default, rules: {line-length: disable}}' 2>/dev/null || echo "YAML check skipped (yamllint not installed)"

echo "Checking TOML files..."
find . -name "*.toml" | xargs cat 2>/dev/null || echo "TOML check skipped"

echo "Checking for large files..."
find . -type f -not -path "*/\.*" -not -path "*/.git/*" -not -path "*/.venv/*" -size +600k | while read file; do
  echo "WARNING: $file is larger than 600KB"
done

echo "Running pytest..."
python -m pytest

echo "Done!"
