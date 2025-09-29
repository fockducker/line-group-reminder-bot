#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Test for Delete and Edit Appointment Functions
ทดสอบฟังก์ชันลบและแก้ไขนัดหมายแบบ integration test จริงๆ
"""

import sys
import os
import uuid
from datetime import datetime

# Add the project root directory to sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from storage.models import Appointment
from storage.sheets_repo import SheetsRepository
from handlers import handle_delete_appointment_command, handle_edit_appointment_command, handle_add_appointment_command

def create_test_appointment():
    """สร้างนัดหมายทดสอบใน Google Sheets"""
    
    print("📝 Creating test appointment...")
    
    # สร้าง test appointment
    test_id = str(uuid.uuid4())[:8]  # สั้นๆ เพื่อง่ายต่อการทดสอบ
    test_datetime = "2025-10-15T14:30:00"
    
    appointment = Appointment(
        id=test_id,
        group_id="test_user_123",  # ใช้ test user
        datetime_iso=test_datetime,
        hospital="โรงพยาบาลทดสอบ",
        department="แผนกทดสอบ", 
        note="การนัดทดสอบ",
        location="ห้องทดสอบ"
    )
    
    # บันทึกลง Google Sheets
    repo = SheetsRepository()
    
    try:
        # ลองบันทึกผ่าน add_appointment function
        success = repo.add_appointment(appointment, "personal")
        if success:
            print(f"✅ Test appointment created with ID: {test_id}")
            return test_id, appointment
        else:
            print("❌ Failed to create test appointment")
            return None, None
    except Exception as e:
        print(f"❌ Error creating test appointment: {e}")
        return None, None

def test_delete_function(test_id):
    """ทดสอบฟังก์ชันลบนัดหมาย"""
    
    print(f"\n🗑️ Testing delete function with ID: {test_id}")
    
    # Mock parameters สำหรับ personal chat
    user_id = "test_user_123"
    context_type = "personal" 
    context_id = "test_user_123"
    
    # ทดสอบการลบ
    message = f"ลบนัด {test_id}"
    result = handle_delete_appointment_command(message, user_id, context_type, context_id)
    
    print("Delete Result:")
    print(result)
    
    # ตรวจสอบว่าลบสำเร็จหรือไม่
    if "✅ ลบนัดหมายเรียบร้อย" in result:
        print("✅ Delete function works correctly!")
        return True
    else:
        print("❌ Delete function failed!")
        return False

def test_edit_function(test_id):
    """ทดสอบฟังก์ชันแก้ไขนัดหมาย"""
    
    print(f"\n🔄 Testing edit function with ID: {test_id}")
    
    # Mock parameters สำหรับ personal chat
    user_id = "test_user_123"
    context_type = "personal"
    context_id = "test_user_123"
    
    # ทดสอบการแก้ไข
    message = f'แก้ไขนัด {test_id} แผนก:"แผนกใหม่"'
    result = handle_edit_appointment_command(message, user_id, context_type, context_id)
    
    print("Edit Result:")
    print(result)
    
    # ตรวจสอบว่าแก้ไขสำเร็จหรือไม่
    if "✅ แก้ไขนัดหมายเรียบร้อย" in result:
        print("✅ Edit function works correctly!")
        return True
    else:
        print("❌ Edit function failed!")
        return False

def test_list_appointments():
    """ทดสอบว่า list appointments ทำงานได้"""
    
    print("\n📋 Testing list appointments...")
    
    repo = SheetsRepository()
    appointments = repo.get_appointments("test_user_123", "personal")
    
    print(f"Found {len(appointments)} appointments for test user")
    for apt in appointments:
        print(f"  - ID: {apt.id}, Note: {apt.note}")
    
    return len(appointments) > 0

def cleanup_test_data():
    """ลบข้อมูลทดสอบ"""
    
    print("\n🧹 Cleaning up test data...")
    
    repo = SheetsRepository()
    appointments = repo.get_appointments("test_user_123", "personal")
    
    cleaned_count = 0
    for apt in appointments:
        if "ทดสอบ" in apt.note or apt.group_id == "test_user_123":
            try:
                repo.delete_appointment(apt.id, "personal")
                cleaned_count += 1
            except Exception as e:
                print(f"Error cleaning up {apt.id}: {e}")
    
    print(f"🧹 Cleaned up {cleaned_count} test appointments")

def main():
    """รัน integration test ทั้งหมด"""
    
    print("🧪 LINE Bot Delete/Edit Integration Test")
    print("=" * 60)
    
    # ตรวจสอบการเชื่อมต่อ Google Sheets
    repo = SheetsRepository()
    if not repo.gc:
        print("❌ Google Sheets not connected! Cannot run integration tests.")
        print("💡 Make sure GOOGLE_CREDENTIALS_JSON is set in environment variables.")
        return False
    
    print("✅ Google Sheets connected successfully")
    
    # ลบข้อมูลทดสอบเก่าก่อน
    cleanup_test_data()
    
    # สร้างนัดหมายทดสอบ
    test_id, test_appointment = create_test_appointment()
    if not test_id:
        print("❌ Cannot create test appointment, aborting tests")
        return False
    
    all_tests_passed = True
    
    try:
        # ทดสอบ list appointments
        if not test_list_appointments():
            print("❌ List appointments test failed")
            all_tests_passed = False
        
        # ทดสอบ edit function
        if not test_edit_function(test_id):
            print("❌ Edit function test failed")
            all_tests_passed = False
        
        # ทดสอบ delete function (ทำหลังสุดเพราะจะลบข้อมูลทิ้ง)
        if not test_delete_function(test_id):
            print("❌ Delete function test failed")
            all_tests_passed = False
    
    finally:
        # ทำความสะอาดข้อมูลทดสอบ
        cleanup_test_data()
    
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ Delete and Edit functions are working correctly")
        print("🚀 Safe to commit and deploy!")
    else:
        print("❌ SOME TESTS FAILED!")
        print("🔧 Please fix issues before committing")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)