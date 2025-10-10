@echo off
title Enhanced Parser Tester
echo ================================
echo  Enhanced Smart Parser Tester
echo ================================
echo.
echo Starting GUI application...
echo.

REM Set UTF-8 encoding
chcp 65001 >nul

REM Check if Python exists
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python not found
    echo Please install Python first
    pause
    exit /b 1
)

REM Run the app
python simple_gui.py

REM Keep window open if there's an error
if %errorlevel% neq 0 (
    echo.
    echo App exited with error code: %errorlevel%
    pause
)