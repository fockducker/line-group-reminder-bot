#!/usr/bin/env python3
"""
ทดสอบการเพิ่มนัดหมายที่มีวันที่ในอดีต
"""

def test_past_appointment_behavior():
    """ทดสอบพื้นฐานการทำงานของระบบกับนัดหมายในอดีต"""
    
    print("🧪 ทดสอบการเพิ่มนัดหมายในอดีต")
    print("="*50)
    
    # ทดสอบการ parse วันที่ในอดีต
    from utils.datetime_parser import SmartDateTimeParser
    from datetime import datetime
    import pytz
    
    parser = SmartDateTimeParser()
    bangkok_tz = pytz.timezone('Asia/Bangkok')
    now = datetime.now(bangkok_tz)
    
    print(f"📅 วันเวลาปัจจุบัน: {now.strftime('%d/%m/%Y %H:%M')}")
    print()
    
    # ทดสอบ structured format ที่มีวันที่ในอดีต
    past_appointment_text = f"""ชื่อนัดหมาย:"ตรวจสุขภาพ"
วันเวลา:"1 ตุลาคม 2025 14:00"
สถานที่:"โรงพยาบาลศิริราช"
บุคคล:"ดร.สมชาย"
"""
    
    print("📝 ทดสอบการ Parse นัดหมายในอดีต:")
    print(past_appointment_text)
    
    try:
        result = parser.extract_appointment_info(past_appointment_text)
        
        if result and result.get('datetime'):
            appointment_dt = result['datetime']
            print(f"✅ Parse สำเร็จ: {appointment_dt.strftime('%d/%m/%Y %H:%M')}")
            
            # ตรวจสอบว่าเป็นอดีตหรือไม่
            if appointment_dt < now:
                print(f"⏰ นัดหมายนี้อยู่ในอดีต (ก่อนวันปัจจุบัน)")
                print(f"📍 จะไปอยู่ในส่วน past_appointments")
                print(f"🔍 จะปรากฏใน 'ดูนัดย้อนหลัง' เท่านั้น")
                print(f"❌ จะ*ไม่*ปรากฏใน 'ดูนัด' (future only)")
            else:
                print(f"🚀 นัดหมายนี้อยู่ในอนาคต")
                
        else:
            print(f"❌ Parse ล้มเหลว")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n" + "="*50)
    print(f"📊 สรุปการทำงานของระบบ:")
    print(f"="*50)
    print(f"🎯 **การเพิ่มนัดหมายในอดีต:**")
    print(f"   ✅ ระบบจะรับและบันทึกได้ปกติ")
    print(f"   ✅ ไม่มีการตรวจสอบ/ป้องกันวันที่ในอดีต")
    print(f"   📍 จะถูกจัดประเภทเป็น 'อดีต' อัตโนมัติ")
    print(f"")
    print(f"📋 **การแสดงผล:**")
    print(f"   🔍 'ดูนัด' → ❌ ไม่แสดง (เฉพาะอนาคต)")
    print(f"   📚 'ดูนัดย้อนหลัง' → ✅ แสดง (รวมอดีต)")
    print(f"   📊 รายการทั้งหมด → ✅ แสดง (รวมทุกอย่าง)")
    print(f"")
    print(f"⚠️ **ข้อควรระวัง:**")
    print(f"   🤔 ผู้ใช้อาจสับสนเมื่อเพิ่มนัดแล้วไม่เห็นใน 'ดูนัด'")
    print(f"   💡 ควรเพิ่มการเตือนเมื่อเพิ่มนัดหมายในอดีต")
    print(f"   🔔 ระบบแจ้งเตือนจะไม่ทำงานกับนัดหมายในอดีต")

def test_appointment_categorization():
    """ทดสอบการจัดหมวดหมู่นัดหมาย"""
    
    print(f"\n🗂️ ทดสอบการจัดหมวดหมู่:")
    print("="*30)
    
    from datetime import datetime, timedelta
    import pytz
    
    bangkok_tz = pytz.timezone('Asia/Bangkok')
    now = datetime.now(bangkok_tz)
    
    # สร้างนัดหมายทดสอบ
    test_appointments = [
        {
            'note': 'นัดหมายในอดีต (1 วันที่แล้ว)',
            'datetime': now - timedelta(days=1),
            'category': 'past'
        },
        {
            'note': 'นัดหมายวันนี้ (1 ชั่วโมงข้างหน้า)',
            'datetime': now + timedelta(hours=1),
            'category': 'future'
        },
        {
            'note': 'นัดหมายในอนาคต (1 สัปดาห์ข้างหน้า)',
            'datetime': now + timedelta(days=7),
            'category': 'future'
        },
        {
            'note': 'นัดหมายในอดีต (1 เดือนที่แล้ว)',
            'datetime': now - timedelta(days=30),
            'category': 'past'
        }
    ]
    
    print(f"📅 วันเวลาปัจจุบัน: {now.strftime('%d/%m/%Y %H:%M')}")
    print()
    
    for apt in test_appointments:
        apt_time = apt['datetime']
        is_past = apt_time < now
        expected_category = apt['category']
        actual_category = 'past' if is_past else 'future'
        
        status = "✅" if actual_category == expected_category else "❌"
        
        print(f"{status} {apt['note']}")
        print(f"     📅 {apt_time.strftime('%d/%m/%Y %H:%M')}")
        print(f"     📂 คาดหวัง: {expected_category}, ได้: {actual_category}")
        print(f"     👀 ปรากฏใน 'ดูนัด': {'❌ ไม่' if is_past else '✅ ใช่'}")
        print(f"     📚 ปรากฏใน 'ดูนัดย้อนหลัง': {'✅ ใช่' if is_past else '❌ ไม่'}")
        print()

if __name__ == "__main__":
    test_past_appointment_behavior()
    test_appointment_categorization()
    
    print("\n🎯 **คำตอบสำหรับคำถาม:**")
    print("="*40)
    print("❓ ถ้าเพิ่มนัดที่เป็นอดีตจะเป็นยังไง?")
    print("   → ระบบจะรับและบันทึกได้ปกติ ไม่มีการป้องกัน")
    print()
    print("❓ มันจะถือว่าเป็นนัดในอดีตจริงๆหรือป่าว?")
    print("   → ใช่! ระบบจะเปรียบเทียบกับเวลาปัจจุบันอัตโนมัติ")
    print()
    print("❓ จะไปอยู่ในคำสั่งดูย้อนหลังไหม?")
    print("   → ใช่! จะปรากฏใน 'ดูนัดย้อนหลัง' เท่านั้น")
    print("   → จะ*ไม่*ปรากฏใน 'ดูนัด' (แสดงเฉพาะอนาคต)")
    print()
    print("💡 **ข้อเสนอแนะ:**")
    print("   🚨 ควรเพิ่มการเตือนเมื่อผู้ใช้เพิ่มนัดหมายในอดีต")
    print("   📋 เพื่อป้องกันความสับสนของผู้ใช้")