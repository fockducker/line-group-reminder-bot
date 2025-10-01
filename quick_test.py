#!/usr/bin/env python3
"""
Quick Test Script for Notification System
ไฟล์สำหรับทดสอบเร็ว ๆ ส่งแจ้งเตือนไปที่ Personal และ Group
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# โหลด environment variables จากไฟล์ .env ถ้ามี
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ โหลด .env file สำเร็จ")
except ImportError:
    print("ℹ️  python-dotenv ไม่พบ จะใช้ environment variables ของระบบ")

from linebot.v3.messaging import MessagingApi, Configuration, ApiClient, PushMessageRequest, TextMessage
from datetime import datetime
import pytz

def check_environment():
    """ตรวจสอบ environment variables"""
    required_vars = {
        'LINE_CHANNEL_ACCESS_TOKEN': 'LINE Channel Access Token',
        'GOOGLE_CREDENTIALS_JSON': 'Google Credentials JSON',
        'GOOGLE_SPREADSHEET_ID': 'Google Spreadsheet ID'
    }
    
    print("🔍 ตรวจสอบ Environment Variables...")
    print("-" * 40)
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # แสดงเฉพาะส่วนเริ่มต้นเพื่อความปลอดภัย
            display_value = value[:20] + "..." if len(value) > 20 else value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: ไม่พบ")
            missing_vars.append(var)
    
    print("-" * 40)
    
    if missing_vars:
        print(f"❌ ขาด environment variables: {', '.join(missing_vars)}")
        print("\n💡 วิธีแก้ไข:")
        print("1. ตรวจสอบไฟล์ .env ในโฟลเดอร์โปรเจค")
        print("2. หรือตั้งค่าใน PowerShell:")
        for var in missing_vars:
            print(f"   $env:{var}=\"your_value_here\"")
        return False
    
    return True

def quick_test():
    """ทดสอบเร็ว ๆ ส่งข้อความไปทั้ง Personal และ Group"""
    
    print("🧪 เริ่มต้นการทดสอบระบบแจ้งเตือน")
    print("=" * 50)
    
    # ตรวจสอบ environment variables ก่อน
    if not check_environment():
        return False
    
    # ตั้งค่า LINE Bot
    channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    if not channel_access_token:
        print("❌ กรุณาตั้งค่า LINE_CHANNEL_ACCESS_TOKEN")
        return False
    
    configuration = Configuration(access_token=channel_access_token)
    api_client = ApiClient(configuration)
    line_bot_api = MessagingApi(api_client)
    
    # ID ของคุณ (แก้ไขตามของจริง)
    personal_id = "Uee05f17b8ca24a2927accb9568263892"  # User ID
    group_id = "C347ae7c1f88b6c899bd5a3188b8d03b1"     # Group ID
    
    bangkok_tz = pytz.timezone('Asia/Bangkok')
    current_time = datetime.now(bangkok_tz)
    
    # ข้อความทดสอบ
    test_messages = [
        {
            'to': personal_id,
            'type': 'Personal Chat',
            'message': f"""🧪 ทดสอบระบบแจ้งเตือน (Personal)

✅ หากได้รับข้อความนี้ แสดงว่าระบบแจ้งเตือนสำหรับ Personal Chat ทำงานปกติ!

📋 รายละเอียดการทดสอบ:
• ประเภท: Personal Chat
• User ID: {personal_id}
• เวลาทดสอบ: {current_time.strftime('%d/%m/%Y %H:%M:%S')}

🔔 ระบบจะส่งแจ้งเตือนทุกวันเวลา 09:00 น."""
        },
        {
            'to': group_id,
            'type': 'Group Chat',
            'message': f"""🧪 ทดสอบระบบแจ้งเตือน (Group)

✅ หากได้รับข้อความนี้ แสดงว่าระบบแจ้งเตือนสำหรับ Group Chat ทำงานปกติ!

📋 รายละเอียดการทดสอบ:
• ประเภท: Group Chat  
• Group ID: {group_id}
• เวลาทดสอบ: {current_time.strftime('%d/%m/%Y %H:%M:%S')}

🔔 ระบบจะส่งแจ้งเตือนทุกวันเวลา 09:00 น."""
        }
    ]
    
    print("🚀 เริ่มทดสอบการส่งข้อความ...")
    print("=" * 50)
    
    # ส่งข้อความ
    for i, msg_data in enumerate(test_messages, 1):
        try:
            print(f"📤 ส่งข้อความ {i}/2 ไปยัง {msg_data['type']}")
            
            line_bot_api.push_message(
                PushMessageRequest(
                    to=msg_data['to'],
                    messages=[TextMessage(text=msg_data['message'])]
                )
            )
            
            print(f"✅ ส่งสำเร็จ: {msg_data['type']}")
            
            # รอสักครู่
            import time
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ ส่งไม่สำเร็จ {msg_data['type']}: {e}")
            return False
    
    print("=" * 50)
    print("🎉 ทดสอบเสร็จสิ้น!")
    print()
    print("📱 กรุณาตรวจสอบข้อความใน LINE:")
    print("  • Personal Chat: ข้อความทดสอบส่วนตัว")
    print("  • Group Chat: ข้อความทดสอบกลุ่ม")
    print()
    print("✅ หากได้รับข้อความทั้งสอง แสดงว่าระบบแจ้งเตือนทำงานปกติ!")
    
    return True

if __name__ == "__main__":
    try:
        success = quick_test()
        if success:
            print("\n🔔 ระบบแจ้งเตือนพร้อมใช้งาน!")
            print("   จะส่งแจ้งเตือนอัตโนมัติทุกวันเวลา 09:00 น.")
        else:
            print("\n❌ การทดสอบล้มเหลว กรุณาตรวจสอบการตั้งค่า")
    except KeyboardInterrupt:
        print("\n⏹️  การทดสอบถูกยกเลิก")
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")