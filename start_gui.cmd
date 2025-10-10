@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Starting Enhanced Parser Tester...
python.exe start_app.py
pause