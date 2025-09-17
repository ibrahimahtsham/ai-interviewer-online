@echo off
REM AI Interviewer Online run script (Windows)
REM Options:
REM   1) Normal run
REM   2) Clean run (remove caches before start)

setlocal enabledelayedexpansion
set "APP_FILE=app.py"

if "%~1"=="" (
  echo Run options:
  echo   1^) Normal run
  echo   2^) Clean run (remove caches)
  set /p CHOICE=Enter choice (1/2^) : 
) else (
  set "CHOICE=%~1"
)
if "%CHOICE%"=="" set "CHOICE=1"

where python >nul 2>nul || (echo [ERROR] Python not found in PATH. Install Python 3 and retry.& exit /b 1)

for /f "tokens=2 delims= " %%v in ('python -V') do set PYVER=%%v
if not defined PYVER (echo [ERROR] Could not determine Python version.& exit /b 1)
echo [INFO] Using Python %PYVER%

if "%CHOICE%"=="2" (
  echo [MODE] Clean run
  echo [INFO] Cleaning caches...
  for /d /r %%d in (__pycache__) do rd /s /q "%%d" 2>nul
  for /r %%f in (*.pyc *.pyo) do del /q "%%f" 2>nul
  if exist .streamlit\cache rd /s /q .streamlit\cache 2>nul
  if exist .pytest_cache rd /s /q .pytest_cache 2>nul
  if exist .mypy_cache rd /s /q .mypy_cache 2>nul
  if exist .ruff_cache rd /s /q .ruff_cache 2>nul
  if exist .venv (
    echo [INFO] Removing virtual environment (.venv)...
    rd /s /q .venv
  )
  echo [INFO] Cache cleanup complete.
) else if not "%CHOICE%"=="1" (
  echo [ERROR] Invalid option %CHOICE% (use 1 or 2)
  exit /b 2
) else (
  echo [MODE] Normal run
)

if not exist .venv (
  echo [INFO] Creating virtual environment (.venv)...
  python -m venv .venv || (echo [ERROR] Failed to create virtual environment.& exit /b 1)
)

call .venv\Scripts\activate.bat || (echo [ERROR] Failed to activate virtual environment.& exit /b 1)
echo [INFO] Active interpreter:
python -c "import sys;print(sys.executable)"

if exist requirements.txt (
  echo [INFO] Upgrading pip...
  python -m pip install --upgrade pip >nul
  echo [INFO] Installing dependencies...
  python -m pip install -r requirements.txt || (echo [ERROR] Dependency installation failed.& exit /b 1)
) else (
  echo [WARN] requirements.txt not found; continuing...
)

python -c "import streamlit,os;print(f'[OK] streamlit {streamlit.__version__} ({os.path.dirname(streamlit.__file__)})')" || (echo [ERROR] streamlit import failed.& exit /b 1)

if not exist "%APP_FILE%" (echo [ERROR] %APP_FILE% not found.& exit /b 1)

echo [INFO] Launching app...
python -m streamlit run "%APP_FILE%"
