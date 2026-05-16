#!/usr/bin/env bash
# Copy the source files into the local Anki addons21 folder for live testing.
# Restart Anki fully afterwards to reload the add-on.
# Override the target with: ADDON_DIR=/path/to/addon ./deploy.sh
set -euo pipefail
cd "$(dirname "$0")"

ADDON_DIR="${ADDON_DIR:-$HOME/Library/Application Support/Anki2/addons21/1258277333}"
mkdir -p "$ADDON_DIR"
cp src/__init__.py src/config.json src/config.md src/manifest.json "$ADDON_DIR/"
echo "Deployed to: $ADDON_DIR"
echo "Restart Anki to load the changes."
