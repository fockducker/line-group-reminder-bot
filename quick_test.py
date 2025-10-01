#!/usr/bin/env python3
"""
Quick Test Script for Notification System
ไฟล์สำหรับทดสอบเร็ว ๆ ส่งแจ้งเตือนไปที่ Personal และ Group
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from linebot.v3.messaging import MessagingApi, Configuration, ApiClient, PushMessageRequest, TextMessage
from datetime import datetime
import pytz

def quick_test():
    """ทดสอบเร็ว ๆ ส่งข้อความไปทั้ง Personal และ Group"""
    
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