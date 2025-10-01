# PowerShell Script สำหรับตั้งค่า Environment Variables
# LINE Group Reminder Bot

Write-Host "🔧 ตั้งค่า Environment Variables สำหรับ LINE Bot" -ForegroundColor Green
Write-Host "=" * 50

# ตรวจสอบว่ามีไฟล์ .env หรือไม่
$envFile = Join-Path $PSScriptRoot ".env"
if (Test-Path $envFile) {
    Write-Host "📄 พบไฟล์ .env กำลังโหลด..." -ForegroundColor Yellow
    
    # อ่านไฟล์ .env และตั้งค่า environment variables
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^([^#][^=]*)=(.*)$") {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            
            # ลบ quotes ถ้ามี
            if ($value -match '^"(.*)"$') {
                $value = $matches[1]
            }
            
            [Environment]::SetEnvironmentVariable($name, $value, [EnvironmentVariableTarget]::Process)
            Write-Host "✅ ตั้งค่า $name" -ForegroundColor Green
        }
    }
} else {
    Write-Host "❌ ไม่พบไฟล์ .env" -ForegroundColor Red
    Write-Host "กรุณาคัดลอก .env.example เป็น .env และใส่ค่าจริง" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "หรือตั้งค่าด้วยตนเอง:" -ForegroundColor Yellow
    Write-Host '$env:LINE_CHANNEL_ACCESS_TOKEN="your_token"' -ForegroundColor Cyan
    Write-Host '$env:GOOGLE_CREDENTIALS_JSON="your_json"' -ForegroundColor Cyan
    Write-Host '$env:GOOGLE_SPREADSHEET_ID="your_id"' -ForegroundColor Cyan
    
    # ให้ผู้ใช้ตั้งค่าเอง
    Write-Host ""
    $token = Read-Host "กรุณาใส่ LINE_CHANNEL_ACCESS_TOKEN"
    if ($token) {
        $env:LINE_CHANNEL_ACCESS_TOKEN = $token
        Write-Host "✅ ตั้งค่า LINE_CHANNEL_ACCESS_TOKEN" -ForegroundColor Green
    }
    
    $credentials = Read-Host "กรุณาใส่ GOOGLE_CREDENTIALS_JSON (JSON string)"
    if ($credentials) {
        $env:GOOGLE_CREDENTIALS_JSON = $credentials
        Write-Host "✅ ตั้งค่า GOOGLE_CREDENTIALS_JSON" -ForegroundColor Green
    }
    
    $spreadsheetId = Read-Host "กรุณาใส่ GOOGLE_SPREADSHEET_ID"
    if ($spreadsheetId) {
        $env:GOOGLE_SPREADSHEET_ID = $spreadsheetId
        Write-Host "✅ ตั้งค่า GOOGLE_SPREADSHEET_ID" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "🔍 ตรวจสอบ Environment Variables:" -ForegroundColor Yellow

$requiredVars = @(
    "LINE_CHANNEL_ACCESS_TOKEN",
    "GOOGLE_CREDENTIALS_JSON", 
    "GOOGLE_SPREADSHEET_ID"
)

$allSet = $true
foreach ($var in $requiredVars) {
    $value = [Environment]::GetEnvironmentVariable($var, [EnvironmentVariableTarget]::Process)
    if ($value) {
        $displayValue = if ($value.Length -gt 20) { $value.Substring(0, 20) + "..." } else { $value }
        Write-Host "✅ $var = $displayValue" -ForegroundColor Green
    } else {
        Write-Host "❌ $var = ไม่พบ" -ForegroundColor Red
        $allSet = $false
    }
}

Write-Host ""
if ($allSet) {
    Write-Host "🎉 Environment Variables ตั้งค่าครบถ้วนแล้ว!" -ForegroundColor Green
    Write-Host "สามารถรัน python quick_test.py ได้เลย" -ForegroundColor Green
} else {
    Write-Host "⚠️  Environment Variables ยังไม่ครบ" -ForegroundColor Yellow
    Write-Host "กรุณาตั้งค่าให้ครบก่อนรันการทดสอบ" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" * 50