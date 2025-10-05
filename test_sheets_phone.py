#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ทดสอบการบันทึกข้อมูลลง Google Sheets พร้อม phone_number
"""

from utils.datetime_parser import SmartDateTimeParser
from storage.models import Appointment
from storage.sheets_repo import SheetsRepository
import uuid
import os

def test_save_to_sheets():
    """ทดสอบการบันทึกข้อมูลลง Google Sheets"""
    
    # ข้อความที่ผู้ใช้ส่งมา
    appointment_text = """นัดหมาย: ตรวจสุขภาพประจำปี
วันที่: 15 ธันวาคม 2567
เวลา: 10:00
สถานที่: โรงพยาบาลบำรุงราษฎร์
อาคาร/แผนก/ชั้น: อาคาร A ชั้น 3 แผนกอายุรกรรม
บุคคล/ผู้ติดต่อ: นพ.สมชาย ใจดี
เบอร์โทร: "02-419-7000"
"""
    
    print("=== ทดสอบการบันทึกลง Google Sheets ===")
    print(f"ข้อความนัดหมาย:\n{appointment_text}")
    print("\n" + "="*50)
    
    # 1. Parse ข้อมูล
    parser = SmartDateTimeParser()
    parsed_info = parser.extract_appointment_info(appointment_text)
    
    if not parsed_info['datetime']:
        print("❌ ไม่สามารถ parse วันที่-เวลาได้")
        return
    
    # 2. สร้าง Appointment object
    appointment_datetime = parsed_info['datetime']
    title = parsed_info.get('title', appointment_text.split('\n')[0] if appointment_text else "การนัดหมาย")
    
    location = parsed_info.get('location', '')
    building_floor_dept = parsed_info.get('building_floor_dept', '')
    contact_person = parsed_info.get('contact_person', '')
    phone_number = parsed_info.get('phone_number', '')
    
    appointment = Appointment(
        id=str(uuid.uuid4())[:8],
        group_id="test_group_sheets",
        datetime_iso=appointment_datetime.isoformat(),
        location=location,
        building_floor_dept=building_floor_dept,
        contact_person=contact_person,
        phone_number=phone_number,
        note=title
    )
    
    print("✅ สร้าง Appointment object สำเร็จ:")
    print(f"   - Phone Number: '{appointment.phone_number}'")
    
    # 3. ทดสอบการบันทึกลง Google Sheets
    try:
        sheets_repo = SheetsRepository()
        
        # ทดสอบการบันทึก
        success = sheets_repo.save_appointment(appointment)
        
        if success:
            print(f"✅ บันทึกลง Google Sheets สำเร็จ!")
            print(f"   - ID: {appointment.id}")
            print(f"   - Phone Number ที่บันทึก: '{appointment.phone_number}'")
            
            # ลองดึงข้อมูลกลับมาตรวจสอบ
            print("\n🔍 ตรวจสอบข้อมูลใน Google Sheets:")
            appointments = sheets_repo.load_appointments("test_group_sheets")
            
            for apt in appointments:
                if apt.id == appointment.id:
                    print(f"   ✅ พบข้อมูลใน Sheets:")
                    print(f"      - ID: {apt.id}")
                    print(f"      - Phone Number: '{apt.phone_number}'")
                    break
            else:
                print(f"   ❌ ไม่พบข้อมูลใน Sheets")
                
        else:
            print(f"❌ ไม่สามารถบันทึกลง Google Sheets ได้")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        
    return appointment

if __name__ == "__main__":
    # ตรวจสอบว่ามี credentials
    if not os.path.exists('.env'):
        print("⚠️  ไม่พบไฟล์ .env สำหรับ Google Sheets credentials")
        print("   การทดสอบจะข้าม Google Sheets testing")
        exit(0)
        
    test_save_to_sheets()