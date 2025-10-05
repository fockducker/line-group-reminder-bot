#!/usr/bin/env python3
"""
ทดสอบ datetime_parser.py หลังอัปเดตตัวแปรใหม่
"""

from utils.datetime_parser import SmartDateTimeParser

def test_new_variables():
    """ทดสอบตัวแปรใหม่ในระบบ parsing"""
    
    print("🧪 ทดสอบ datetime_parser.py ด้วยตัวแปรใหม่")
    print("="*50)
    
    parser = SmartDateTimeParser()
    
    # ทดสอบ structured format ใหม่
    test_text = """ชื่อนัดหมาย:"ตรวจสุขภาพประจำปี"
วันเวลา:"8 ตุลาคม 2025 14:00"
สถานที่:"โรงพยาบาลศิริราช"
อาคาร:"อาคาร 1 ชั้น 3 แผนกอายุรกรรม"
บุคคล:"ดร.สมชาย ใจดี"
เบอร์โทร:"02-419-7000" """
    
    print("📝 ข้อความทดสอบ:")
    print(test_text)
    print()
    
    result = parser.extract_appointment_info(test_text)
    
    if result:
        print("🎯 ผลการ parsing สำเร็จ!")
        print(f"  📝 ชื่อ: {result.get('title')}")
        print(f"  📅 วันเวลา: {result.get('datetime')}")
        print(f"  📍 สถานที่: {result.get('location')}")
        print(f"  🏢 อาคาร/แผนก/ชั้น: {result.get('building_floor_dept')}")
        print(f"  👤 บุคคล/ผู้ติดต่อ: {result.get('contact_person')}")
        print(f"  📞 เบอร์โทร: {result.get('phone_number')}")
        print()
        print("🔄 ทดสอบ Backward Compatibility:")
        print(f"  🏥 hospital (alias): {result.get('hospital')}")
        print(f"  🏢 department (alias): {result.get('department')}")
        print(f"  👨‍⚕️ doctor (alias): {result.get('doctor')}")
        print()
        print("✅ datetime_parser.py อัปเดตเสร็จสมบูรณ์!")
        
    else:
        print("❌ การ parsing ล้มเหลว")
    
    # ทดสอบ natural language parsing
    print("\n" + "="*50)
    print("🧪 ทดสอบ Natural Language Parsing")
    
    natural_text = "เพิ่มนัด ตรวจเลือด วันที่ 10 ตุลาคม 2025 เวลา 09:00 โรงพยาบาลรามาธิบดี หมอสมหญิง"
    
    print(f"📝 ข้อความ: {natural_text}")
    
    result2 = parser.extract_appointment_info(natural_text)
    
    if result2:
        print("🎯 Natural parsing สำเร็จ!")
        print(f"  📝 ชื่อ: {result2.get('title')}")
        print(f"  📍 สถานที่: {result2.get('location')}")
        print(f"  👤 บุคคล/ผู้ติดต่อ: {result2.get('contact_person')}")
        print(f"  🔄 doctor (alias): {result2.get('doctor')}")
    else:
        print("❌ Natural parsing ล้มเหลว")

if __name__ == "__main__":
    test_new_variables()