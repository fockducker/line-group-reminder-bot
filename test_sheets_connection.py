#!/usr/bin/env python3
"""
Test script สำหรับทดสอบการเชื่อมต่อ Google Sheets
ใช้เพื่อ debug ปัญหา Google Sheets connection
"""

import os
import json
import sys
from datetime import datetime
from storage.sheets_repo import SheetsRepository
from storage.models import Appointment

def test_environment_variables():
    """ทดสอบการตั้งค่า Environment Variables"""
    print("🔍 ตรวจสอบ Environment Variables...")
    
    # ตรวจสอบ GOOGLE_CREDENTIALS_JSON
    credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    if not credentials_json:
        print("❌ GOOGLE_CREDENTIALS_JSON ไม่พบ")
        return False
    
    print(f"✅ GOOGLE_CREDENTIALS_JSON พบแล้ว (ความยาว: {len(credentials_json)} chars)")
    
    # ทดสอบ parse JSON
    try:
        credentials_data = json.loads(credentials_json)
        print(f"✅ JSON parse สำเร็จ - project_id: {credentials_data.get('project_id')}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse ไม่สำเร็จ: {e}")
        return False
    
    # ตรวจสอบ GOOGLE_SPREADSHEET_ID
    spreadsheet_id = os.getenv('GOOGLE_SPREADSHEET_ID')
    if not spreadsheet_id:
        print("❌ GOOGLE_SPREADSHEET_ID ไม่พบ")
        return False
    
    print(f"✅ GOOGLE_SPREADSHEET_ID พบแล้ว: {spreadsheet_id}")
    return True

def test_sheets_connection():
    """ทดสอบการเชื่อมต่อ Google Sheets"""
    print("\n🔗 ทดสอบการเชื่อมต่อ Google Sheets...")
    
    try:
        repo = SheetsRepository()
        
        if not repo.gc:
            print("❌ ไม่สามารถเชื่อมต่อ Google Sheets API")
            return False
        
        print("✅ เชื่อมต่อ Google Sheets API สำเร็จ")
        
        if not repo.spreadsheet:
            print("❌ ไม่สามารถเปิด Spreadsheet")
            return False
        
        print(f"✅ เปิด Spreadsheet สำเร็จ: {repo.spreadsheet.title}")
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

def test_create_appointment():
    """ทดสอบการสร้างและบันทึกข้อมูล"""
    print("\n📝 ทดสอบการบันทึกข้อมูล...")
    
    try:
        # สร้าง test appointment
        test_appointment = Appointment(
            id="test123",
            group_id="test_user",
            datetime_iso=datetime.now().isoformat(),
            hospital="Test Hospital",
            department="Test Department",
            doctor="Test Doctor",
            note="Test appointment from script"
        )
        
        print(f"✅ สร้าง Appointment object: {test_appointment.note}")
        
        # ทดสอบบันทึกลง Google Sheets
        repo = SheetsRepository()
        result = repo.add_appointment(test_appointment)
        
        if result:
            print("✅ บันทึกข้อมูลลง Google Sheets สำเร็จ")
        else:
            print("❌ บันทึกข้อมูลไม่สำเร็จ")
        
        return result
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการทดสอบ: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """ฟังก์ชันหลักสำหรับรันการทดสอบ"""
    print("🚀 เริ่มทดสอบ Google Sheets Connection")
    print("=" * 50)
    
    # Test 1: Environment Variables
    if not test_environment_variables():
        print("\n❌ การทดสอบล้มเหลว: Environment Variables ไม่ครบถ้วน")
        sys.exit(1)
    
    # Test 2: Google Sheets Connection
    if not test_sheets_connection():
        print("\n❌ การทดสอบล้มเหลว: ไม่สามารถเชื่อมต่อ Google Sheets")
        sys.exit(1)
    
    # Test 3: Create and Save Appointment
    if not test_create_appointment():
        print("\n❌ การทดสอบล้มเหลว: ไม่สามารถบันทึกข้อมูล")
        sys.exit(1)
    
    print("\n🎉 การทดสอบทั้งหมดสำเร็จ!")
    print("=" * 50)

if __name__ == "__main__":
    main()