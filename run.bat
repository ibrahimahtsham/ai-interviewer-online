@echo off
REM AI Interviewer Online run script (Windows)
REM Two-step: collect both choices first, then execute.

setlocal enabledelayedexpansion
set "APP_FILE=app.py"

REM First menu (setup) unless argument supplied
if "%~1"=="" (
  echo Setup:
  echo   1^) Normal run
  echo   2^) Clean run
  set /p SETUP_CHOICE=Choose (1/2^): 
) else (
  set "SETUP_CHOICE=%~1"
)
if "%SETUP_CHOICE%"=="" set "SETUP_CHOICE=1"

REM Second menu (run target)
echo.
echo Run Target:
echo   1^) Streamlit app
echo   2^) LLM service (single prompt)
set /p TARGET_CHOICE=Choose (1/2^): 
if "%TARGET_CHOICE%"=="" set "TARGET_CHOICE=1"

where python >nul 2>nul || (echo [ERROR] Python not found in PATH.& exit /b 1)
for /f "tokens=2 delims= " %%v in ('python -V') do set PYVER=%%v
if not defined PYVER (echo [ERROR] Could not determine Python version.& exit /b 1)
echo [INFO] Using Python %PYVER%

if "%SETUP_CHOICE%"=="2" (
  echo [MODE] Clean run
  echo [INFO] Cleaning caches...
  for /d /r %%d in (__pycache__) do rd /s /q "%%d" 2>nul
  for /r %%f in (*.pyc *.pyo) do del /q "%%f" 2>nul
  if exist .streamlit\cache rd /s /q .streamlit\cache 2>nul
  if exist .pytest_cache rd /s /q .pytest_cache 2>nul
  if exist .mypy_cache rd /s /q .mypy_cache 2>nul
  if exist .ruff_cache rd /s /q .ruff_cache 2>nul
) else if not "%SETUP_CHOICE%"=="1" (
  echo [ERROR] Invalid setup choice %SETUP_CHOICE% (use 1 or 2)
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

REM Execute target
if "%TARGET_CHOICE%"=="1" goto launch_app
if "%TARGET_CHOICE%"=="2" goto llm_single
echo [ERROR] Invalid run target.& exit /b 2

:launch_app
if not exist "%APP_FILE%" (echo [ERROR] %APP_FILE% not found.& exit /b 1)
echo [INFO] Launching Streamlit app...
python -m streamlit run "%APP_FILE%"
goto :eof

:llm_single
if not exist services\llm_service.py (echo [ERROR] services\llm_service.py not found.& exit /b 1)
set /p LLM_PROMPT=Prompt: 
if "%LLM_PROMPT%"=="" (echo [INFO] Empty prompt.& exit /b 0)
python services\llm_service.py "%LLM_PROMPT%"
goto :eof
