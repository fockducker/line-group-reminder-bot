#!/usr/bin/env python3
"""
Test Notification System
ไฟล์สำหรับทดสอบระบบแจ้งเตือนแบบ manual
ส่งการแจ้งเตือนไปยัง personal และ group chat
"""

import os
import sys
import logging
from datetime import datetime, timedelta
import pytz

# เพิ่ม path เพื่อให้ import modules ได้
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from linebot.v3.messaging import MessagingApi, Configuration, ApiClient, PushMessageRequest, TextMessage
from notifications.notification_service import NotificationService
from storage.sheets_repo import SheetsRepository
from storage.models import Appointment

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bangkok timezone
BANGKOK_TZ = pytz.timezone('Asia/Bangkok')

def setup_line_bot():
    """ตั้งค่า LINE Bot API"""
    try:
        channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        if not channel_access_token:
            raise ValueError("LINE_CHANNEL_ACCESS_TOKEN not found in environment variables")
        
        configuration = Configuration(access_token=channel_access_token)
        api_client = ApiClient(configuration)
        line_bot_api = MessagingApi(api_client)
        
        logger.info("LINE Bot API initialized successfully")
        return line_bot_api
        
    except Exception as e:
        logger.error(f"Failed to setup LINE Bot API: {e}")
        return None

def create_test_appointments():
    """สร้างนัดหมายทดสอบ"""
    now = datetime.now(BANGKOK_TZ)
    
    # นัดหมายสำหรับทดสอบ (ใส่ User ID และ Group ID จริงของคุณ)
    test_appointments = [
        {
            'id': 'test001',
            'group_id': 'Uee05f17b8ca24a2927accb9568263892',  # Personal - User ID ของคุณ
            'note': 'ทดสอบแจ้งเตือน Personal Chat',
            'datetime': now + timedelta(days=1),  # พรุ่งนี้
            'hospital': 'โรงพยาบาลทดสอบ Personal',
            'department': 'แผนกทดสอบ Personal',
            'doctor': 'หมอทดสอบ Personal'
        },
        {
            'id': 'test002', 
            'group_id': 'C347ae7c1f88b6c899bd5a3188b8d03b1',  # Group - Group ID ของคุณ
            'note': 'ทดสอบแจ้งเตือน Group Chat',
            'datetime': now,  # วันนี้
            'hospital': 'โรงพยาบาลทดสอบ Group',
            'department': 'แผนกทดสอบ Group',
            'doctor': 'หมอทดสอบ Group'
        }
    ]
    
    appointments = []
    for apt_data in test_appointments:
        appointment = Appointment(
            id=apt_data['id'],
            group_id=apt_data['group_id'],
            datetime_iso=apt_data['datetime'].isoformat(),
            hospital=apt_data['hospital'],
            department=apt_data['department'],
            doctor=apt_data['doctor'],
            note=apt_data['note'],
            location="ห้องทดสอบ 123",
            lead_days=[7, 3, 1],
            notified_flags=[False, False, False],
            created_at=now.isoformat(),
            updated_at=now.isoformat()
        )
        appointments.append(appointment)
    
    logger.info(f"Created {len(appointments)} test appointments")
    return appointments

def test_daily_notifications(notification_service, test_appointments):
    """ทดสอบการส่งแจ้งเตือนรายวัน"""
    logger.info("🧪 Testing daily notifications...")
    
    try:
        current_time = datetime.now(BANGKOK_TZ)
        
        for i, appointment in enumerate(test_appointments, 1):
            logger.info(f"📤 Sending test notification {i}/{len(test_appointments)} for {appointment.note}")
            
            # ส่งการแจ้งเตือนทดสอบ
            notification_service._send_daily_notification(appointment, current_time)
            
            # รอสักครู่ระหว่างการส่ง
            import time
            time.sleep(1)
        
        logger.info("✅ Daily notification test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Daily notification test failed: {e}")
        return False

