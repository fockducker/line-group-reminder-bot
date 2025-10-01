#!/usr/bin/env python3
"""
Keep-Alive Script for Render Service
รันสคริปต์นี้เพื่อป้องกัน Render Free Tier หลับ
"""

import time
import requests
import schedule
from datetime import datetime
import logging

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('keep_alive.log'),
        logging.StreamHandler()
    ]
)

SERVICE_URL = "https://line-group-reminder-bot.onrender.com"
PING_INTERVAL_MINUTES = 14

def ping_service():
    """ส่ง ping ไปยัง service เพื่อป้องกันการหลับ"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    endpoints = [
        f"{SERVICE_URL}/health",
        f"{SERVICE_URL}/"
    ]
    
    success_count = 0
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=30)
            if response.status_code == 200:
                logging.info(f"✅ Ping successful: {endpoint}")
                success_count += 1
            else:
                logging.warning(f"⚠️  Ping returned {response.status_code}: {endpoint}")
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Ping failed: {endpoint} - {str(e)}")
        
        # รอระหว่าง endpoint
        time.sleep(5)
    
    status = "SUCCESS" if success_count > 0 else "FAILED"
    logging.info(f"📊 Keep-alive result: {status} ({success_count}/{len(endpoints)} endpoints)")
    
    return success_count > 0

def run_keep_alive_service():
    """รันบริการ keep-alive แบบต่อเนื่อง"""
    logging.info("🤖 Keep-Alive Service Started")
    logging.info(f"🎯 Target: {SERVICE_URL}")
    logging.info(f"⏱️  Interval: {PING_INTERVAL_MINUTES} minutes")
    logging.info("🛑 Press Ctrl+C to stop")
    logging.info("=" * 50)
    
    # ตั้งค่า schedule
    schedule.every(PING_INTERVAL_MINUTES).minutes.do(ping_service)
    
    # รันครั้งแรกทันที
    ping_service()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # เช็คทุกนาที
    except KeyboardInterrupt:
        logging.info("🛑 Keep-alive service stopped by user")

def run_once():
    """รันครั้งเดียว"""
    logging.info("🏃 Running one-time keep-alive ping...")
    result = ping_service()
    return result

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # รันครั้งเดียว
        success = run_once()
        sys.exit(0 if success else 1)
    else:
        # รันแบบ service
        run_keep_alive_service()

"""
วิธีใช้:

1. รันครั้งเดียว:
   python keep_alive_service.py --once

2. รันแบบ service (รันต่อเนื่อง):
   python keep_alive_service.py

3. ตั้งใน cron (Linux/Mac):
   */14 * * * * /usr/bin/python3 /path/to/keep_alive_service.py --once

4. ตั้งใน Task Scheduler (Windows):
   Program: python.exe
   Arguments: C:\path\to\keep_alive_service.py --once
   Trigger: Repeat every 14 minutes

Dependencies:
   pip install requests schedule
"""