#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug การทำงานของ _parse_structured_appointment โดยตรง
"""

from utils.datetime_parser import SmartDateTimeParser
import logging

# ตั้งค่า logging เพื่อดู debug information
logging.basicConfig(level=logging.DEBUG)

def test_structured_parsing_direct():
    """ทดสอบ _parse_structured_appointment โดยตรง"""
    
    appointment_text = """นัดหมาย: ตรวจสุขภาพประจำปี
วันที่: 15 ธันวาคม 2567
เวลา: 10:00
สถานที่: โรงพยาบาลบำรุงราษฎร์
อาคาร/แผนก/ชั้น: อาคาร A ชั้น 3 แผนกอายุรกรรม
บุคคล/ผู้ติดต่อ: นพ.สมชาย ใจดี
เบอร์โทร: "02-419-7000"
"""
    
    print("=== ทดสอบ _parse_structured_appointment โดยตรง ===")
    print(f"ข้อความนัดหมาย:\n{appointment_text}")
    print("\n" + "="*60)
    
    parser = SmartDateTimeParser()
    
    # เรียก _parse_structured_appointment โดยตรง
    result = parser._parse_structured_appointment(appointment_text)
    
    if result:
        print("✅ ผลลัพธ์จาก _parse_structured_appointment:")
        for key, value in result.items():
            print(f"   {key}: '{value}'")
            
        # ตรวจสอบเฉพาะ phone_number
        phone_number = result.get('phone_number', '')
        print(f"\n🔍 ตรวจสอบ phone_number:")
        print(f"   Type: {type(phone_number)}")
        print(f"   Value: '{phone_number}'")
        print(f"   Length: {len(phone_number)}")
        
        if phone_number:
            print(f"   ✅ มี phone_number = '{phone_number}'")
        else:
            print(f"   ❌ ไม่มี phone_number (ค่าว่าง)")
            
    else:
        print("❌ _parse_structured_appointment ส่งคืน None")
        
    print("\n" + "="*60)
    
    # ลองใช้ extract_appointment_info เปรียบเทียบ
    print("เปรียบเทียบกับ extract_appointment_info:")
    result2 = parser.extract_appointment_info(appointment_text)
    
    phone_number2 = result2.get('phone_number', '')
    print(f"   phone_number จาก extract_appointment_info: '{phone_number2}'")
    
    return result

if __name__ == "__main__":
    test_structured_parsing_direct()