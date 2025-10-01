@echo off
echo ========================================
echo    LINE Bot Notification System Test
echo ========================================
echo.

REM เข้าไปใน directory ที่ถูกต้อง
cd /d "C:\Users\fermi\line-group-reminder-bot"

REM เปิดใช้งาน virtual environment
echo เปิดใช้งาน virtual environment...
call venv\Scripts\activate.bat

REM ตั้งค่า environment variables ด้วย PowerShell
echo.
echo ตั้งค่า environment variables...
powershell -ExecutionPolicy Bypass -File "setup_env.ps1"

echo.
echo ========================================

REM รันการทดสอบ
echo เริ่มทดสอบระบบแจ้งเตือน...
echo ========================================
python test_notifications.py

REM แสดงผลลัพธ์
echo.
echo ========================================
echo การทดสอบเสร็จสิ้น
echo ========================================
echo กรุณาตรวจสอบข้อความใน LINE Chat
echo - Personal Chat: ข้อความทดสอบส่วนตัว
echo - Group Chat: ข้อความทดสอบกลุ่ม
echo.

pause