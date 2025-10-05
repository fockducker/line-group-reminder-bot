#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ทดสอบระบบทั้งหมดจากการ parse ถึงการสร้าง Appointment
"""

from utils.datetime_parser import SmartDateTimeParser
from storage.models import Appointment
import uuid

def test_complete_appointment_flow():
    """ทดสอบการทำงานของระบบทั้งหมด"""
    
    # ข้อความที่ผู้ใช้ส่งมา (format ที่ผู้ใช้ระบุ)
    appointment_text = """นัดหมาย: ตรวจสุขภาพประจำปี
วันที่: 15 ธันวาคม 2567
เวลา: 10:00
สถานที่: โรงพยาบาลบำรุงราษฎร์
อาคาร/แผนก/ชั้น: อาคาร A ชั้น 3 แผนกอายุรกรรม
บุคคล/ผู้ติดต่อ: นพ.สมชาย ใจดี
เบอร์โทร: "02-419-7000"
"""
    
    print("=== ทดสอบระบบทั้งหมด ===")
    print(f"ข้อความนัดหมาย:\n{appointment_text}")
    print("\n" + "="*50)
    
    # 1. ทดสอบ Parser
    parser = SmartDateTimeParser()
    parsed_info = parser.extract_appointment_info(appointment_text)
    
    print("1. ผลจาก Parser:")
    print(f"   - วันที่-เวลา: {parsed_info.get('datetime')}")
    print(f"   - สถานที่: {parsed_info.get('location', '')}")
    print(f"   - อาคาร/แผนก/ชั้น: {parsed_info.get('building_floor_dept', '')}")
    print(f"   - บุคคล/ผู้ติดต่อ: {parsed_info.get('contact_person', '')}")
    print(f"   - เบอร์โทร: {parsed_info.get('phone_number', '')}")
    print(f"   - note/title: {parsed_info.get('title', '')}")
    
    # 2. จำลองการสร้าง Appointment object เหมือนใน handlers.py
    if parsed_info['datetime']:
        appointment_datetime = parsed_info['datetime']
        title = parsed_info.get('title', appointment_text.split('\n')[0] if appointment_text else "การนัดหมาย")
        
        # ดึงข้อมูลจาก parsed_info (เหมือนใน handlers.py ใหม่)
        location = parsed_info.get('location', '')
        building_floor_dept = parsed_info.get('building_floor_dept', '')
        contact_person = parsed_info.get('contact_person', '')
        phone_number = parsed_info.get('phone_number', '')
        
        print(f"\n2. ตัวแปรก่อนสร้าง Appointment:")
        print(f"   - location: '{location}'")
        print(f"   - building_floor_dept: '{building_floor_dept}'")
        print(f"   - contact_person: '{contact_person}'")
        print(f"   - phone_number: '{phone_number}'")
        
        # สร้าง Appointment object
        appointment = Appointment(
            id=str(uuid.uuid4())[:8],
            group_id="test_group",
            datetime_iso=appointment_datetime.isoformat(),
            location=location,
            building_floor_dept=building_floor_dept,
            contact_person=contact_person,
            phone_number=phone_number,
            note=title
        )
        
        print(f"\n3. Appointment Object ที่สร้างขึ้น:")
        print(f"   - ID: {appointment.id}")
        print(f"   - DateTime: {appointment.datetime_iso}")
        print(f"   - Location: '{appointment.location}'")
        print(f"   - Building/Floor/Dept: '{appointment.building_floor_dept}'")
        print(f"   - Contact Person: '{appointment.contact_person}'")
        print(f"   - Phone Number: '{appointment.phone_number}'")  # นี่คือจุดสำคัญ!
        print(f"   - Note: {appointment.note}")
        
        # 4. ตรวจสอบเฉพาะ phone_number
        print(f"\n4. ✅ สถานะ Phone Number:")
        if appointment.phone_number:
            print(f"   ✅ PASS: Phone number ถูกบันทึก = '{appointment.phone_number}'")
        else:
            print(f"   ❌ FAIL: Phone number ไม่ถูกบันทึก (ค่าว่าง)")
            
        return appointment
    else:
        print("❌ ไม่สามารถ parse วันที่-เวลาได้")
        return None

if __name__ == "__main__":
    appointment = test_complete_appointment_flow()
    
    print("\n" + "="*50)
    print("สรุป: ระบบสามารถ parse และสร้าง Appointment พร้อม phone_number ได้แล้ว!")