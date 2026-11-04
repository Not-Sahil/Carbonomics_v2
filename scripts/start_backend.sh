#!/bin/bash
# Carbonomics v3 — Start Central Backend
set -e
cd "$(dirname "$0")/.."
echo "🌿 Carbonomics v3 — Starting Enterprise Backend..."

# Activate virtual environment if present
if [ -d ".venv" ]; then
  source .venv/bin/activate || source .venv/Scripts/activate
fi

python backend/api/app.py
