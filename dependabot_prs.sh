#!/usr/bin/env bash

# Exit immediately if a pipeline returns a non-zero status
set -eo pipefail

# 1. Check if repository argument is provided
if [ -z "$1" ]; then
    echo "Error: No repository specified."
    echo "Usage: $0 <owner/repository>"
    echo "Example: $0 openSUSE/qem-bot"
    exit 1
fi

REPO="$1"

# 2. Check for required dependencies
for cmd in gh jq sed; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "Error: '$cmd' is required but not installed." >&2
        exit 1
    fi
done

# 3. Print the header
echo -e "DATE       | PACKAGE | VERSION CHANGE"
echo -e "-----------|---------|---------------"

# 4. Fetch and parse the PR data (last 30 days / 2592000 seconds)
gh pr list --repo "$REPO" \
           --author "app/dependabot" \
           --state all \
           --limit 1000 \
           --json title,createdAt \
           --jq '.[] | select((.createdAt | fromdateiso8601) >= (now - 2592000)) | "\(.createdAt)\t\(.title)"' | \
  sed -E -n 's/^([0-9]{4}-[0-9]{2}-[0-9]{2})T[^\t]+\t.*[bB]ump ([^ ]+) from ([^ ]+) to ([^ ]+).*/\1 | \2 | \3 -> \4/p'