def test_individual_notifications(line_bot_api, test_appointments):
    """ทดสอบการส่งข้อความแจ้งเตือนแยกรายการ"""
    logger.info("🧪 Testing individual notifications...")
    
    try:
        for i, appointment in enumerate(test_appointments, 1):
            # สร้างข้อความทดสอบ
            context_type = "Personal" if not appointment.group_id.startswith('C') else "Group"
            
            message = f"""🧪 ทดสอบการแจ้งเตือน ({context_type})

📋 การทดสอบระบบแจ้งเตือน #{i}
🏥 {appointment.note}
📅 วันที่: {appointment.appointment_datetime.strftime('%d/%m/%Y %H:%M')}
🏢 สถานที่: {appointment.hospital}
🔖 แผนก: {appointment.department}
👨‍⚕️ แพทย์: {appointment.doctor}
🆔 รหัส: {appointment.id}

✅ หากได้รับข้อความนี้ แสดงว่าระบบแจ้งเตือนทำงานปกติ!

⏰ เวลาทดสอบ: {datetime.now(BANGKOK_TZ).strftime('%d/%m/%Y %H:%M:%S')}"""
            
            # ส่งข้อความ
            line_bot_api.push_message(
                PushMessageRequest(
                    to=appointment.group_id,
                    messages=[TextMessage(text=message)]
                )
            )
            
            logger.info(f"✅ Sent test message {i} to {context_type}: {appointment.group_id}")
            
            # รอสักครู่
            import time
            time.sleep(2)
        
        logger.info("✅ Individual notification test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Individual notification test failed: {e}")
        return False

def test_notification_service_integration(notification_service):
    """ทดสอบการทำงานของ NotificationService โดยรวม"""
    logger.info("🧪 Testing NotificationService integration...")
    
    try:
        # ทดสอบการดึงข้อมูลนัดหมาย
        appointments = notification_service._get_all_appointments()
        logger.info(f"📋 Found {len(appointments)} real appointments in system")
        
        # ถ้ามีนัดหมายจริง ทดสอบส่งแจ้งเตือน
        if appointments:
            # ส่งแจ้งเตือนนัดหมายแรก
            first_appointment = appointments[0]
            logger.info(f"📤 Testing with real appointment: {first_appointment.note}")
            
            current_time = datetime.now(BANGKOK_TZ)
            notification_service._send_daily_notification(first_appointment, current_time)
            
            logger.info("✅ Real appointment notification sent")
        else:
            logger.info("ℹ️ No real appointments found, skipping real data test")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ NotificationService integration test failed: {e}")
        return False

def main():
    """ฟังก์ชันหลักสำหรับทดสอบ"""
    print("🚀 Starting Notification System Test...")
    print("=" * 50)
    
    # ตรวจสอบ environment variables
    required_vars = ['LINE_CHANNEL_ACCESS_TOKEN', 'GOOGLE_CREDENTIALS_JSON', 'GOOGLE_SPREADSHEET_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {missing_vars}")
        print("❌ กรุณาตั้งค่า environment variables ที่จำเป็น")
        return False
    
    # ตั้งค่า LINE Bot
    line_bot_api = setup_line_bot()
    if not line_bot_api:
        print("❌ Failed to setup LINE Bot API")
        return False
    
    # สร้าง NotificationService
    try:
        notification_service = NotificationService(line_bot_api)
        logger.info("✅ NotificationService created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create NotificationService: {e}")
        return False
    
    # สร้างนัดหมายทดสอบ
    test_appointments = create_test_appointments()
    
    print("\n📋 Test Plan:")
    print("1. ทดสอบการส่งข้อความแจ้งเตือนแยกรายการ")
    print("2. ทดสอบระบบแจ้งเตือนรายวัน")
    print("3. ทดสอบกับข้อมูลจริงใน Google Sheets")
    print()
    
    # รอให้ผู้ใช้พร้อม
    input("กด Enter เพื่อเริ่มทดสอบ...")
    
    results = []
    
    # Test 1: Individual notifications
    print("\n🧪 Test 1: Individual Notifications")
    result1 = test_individual_notifications(line_bot_api, test_appointments)
    results.append(("Individual Notifications", result1))
    
    print("\n⏳ รอ 5 วินาที...")
    import time
    time.sleep(5)
    
    # Test 2: Daily notifications
    print("\n🧪 Test 2: Daily Notifications")
    result2 = test_daily_notifications(notification_service, test_appointments)
    results.append(("Daily Notifications", result2))
    
    print("\n⏳ รอ 5 วินาที...")
    time.sleep(5)
    
    # Test 3: Real data integration
    print("\n🧪 Test 3: Real Data Integration")
    result3 = test_notification_service_integration(notification_service)
    results.append(("Real Data Integration", result3))
    
    # สรุปผลการทดสอบ
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 All tests PASSED! Notification system is working correctly!")
    else:
        print("⚠️  Some tests FAILED. Please check the logs above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)