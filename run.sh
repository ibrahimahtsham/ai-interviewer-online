#!/usr/bin/env bash
# Bootstrap script for AI Interviewer Online (Linux/macOS)
# - Ensures Python 3 present
# - Creates virtual environment if missing
# - Installs/updates dependencies
# - Launches Streamlit app

set -euo pipefail

# Detect python executable preference
PYTHON_BIN="${PYTHON:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  if command -v python >/dev/null 2>&1; then
    PYTHON_BIN=python
  else
    echo "[ERROR] Python 3 not found. Please install Python 3." >&2
    exit 1
  fi
fi

echo "[INFO] Using $("$PYTHON_BIN" --version)"

# Create venv if missing
if [ ! -d .venv ]; then
  echo "[INFO] Creating virtual environment (.venv)..."
  "$PYTHON_BIN" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

# Upgrade pip
echo "[INFO] Upgrading pip..."
python -m pip install --upgrade pip >/dev/null

# Install requirements
if [ -f requirements.txt ]; then
  echo "[INFO] Installing dependencies from requirements.txt..."
  pip install -r requirements.txt
else
  echo "[WARN] requirements.txt not found; continuing without dependency install." >&2
fi

echo "[INFO] Launching Streamlit app..."
exec streamlit run app.py
