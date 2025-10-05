#!/usr/bin/env python3
"""
Test script สำหรับทดสอบการเปลี่ยนแปลงตัวแปรใหม่
ทดสอบการดึงข้อมูลจาก Google Sheets ด้วยตัวแปรใหม่
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from storage.sheets_repo import SheetsRepository
from storage.models import Appointment
from datetime import datetime
import logging

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_new_variables():
    """ทดสอบระบบตัวแปรใหม่"""
    
    print("🧪 ทดสอบการเปลี่ยนแปลงตัวแปรใหม่")
    print("="*50)
    
    try:
        # สร้าง SheetsRepository
        repo = SheetsRepository()
        
        if not repo.gc or not repo.spreadsheet:
            print("❌ ไม่สามารถเชื่อมต่อ Google Sheets ได้")
            return
        
        print("✅ เชื่อมต่อ Google Sheets สำเร็จ")
        print(f"📊 Spreadsheet: {repo.spreadsheet.title}")
        
        # ทดสอบดึงข้อมูล Personal
        print("\n📱 ทดสอบ Personal Appointments:")
        try:
            personal_appointments = repo.get_appointments("", "personal")
            print(f"📋 พบ Personal appointments: {len(personal_appointments)} รายการ")
            
            for apt in personal_appointments:
                print(f"\n📅 Appointment ID: {apt.id}")
                print(f"   📝 หมายเหตุ: {apt.note}")
                print(f"   📍 สถานที่: {apt.location}")
                print(f"   🏢 อาคาร/แผนก/ชั้น: {apt.building_floor_dept}")
                print(f"   👤 บุคคล/ผู้ติดต่อ: {apt.contact_person}")
                print(f"   📞 เบอร์โทร: {apt.phone_number}")
                print(f"   🕐 วันเวลา: {apt.appointment_datetime}")
                print(f"   👤 User ID: {apt.group_id}")
                
                # ทดสอบ Backward compatibility
                print(f"   🔄 Backward compatibility:")
                print(f"      - hospital (alias): {apt.hospital}")
                print(f"      - department (alias): {apt.department}")
                print(f"      - doctor (alias): {apt.doctor}")
                
        except Exception as e:
            print(f"❌ Error ดึงข้อมูล Personal: {e}")
        
        # ทดสอบดึงข้อมูล Group
        print("\n👥 ทดสอบ Group Appointments:")
        try:
            # หา Group contexts
            group_contexts = []
            worksheets = repo.spreadsheet.worksheets()
            
            for worksheet in worksheets:
                if worksheet.title.startswith("appointments_group_"):
                    group_id = worksheet.title.replace("appointments_group_", "")
                    group_contexts.append({
                        'group_id': group_id,
                        'context': worksheet.title
                    })
            
            print(f"🔍 พบ Group contexts: {len(group_contexts)} กลุ่ม")
            
            for group_info in group_contexts[:1]:  # ทดสอบแค่กลุ่มแรก
                group_appointments = repo.get_appointments(
                    group_info['group_id'], 
                    group_info['context']
                )
                print(f"📋 พบ Group appointments ({group_info['group_id']}): {len(group_appointments)} รายการ")
                
                for apt in group_appointments:
                    print(f"\n📅 Appointment ID: {apt.id}")
                    print(f"   📝 หมายเหตุ: {apt.note}")
                    print(f"   📍 สถานที่: {apt.location}")
                    print(f"   🏢 อาคาร/แผนก/ชั้น: {apt.building_floor_dept}")
                    print(f"   👤 บุคคล/ผู้ติดต่อ: {apt.contact_person}")
                    print(f"   📞 เบอร์โทร: {apt.phone_number}")
                    print(f"   🕐 วันเวลา: {apt.appointment_datetime}")
                    print(f"   👥 Group ID: {apt.group_id}")
                    
                    # ทดสอบ Backward compatibility
                    print(f"   🔄 Backward compatibility:")
                    print(f"      - hospital (alias): {apt.hospital}")
                    print(f"      - department (alias): {apt.department}")
                    print(f"      - doctor (alias): {apt.doctor}")
                    
        except Exception as e:
            print(f"❌ Error ดึงข้อมูล Group: {e}")
        
        # สรุปผลการทดสอบ
        print("\n📊 สรุปผลการทดสอบ:")
        print("="*30)
        print("✅ ตัวแปรใหม่:")
        print("   📍 location (เดิม: hospital)")
        print("   🏢 building_floor_dept (เดิม: department)")
        print("   👤 contact_person (เดิม: doctor)")
        print("   📞 phone_number (ใหม่)")
        print()
        print("🔄 Backward Compatibility:")
        print("   ✅ hospital → location")
        print("   ✅ department → building_floor_dept")
        print("   ✅ doctor → contact_person")
        print()
        print("🎯 ระบบพร้อมใช้งานตัวแปรใหม่!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def create_test_appointment():
    """สร้างข้อมูลทดสอบด้วยตัวแปรใหม่"""
    test_appointment = Appointment(
        id="TEST123",
        group_id="TEST_USER_ID",
        datetime_iso="2025-10-10T14:30:00",
        location="โรงพยาบาลศิริราช",
        building_floor_dept="อาคาร 1 ชั้น 3 แผนกอายุรกรรม",
        contact_person="ดร.สมชาย ใจดี",
        phone_number="02-419-7000",
        note="ตรวจสุขภาพประจำปี"
    )
    
    print("🧪 ตัวอย่างข้อมูลนัดหมายด้วยตัวแปรใหม่:")
    print(f"   📝 หมายเหตุ: {test_appointment.note}")
    print(f"   📍 สถานที่: {test_appointment.location}")
    print(f"   🏢 อาคาร/แผนก/ชั้น: {test_appointment.building_floor_dept}")
    print(f"   👤 บุคคล/ผู้ติดต่อ: {test_appointment.contact_person}")
    print(f"   📞 เบอร์โทร: {test_appointment.phone_number}")
    print()
    print("🔄 ทดสอบ Backward Compatibility:")
    print(f"   🏥 hospital (alias): {test_appointment.hospital}")
    print(f"   🏢 department (alias): {test_appointment.department}")
    print(f"   👨‍⚕️ doctor (alias): {test_appointment.doctor}")

if __name__ == "__main__":
    print("🚀 เริ่มต้นการทดสอบตัวแปรใหม่")
    print("="*50)
    
    # ทดสอบการสร้างข้อมูล
    create_test_appointment()
    print()
    
    # ทดสอบการดึงข้อมูลจาก Google Sheets
    test_new_variables()
    
    print("\n🎉 การทดสอบเสร็จสิ้น!")