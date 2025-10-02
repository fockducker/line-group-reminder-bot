# UptimeRobot Setup Guide
# วิธีตั้งค่า UptimeRobot เพื่อป้องกัน Render หลับ (ฟรี)

## ขั้นตอน:

### 1. สมัคร UptimeRobot
- ไปที่: https://uptimerobot.com
- สมัครบัญชีฟรี (ใช้ได้ 50 monitors)

### 2. สร้าง Monitor
- กด "Add New Monitor"
- Monitor Type: **HTTP(s)**
- Friendly Name: **LINE Bot Keep-Alive**
- URL: **https://line-group-reminder-bot.onrender.com/health**
- Monitoring Interval: **5 minutes** (ฟรีได้แค่ 5 นาที)

### 3. ตั้งค่า Alert (ถ้าต้องการ)
- Alert Contacts: Email ของคุณ
- จะแจ้งเตือนถ้าบอทล่ม

### 4. Save และรอ
- UptimeRobot จะ ping ทุก 5 นาที
- Render จะไม่หลับเพราะมี traffic ต่อเนื่อง

## ข้อดี:
✅ ฟรี 100%
✅ ไม่ต้องพึ่ง GitHub Actions
✅ Monitoring + Keep-alive ในตัวเดียว
✅ Email alert ถ้าบอทล่ม
✅ Dashboard สวย

## ข้อเสีย:
❌ ต่ำสุด 5 นาที (GitHub Actions ได้ 1 นาที)

## Alternative URLs to monitor:
- https://line-group-reminder-bot.onrender.com/health
- https://line-group-reminder-bot.onrender.com/healthz

## Tips:
- ใช้ /health เพราะ response รวดเร็ว
- ตั้ง timeout 30 seconds
- เปิด notifications ถ้าต้องการรู้สถานะ