#!/usr/bin/env bash
# Package the add-on into a distributable .ankiaddon file.
# The .ankiaddon format is a plain zip with the source files at the root
# (no parent folder, and no meta.json).
set -euo pipefail
cd "$(dirname "$0")"

OUT="dist/anki-image-rescaler.ankiaddon"
mkdir -p dist
rm -f "$OUT"
zip -j "$OUT" src/__init__.py src/config.json src/config.md src/manifest.json
echo "Built $OUT"
