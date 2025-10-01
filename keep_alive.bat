@echo off
REM Keep-Alive Script สำหรับ Windows Task Scheduler
REM รันไฟล์นี้ใน Task Scheduler ทุก 10-14 นาที

echo [%date% %time%] Starting keep-alive ping...

REM Ping health endpoint
curl -f "https://line-group-reminder-bot.onrender.com/health" > nul 2>&1
if %errorlevel% == 0 (
    echo [%date% %time%] Health check: SUCCESS
) else (
    echo [%date% %time%] Health check: FAILED
)

REM รอ 5 วินาที
timeout /t 5 /nobreak > nul

REM Ping root endpoint เป็น backup
curl -f "https://line-group-reminder-bot.onrender.com/" > nul 2>&1
if %errorlevel% == 0 (
    echo [%date% %time%] Root ping: SUCCESS
) else (
    echo [%date% %time%] Root ping: FAILED
)

echo [%date% %time%] Keep-alive completed
echo.

REM ถ้าต้องการ log ให้เพิ่ม >> "C:\path\to\logfile.txt"