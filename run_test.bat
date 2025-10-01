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

REM ตรวจสอบว่า environment variables พร้อมหรือไม่
echo.
echo ตรวจสอบ environment variables...
if "%LINE_CHANNEL_ACCESS_TOKEN%"=="" (
    echo ❌ LINE_CHANNEL_ACCESS_TOKEN ไม่ได้ตั้งค่า
    echo กรุณาตั้งค่า environment variables ก่อน
    pause
    exit /b 1
)

if "%GOOGLE_CREDENTIALS_JSON%"=="" (
    echo ❌ GOOGLE_CREDENTIALS_JSON ไม่ได้ตั้งค่า
    echo กรุณาตั้งค่า environment variables ก่อน
    pause
    exit /b 1
)

if "%GOOGLE_SPREADSHEET_ID%"=="" (
    echo ❌ GOOGLE_SPREADSHEET_ID ไม่ได้ตั้งค่า
    echo กรุณาตั้งค่า environment variables ก่อน
    pause
    exit /b 1
)

echo ✅ Environment variables พร้อมแล้ว
echo.

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