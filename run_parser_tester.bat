@echo off
echo 🤖 Starting Enhanced Smart Parser Tester...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ first
    pause
    exit /b 1
)

REM Check if required modules are available
echo 📦 Checking required modules...
python -c "import tkinter; print('✅ tkinter OK')" 2>nul
if errorlevel 1 (
    echo ❌ tkinter not available
    echo Please install tkinter: pip install tk
    pause
    exit /b 1
)

python -c "import json, datetime, pathlib; print('✅ Standard modules OK')" 2>nul
if errorlevel 1 (
    echo ❌ Some standard modules missing
    pause
    exit /b 1
)

REM Check if enhanced_smart_parser.py exists
if not exist "utils\enhanced_smart_parser.py" (
    echo ❌ Enhanced Smart Parser not found at utils\enhanced_smart_parser.py
    echo Please make sure the file exists
    pause
    exit /b 1
)

echo ✅ All checks passed!
echo.
echo 🚀 Launching Parser Tester App...
echo.

REM Run the app
python parser_tester_app.py

REM Check exit code
if errorlevel 1 (
    echo.
    echo ❌ App exited with error
    pause
) else (
    echo.
    echo ✅ App closed successfully
)

pause