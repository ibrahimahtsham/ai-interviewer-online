#!/usr/bin/env bash
# AI Interviewer Online run script (Linux/macOS)
# Provides two options:
#   1) Normal run  - reuse venv, install/update deps
#   2) Clean run   - remove caches first, then proceed

set -euo pipefail

APP_FILE="app.py"
PYTHON_BIN="${PYTHON:-python3}"

usage() {
  cat <<EOF
Run options:
  1) Normal run (default)
  2) Clean run  (remove caches before starting)
You can pass the choice as first arg, e.g.:
  ./run.sh 2
Environment vars:
  PYTHON=python3.12   Override python executable
EOF
}

prompt_choice() {
  echo "Select option:" >&2
  echo "  1) Run normally" >&2
  echo "  2) Clean run" >&2
  read -rp "Enter choice (1/2): " choice
  echo "${choice:-1}"
}

ensure_python() {
  if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    if command -v python >/dev/null 2>&1; then
      PYTHON_BIN=python
    else
      echo "[ERROR] Python 3 not found." >&2
      exit 1
    fi
  fi
  echo "[INFO] Using $("$PYTHON_BIN" --version 2>&1)"
}

clean_caches() {
  echo "[INFO] Cleaning caches..."
  find . -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
  find . -type f -name "*.py[co]" -delete 2>/dev/null || true
  rm -rf .streamlit/cache 2>/dev/null || true
  rm -rf .pytest_cache .mypy_cache .ruff_cache 2>/dev/null || true
  if [[ -d .venv ]]; then
    echo "[INFO] Removing virtual environment (.venv)..."
    rm -rf .venv
  fi
  echo "[INFO] Cache cleanup complete." 
}

activate_venv() {
  if [[ ! -d .venv ]]; then
    echo "[INFO] Creating virtual environment (.venv)..."
    "$PYTHON_BIN" -m venv .venv
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate
  echo "[INFO] Active interpreter: $(python -c 'import sys;print(sys.executable)')"
}

install_deps() {
  if [[ -f requirements.txt ]]; then
    echo "[INFO] Upgrading pip..."
    python -m pip install --upgrade pip >/dev/null
    echo "[INFO] Installing dependencies from requirements.txt..."
    python -m pip install -r requirements.txt
  else
    echo "[WARN] requirements.txt not found; skipping install." >&2
  fi
}

verify_streamlit() {
  python - <<'PY'
import sys
try:
    import streamlit, os
    print(f"[OK] streamlit {streamlit.__version__} ({os.path.dirname(streamlit.__file__)})")
except Exception as e:
    print("[ERROR] streamlit import failed:", e)
    sys.exit(1)
PY
}

launch() {
  if [[ ! -f "$APP_FILE" ]]; then
    echo "[ERROR] $APP_FILE not found." >&2
    exit 1
  fi
  echo "[INFO] Launching app..."
  exec python -m streamlit run "$APP_FILE"
}

main() {
  local choice
  choice="${1:-}" 
  if [[ -z "$choice" ]]; then
    usage
    choice="$(prompt_choice)"
  fi
  ensure_python
  case "$choice" in
    1) echo "[MODE] Normal run" ;;
    2) echo "[MODE] Clean run"; clean_caches ;;
    *) echo "[ERROR] Invalid option '$choice' (use 1 or 2)" >&2; exit 2 ;;
  esac
  activate_venv
  install_deps
  verify_streamlit
  launch
}

main "$@"
