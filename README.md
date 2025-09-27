# LINE Group Reminder Bot

โปรเจ็กต์ LINE Bot สำหรับการแจ้งเตือนในกลุ่ม ใช้ Flask และ LINE Messaging API

## คุณสมบัติ

- รับและตอบข้อความผ่าน LINE Messaging API
- Health check endpoint สำหรับตรวจสอบสถานะ
- รองรับการตั้งค่าผ่าน environment variables
- โครงสร้างโค้ดที่เรียบง่ายและขยายได้

## การติดตั้ง

### 1. Clone โปรเจ็กต์

```bash
git clone <repository-url>
cd line-group-reminder-bot
```

### 2. สร้าง Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

### 4. ตั้งค่า Environment Variables

สร้างไฟล์ `.env` ในโฟลเดอร์โปรเจ็กต์:

```env
CHANNEL_ACCESS_TOKEN=your_channel_access_token_here
CHANNEL_SECRET=your_channel_secret_here
PORT=8000
```

**หมายเหตุ:** คุณต้องได้รับค่าเหล่านี้จาก LINE Developers Console

### 5. การตั้งค่า LINE Developers

1. ไปที่ [LINE Developers Console](https://developers.line.biz/)
2. สร้าง Provider ใหม่หรือใช้ที่มีอยู่
3. สร้าง Channel ประเภท "Messaging API"
4. ในส่วน "Basic settings" จะได้ `Channel Secret`
5. ในส่วน "Messaging API" จะได้ `Channel Access Token`
6. ตั้งค่า Webhook URL เป็น: `https://your-domain.com/callback`

## การรันโปรเจ็กต์

### Development Mode

```bash
python app.py
```

เซิร์ฟเวอร์จะรันที่ `http://localhost:8000`

### Production Mode

สำหรับ production แนะนำให้ใช้ WSGI server เช่น Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## Endpoints

### `/healthz` (GET)
- Health check endpoint
- ใช้สำหรับตรวจสอบว่าแอปพลิเคชันทำงานปกติ
- Response: `{"status": "ok", "message": "LINE Bot is running"}`

### `/callback` (POST)
- Webhook endpoint สำหรับรับข้อความจาก LINE
- ต้องตั้งค่าใน LINE Developers Console

### `/run-scheduler` (GET)
- Scheduler endpoint สำหรับรันการแจ้งเตือนตามเวลาที่กำหนด
- จะถูกเรียกโดย cron job service เช่น [cron-job.org](https://cron-job.org)
- Response: `{"status": "success", "message": "scheduler ok", "timestamp": "..."}`

## การพัฒนาเพิ่มเติม

### การเพิ่ม Message Handler

```python
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # ใส่โค้ดจัดการข้อความของคุณที่นี่
    pass
```

### การส่งข้อความ

```python
from linebot.models import TextSendMessage

line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text="ข้อความที่ต้องการส่ง")
)
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Channel Access Token | Required |
| `LINE_CHANNEL_SECRET` | LINE Channel Secret | Required |
| `PORT` | Port สำหรับรันเซิร์ฟเวอร์ | 8000 |

## การทดสอบ

### ทดสอบ Health Check

```bash
curl http://localhost:8000/healthz
```

### ทดสอบ Webhook (ใช้ ngrok สำหรับ local development)

1. ติดตั้ง [ngrok](https://ngrok.com/)
2. รัน: `ngrok http 8000`
3. ใช้ URL ที่ได้จาก ngrok ตั้งค่าใน LINE Developers Console

## โครงสร้างโปรเจ็กต์

```
line-group-reminder-bot/
├── app.py              # ไฟล์หลักของแอปพลิเคชัน (Flask server)
├── handlers.py         # โมดูลจัดการ LINE event handlers
├── scheduler.py        # โมดูลจัดการการแจ้งเตือนตามเวลา
├── storage/            # โมดูลจัดการข้อมูล
│   ├── __init__.py     # Package initializer
│   ├── models.py       # Data classes (Appointment)
│   └── sheets_repo.py  # Google Sheets repository
├── requirements.txt    # Dependencies
├── .env               # Environment variables (ไม่ commit)
├── .env.example       # ตัวอย่าง environment variables
├── .gitignore         # ไฟล์ที่ไม่ต้องการ commit
├── Procfile           # สำหรับ deployment บน Render
├── render.yaml        # Render deployment configuration
└── README.md          # เอกสารนี้
```

## Troubleshooting

### ปัญหาที่พบบ่อย

1. **Invalid signature error**
   - ตรวจสอบ `CHANNEL_SECRET` ให้ถูกต้อง
   - ตรวจสอบ Webhook URL ใน LINE Console

2. **Environment variables not found**
   - ตรวจสอบไฟล์ `.env` และค่าต่าง ๆ
   - ตรวจสอบการใช้ `python-dotenv`

3. **Bot ไม่ตอบกลับ**
   - ตรวจสอบ `CHANNEL_ACCESS_TOKEN`
   - ตรวจสอบ logs ใน console

## การ Deploy บน Render

โปรเจ็กต์นี้พร้อมสำหรับการ deploy บน [Render](https://render.com) แล้ว

### วิธีการ Deploy

#### 1. การ Deploy แบบ Manual

1. สร้างบัญชีที่ [Render.com](https://render.com)
2. เชื่อมต่อ GitHub repository
3. สร้าง Web Service ใหม่
4. เลือก repository นี้
5. ตั้งค่าดังนี้:
   - **Name:** `line-group-reminder-bot`
   - **Runtime:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`

#### 2. การ Deploy แบบ Infrastructure as Code

โปรเจ็กต์มีไฟล์ `render.yaml` ที่กำหนด configuration แล้ว:

```yaml
services:
  - type: web
    name: line-group-reminder-bot
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: LINE_CHANNEL_SECRET
        sync: false
      - key: LINE_CHANNEL_ACCESS_TOKEN  
        sync: false
      - key: PORT
        value: 10000
```

### ตั้งค่า Environment Variables บน Render

ใน Render Dashboard ตั้งค่า Environment Variables ดังนี้:

| Variable Name | Value | Description |
|--------------|-------|-------------|
| `LINE_CHANNEL_SECRET` | `your_channel_secret` | LINE Channel Secret จาก LINE Developers |
| `LINE_CHANNEL_ACCESS_TOKEN` | `your_access_token` | LINE Channel Access Token จาก LINE Developers |
| `PORT` | `10000` | Port สำหรับรันเซิร์ฟเวอร์ (ตั้งอัตโนมัติ) |

### หลังจาก Deploy สำเร็จ

1. **รับ Webhook URL:** หลังจาก deploy สำเร็จ คุณจะได้ URL เช่น:
   ```
   https://line-group-reminder-bot-xxxx.onrender.com
   ```

2. **ตั้งค่าใน LINE Developers Console:**
   - ไปที่ Messaging API settings
   - ตั้งค่า Webhook URL เป็น: `https://your-app-name.onrender.com/callback`
   - เปิดใช้งาน Webhook

3. **ทดสอบการทำงาน:**
   - Health Check: `https://your-app-name.onrender.com/healthz`
   - ทดสอบส่งข้อความผ่าน LINE Bot

### หมายเหตุสำคัญ

- Render Free Plan มีข้อจำกัดเรื่องการ sleep หลังจากไม่ได้ใช้งาน 15 นาที
- สำหรับ production แนะนำให้ใช้ Paid Plan
- ตรวจสอบ logs ใน Render Dashboard หากมีปัญหา

## การตั้งค่า Cron Job

สำหรับการแจ้งเตือนอัตโนมัติ แนะนำให้ใช้ [cron-job.org](https://cron-job.org) เพื่อเรียก endpoint `/run-scheduler` ตามเวลาที่กำหนด

### ขั้นตอนการตั้งค่า cron-job.org:

1. **สมัครสมาชิก** ที่ [cron-job.org](https://cron-job.org)
2. **สร้าง Cron Job ใหม่:**
   - **Title:** LINE Group Reminder
   - **URL:** `https://your-app-name.onrender.com/run-scheduler`
   - **Execution:** ตั้งเวลาตามที่ต้องการ (เช่น ทุก 15 นาที: `*/15 * * * *`)
3. **เปิดใช้งาน** Cron Job

### ตัวอย่างการตั้งค่า Cron Schedule:

| เวลา | Cron Expression | คำอธิบาย |
|------|-----------------|----------|
| ทุก 15 นาที | `*/15 * * * *` | เช็คการแจ้งเตือนทุก 15 นาที |
| ทุกชั่วโมง | `0 * * * *` | เช็คการแจ้งเตือนทุกชั่วโมง |
| ทุกเช้า 9:00 | `0 9 * * *` | เช็คการแจ้งเตือนทุกเช้า 9:00 |
| จ.-ศ. 9:00 | `0 9 * * 1-5` | เช็คการแจ้งเตือนวันทำงาน 9:00 |

### หมายเหตุ:
- Cron job จะเรียก `/run-scheduler` เพื่อตรวจสอบว่ามีการแจ้งเตือนที่ต้องส่งหรือไม่
- ใน version ปัจจุบัน scheduler จะคืน "scheduler ok" ก่อน
- ในอนาคตจะเพิ่มฟีเจอร์การจัดการการแจ้งเตือนจริง

## License

MIT License