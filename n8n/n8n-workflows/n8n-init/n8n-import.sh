#!/bin/sh
set -e

if [ "$CURRENT_ENV" = "dev" ]; then
  echo "Dev environment detected, skipping init..."
  exec n8n
fi

HASH_DIR="/home/node/.n8n/hashes"
mkdir -p "$HASH_DIR"

WORKFLOWS_CHANGED=0

check_and_import_workflow() {
  FILE="$1"
  HASH_KEY="$2"
  HASH_FILE="$HASH_DIR/$HASH_KEY"

  CURRENT_HASH=$(md5sum "$FILE" | awk '{print $1}')
  STORED_HASH=$(cat "$HASH_FILE" 2>/dev/null || echo "none")

  if [ "$CURRENT_HASH" = "$STORED_HASH" ]; then
    echo "  Unchanged: $HASH_KEY"
  else
    echo "  Importing: $HASH_KEY"
    n8n import:workflow --input="$FILE"
    echo "$CURRENT_HASH" > "$HASH_FILE"
    WORKFLOWS_CHANGED=1
  fi
}

import_workflows_from_dir() {
  DIR="$1"

  if [ ! -d "$DIR" ]; then
    echo "No directory found at $DIR, skipping."
    return
  fi

  COUNT=0
  for FILE in "$DIR"/*.json; do
    [ -f "$FILE" ] || continue
    HASH_KEY=$(basename "$FILE" .json)
    check_and_import_workflow "$FILE" "$HASH_KEY"
    COUNT=$((COUNT + 1))
  done

  if [ "$COUNT" = "0" ]; then
    echo "No workflow files found in $DIR"
  fi
}

# ---- Credentials — always import, they're fast ----
echo "Importing credentials..."
[ -f "/home/node/.n8n-files/workflows/n8n_exports/all_credentials.json" ] && \
  n8n import:credentials --input=/home/node/.n8n-files/workflows/n8n_exports/all_credentials.json

# ---- Workflows — import individual files from workflows/ subdir ----
echo "Checking root workflows..."
import_workflows_from_dir "/home/node/.n8n-files/workflows/n8n_exports/workflows"

# ---- Activate once if anything changed ----
if [ "$WORKFLOWS_CHANGED" = "1" ]; then
  echo "Activating workflows..."
  n8n list:workflow | awk -F'|' '
  {
    gsub(/^[ \t]+|[ \t]+$/, "", $1);
    gsub(/^[ \t]+|[ \t]+$/, "", $2);
    if ($1 != "" && $1 != "ID") {
      system("echo \"  Activating: " $2 " (ID: " $1 ")\"");
      system("n8n publish:workflow --id=\"" $1 "\"");
    }
  }'
  echo "Activation complete."
else
  echo "No workflow changes detected, skipping activation."
fi

exec n8n