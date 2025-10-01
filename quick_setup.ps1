# Quick Setup and Test Script
# รันสคริปต์นี้เพื่อตั้งค่าและทดสอบในคำสั่งเดียว

Write-Host "🚀 LINE Bot Quick Test Setup" -ForegroundColor Green
Write-Host "=" * 40

# เข้าไปใน directory ที่ถูกต้อง
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# เปิดใช้งาน virtual environment
Write-Host "🔧 เปิดใช้งาน virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# ตั้งค่า environment variables
Write-Host "⚙️  ตั้งค่า environment variables..." -ForegroundColor Yellow
& ".\setup_env.ps1"

# ถามว่าจะรันการทดสอบไหม
Write-Host ""
$runTest = Read-Host "รันการทดสอบเลยไหม? (y/n)"
if ($runTest -eq "y" -or $runTest -eq "Y" -or $runTest -eq "") {
    Write-Host ""
    Write-Host "🧪 เริ่มการทดสอบ..." -ForegroundColor Green
    python quick_test.py
} else {
    Write-Host ""
    Write-Host "✅ Setup เสร็จแล้ว! รันคำสั่ง 'python quick_test.py' เพื่อทดสอบ" -ForegroundColor Green
}

Write-Host ""
Write-Host "=" * 40
Read-Host "กด Enter เพื่อปิด"