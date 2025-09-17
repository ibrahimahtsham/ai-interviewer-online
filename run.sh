#!/usr/bin/env bash
# AI Interviewer Online run script (Linux/macOS)
# Step 1: choose normal or clean run (sets up venv + installs deps)
# Step 2: choose what to run (Streamlit app or single LLM prompt)

set -euo pipefail

APP_FILE="app.py"
PYTHON_BIN="${PYTHON:-python3}"

usage() {
  cat <<EOF
Usage: ./run.sh [1|2]
  1  Normal run (reuse venv)
  2  Clean run (wipe caches + recreate venv)
After setup you'll pick:
  1  Streamlit app
  2  LLM service (single prompt)
Env override: PYTHON=python3.12 ./run.sh
EOF
}

prompt_choice_setup() {
  echo "Setup:" >&2
  echo "  1) Normal run" >&2
  echo "  2) Clean run" >&2
  read -rp "Choose (1/2): " choice
  SETUP_CHOICE="${choice:-1}"
}

prompt_choice_run() {
  echo
  echo "Run Target:" >&2
  echo "  1) Streamlit app" >&2
  echo "  2) LLM service (single prompt)" >&2
  read -rp "Choose (1/2): " choice
  TARGET_CHOICE="${choice:-1}"
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
    print("[WARN] streamlit import failed (app launch may fail):", e)
PY
}

launch_streamlit() {
  if [[ ! -f "$APP_FILE" ]]; then
    echo "[ERROR] $APP_FILE not found." >&2
    return 1
  fi
  echo "[INFO] Launching Streamlit app..."
  exec python -m streamlit run "$APP_FILE"
}

llm_single() {
  if [[ ! -f services/llm_service.py ]]; then
    echo "[ERROR] services/llm_service.py not found." >&2
    return 1
  fi
  read -rp "Prompt: " p
  [[ -z "$p" ]] && echo "[INFO] Empty prompt, abort." && return 0
  python services/llm_service.py "$p" || echo "[ERROR] LLM call failed"
}

execute_target() {
  case "$TARGET_CHOICE" in
    1) launch_streamlit ;;
    2) llm_single ;;
    *) echo "[ERROR] Invalid run target '$TARGET_CHOICE'"; exit 2 ;;
  esac
}

main() {
  local arg_choice
  arg_choice="${1:-}" 
  case "$arg_choice" in
    -h|--help) usage; exit 0 ;;
    1|2) SETUP_CHOICE="$arg_choice" ;;
    "") prompt_choice_setup ;;
    *) echo "[ERROR] Invalid first argument (use 1 or 2)"; exit 2 ;;
  esac

  prompt_choice_run

  ensure_python
  case "$SETUP_CHOICE" in
    1) echo "[MODE] Normal run" ;;
    2) echo "[MODE] Clean run"; clean_caches ;;
    *) echo "[ERROR] Invalid setup choice '$SETUP_CHOICE'"; exit 2 ;;
  esac

  activate_venv
  install_deps
  verify_streamlit
  execute_target
}

main "$@"
