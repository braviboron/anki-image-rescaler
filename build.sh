#!/usr/bin/env bash
# Package the add-on into an upload-ready .ankiaddon file (for AnkiWeb).
# The .ankiaddon format is a plain zip with the source files at the root
# (no parent folder, and no meta.json).
set -euo pipefail
cd "$(dirname "$0")"

OUT="publications/anki-image-rescaler.ankiaddon"
mkdir -p publications
rm -f "$OUT"
zip -j "$OUT" src/__init__.py src/config.json src/config.md src/manifest.json
echo "Built $OUT"
