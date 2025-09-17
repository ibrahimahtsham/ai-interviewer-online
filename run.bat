@echo off
REM Bootstrap script for AI Interviewer Online (Windows)
REM - Ensures Python 3 present
REM - Creates virtual environment if missing
REM - Installs/updates dependencies
REM - Launches Streamlit app

setlocal enabledelayedexpansion

where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python not found in PATH. Install Python 3 and retry.
  exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python -V') do set PYVER=%%v
if not defined PYVER (
  echo [ERROR] Could not determine Python version.
  exit /b 1
)

echo [INFO] Using Python %PYVER%

if not exist .venv (
  echo [INFO] Creating virtual environment (.venv)...
  python -m venv .venv
  if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    exit /b 1
  )
)

call .venv\Scripts\activate.bat
if errorlevel 1 (
  echo [ERROR] Failed to activate virtual environment.
  exit /b 1
)

echo [INFO] Upgrading pip...
python -m pip install --upgrade pip >nul
if errorlevel 1 (
  echo [ERROR] pip upgrade failed.
  exit /b 1
)

if exist requirements.txt (
  echo [INFO] Installing dependencies...
  pip install -r requirements.txt
  if errorlevel 1 (
    echo [ERROR] Dependency installation failed.
    exit /b 1
  )
) else (
  echo [WARN] requirements.txt not found; continuing...
)

echo [INFO] Launching Streamlit app...
streamlit run app.py
