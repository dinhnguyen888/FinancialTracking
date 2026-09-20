#!/usr/bin/env bash
set -e

# Navigate to project root
cd "$(dirname "$0")/.."

# Activate virtualenv
source apps/.venv/bin/activate

# Set python path and run Flet app
export PYTHONPATH=.
python3 apps/main.py
