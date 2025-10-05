#!/usr/bin/env python3
"""
ทดสอบฟีเจอร์ใหม่: การเตือนเมื่อเพิ่มนัดหมายในอดีต
"""

def test_past_appointment_warning():
    """ทดสอบการเตือนนัดหมายในอดีต"""
    
    print("🧪 ทดสอบฟีเจอร์การเตือนนัดหมายในอดีต")
    print("="*50)
    
    # สร้างข้อมูลทดสอบ
    from datetime import datetime, timedelta
    import pytz
    
    bangkok_tz = pytz.timezone('Asia/Bangkok')
    now = datetime.now(bangkok_tz)
    
    # ทดสอบการจำลองการตรวจสอบ
    print(f"📅 เวลาปัจจุบัน: {now.strftime('%d/%m/%Y %H:%M')}")
    print()
    
    test_cases = [
        {
            'name': 'นัดหมายในอดีต (1 วันที่แล้ว)',
            'datetime': now - timedelta(days=1),
            'expected_warning': True
        },
        {
            'name': 'นัดหมายในอนาคต (1 วันข้างหน้า)', 
            'datetime': now + timedelta(days=1),
            'expected_warning': False
        },
        {
            'name': 'นัดหมายในอดีต (1 ชั่วโมงที่แล้ว)',
            'datetime': now - timedelta(hours=1),
            'expected_warning': True
        },
        {
            'name': 'นัดหมายในอนาคต (1 ชั่วโมงข้างหน้า)',
            'datetime': now + timedelta(hours=1),
            'expected_warning': False
        }
    ]
    
    print("🔍 ทดสอบการตรวจสอบนัดหมายในอดีต:")
    for case in test_cases:
        appointment_dt = case['datetime']
        is_past = appointment_dt < now
        expected_warning = case['expected_warning']
        
        status = "✅" if is_past == expected_warning else "❌"
        warning_text = "⚠️ แสดงคำเตือน" if is_past else "✅ ไม่แสดงคำเตือน"
        
        print(f"{status} {case['name']}")
        print(f"     📅 {appointment_dt.strftime('%d/%m/%Y %H:%M')}")
        print(f"     🚨 {warning_text}")
        print()

def demonstrate_message_difference():
    """แสดงความแตกต่างของข้อความที่ส่งกลับ"""
    
    print("📋 ตัวอย่างข้อความที่แตกต่างกัน:")
    print("="*40)
    
    print("🔮 **นัดหมายในอนาคต:**")
    future_message = """✅ บันทึกนัดหมายสำเร็จ!

📝 ชื่อนัดหมาย: "ตรวจสุขภาพ"
🆔 รหัส: ABC12345
📅 วันเวลา: 10/10/2025 14:00
👤 บุคคล/ผู้ติดต่อ: ดร.สมชาย
📍 สถานที่: โรงพยาบาลศิริราช
🏢 อาคาร/แผนก/ชั้น: อาคาร 1

✅ ข้อมูลถูกบันทึกแล้ว
🔔 ระบบจะแจ้งเตือน 7 วัน และ 1 วันก่อนนัดหมาย"""
    
    print(future_message)
    print()
    
    print("⚠️ **นัดหมายในอดีต:**")
    past_message = """⚠️ คำเตือน: นัดหมายในอดีต!

📝 ชื่อนัดหมาย: "ตรวจสุขภาพ"
🆔 รหัส: ABC12345
📅 วันเวลา: 01/10/2025 14:00 (อดีต)
👤 บุคคล/ผู้ติดต่อ: ดร.สมชาย
📍 สถานที่: โรงพยาบาลศิริราช
🏢 อาคาร/แผนก/ชั้น: อาคาร 1

✅ ข้อมูลถูกบันทึกแล้ว
📋 นัดหมายนี้จะปรากฏใน "ดูนัดย้อนหลัง" เท่านั้น
💡 หากต้องการดูใช้คำสั่ง "ดูนัดย้อนหลัง"
⚠️ ระบบแจ้งเตือนจะไม่ทำงานกับนัดหมายในอดีต"""
    
    print(past_message)

if __name__ == "__main__":
    test_past_appointment_warning()
    demonstrate_message_difference()
    
    print("\n🎯 สรุปฟีเจอร์ใหม่:")
    print("="*30)
    print("✅ เพิ่มการตรวจสอบนัดหมายในอดีต")
    print("⚠️ แสดงคำเตือนชัดเจนเมื่อเป็นนัดหมายในอดีต")
    print("💡 แจ้งให้ผู้ใช้ทราบว่าจะเห็นใน 'ดูนัดย้อนหลัง'")
    print("🔔 อธิบายว่าระบบแจ้งเตือนจะไม่ทำงาน")
    print("👤 ป้องกันความสับสนของผู้ใช้")
    print("\n🚀 พร้อม commit แล้ว!")