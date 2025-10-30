@echo off
REM Chair Flying Launcher for Windows
REM This batch file makes it easy to run the Chair Flying application on Windows

echo ============================================================
echo Chair Flying - Aviation Training Practice
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.7 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

REM Check Python version
python -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.7 or higher is required
    echo.
    echo Your current Python version:
    python --version
    echo.
    echo Please upgrade Python from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check if config.json exists
if not exist "config.json" (
    echo ERROR: config.json not found
    echo.
    echo Please create config.json in the same folder as this script.
    echo See README.md for instructions.
    echo.
    pause
    exit /b 1
)

REM Check if maneuvers file exists
for /f "tokens=2 delims=:, " %%a in ('python -c "import json; print(json.load(open('config.json'))['maneuvers_file'])" 2^>nul') do set MANEUVERS_FILE=%%a
if not exist "%MANEUVERS_FILE%" (
    echo ERROR: Maneuvers file not found
    echo.
    echo Please create the maneuvers file specified in config.json.
    echo See README.md for instructions.
    echo.
    pause
    exit /b 1
)

REM Run the application
echo Starting Chair Flying...
echo.
python chair_flying.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo.
    echo An error occurred. Press any key to close this window.
    pause >nul
)
