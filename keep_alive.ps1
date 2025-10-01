# Keep-Alive PowerShell Script
# รันใน PowerShell ทุก 10-14 นาที หรือตั้งใน Task Scheduler

param(
    [string]$ServiceUrl = "https://line-group-reminder-bot.onrender.com",
    [int]$IntervalMinutes = 14,
    [switch]$RunOnce = $false
)

function Ping-Service {
    param([string]$Url, [string]$EndpointName)
    
    try {
        $response = Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec 30
        Write-Host "✅ $EndpointName ping: SUCCESS" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ $EndpointName ping: FAILED - $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Send-KeepAlive {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "🏃 [$timestamp] Starting keep-alive ping..." -ForegroundColor Yellow
    
    # Ping health endpoint
    $healthSuccess = Ping-Service -Url "$ServiceUrl/health" -EndpointName "Health"
    
    # รอ 5 วินาที
    Start-Sleep -Seconds 5
    
    # Ping root endpoint เป็น backup
    $rootSuccess = Ping-Service -Url "$ServiceUrl/" -EndpointName "Root"
    
    $status = if ($healthSuccess -or $rootSuccess) { "✅ SUCCESS" } else { "❌ FAILED" }
    Write-Host "📊 [$timestamp] Keep-alive result: $status" -ForegroundColor $(if ($healthSuccess -or $rootSuccess) { "Green" } else { "Red" })
    
    if (-not $RunOnce) {
        $nextPing = (Get-Date).AddMinutes($IntervalMinutes).ToString("yyyy-MM-dd HH:mm:ss")
        Write-Host "⏰ Next ping scheduled: $nextPing" -ForegroundColor Cyan
    }
    
    Write-Host ""
}

# Main execution
if ($RunOnce) {
    # รันครั้งเดียว
    Send-KeepAlive
} else {
    # รันแบบ loop
    Write-Host "🤖 Keep-Alive Service Started" -ForegroundColor Green
    Write-Host "🎯 Target: $ServiceUrl" -ForegroundColor Yellow
    Write-Host "⏱️  Interval: $IntervalMinutes minutes" -ForegroundColor Yellow
    Write-Host "🛑 Press Ctrl+C to stop" -ForegroundColor Red
    Write-Host "=" * 50
    
    while ($true) {
        Send-KeepAlive
        Start-Sleep -Seconds ($IntervalMinutes * 60)
    }
}

<# 
วิธีใช้:

1. รันครั้งเดียว:
   .\keep_alive.ps1 -RunOnce

2. รันแบบ loop (ทุก 14 นาที):
   .\keep_alive.ps1

3. รันแบบ loop ทุก 10 นาที:
   .\keep_alive.ps1 -IntervalMinutes 10

4. ตั้งใน Task Scheduler:
   Program: powershell.exe
   Arguments: -ExecutionPolicy Bypass -File "C:\path\to\keep_alive.ps1" -RunOnce
   Trigger: Repeat every 14 minutes
#>