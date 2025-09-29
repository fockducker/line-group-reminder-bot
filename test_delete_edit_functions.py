#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Delete and Edit Appointment Functions
ทดสอบฟังก์ชันการลบและแก้ไขนัดหมาย
"""

import sys
import os

# Add the project root directory to sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from handlers import handle_delete_appointment_command, handle_edit_appointment_command

def test_delete_appointment():
    """ทดสอบฟังก์ชันการลบนัดหมาย"""
    
    print("🔍 Testing Delete Appointment Function...")
    print("=" * 50)
    
    test_cases = [
        {
            "message": "ลบนัด ABC123",
            "description": "Standard delete format",
            "should_parse": True
        },
        {
            "message": "ยกเลิกนัด XYZ789",
            "description": "Alternative delete format",
            "should_parse": True
        },
        {
            "message": "ลบการนัด DEF456",
            "description": "Full phrase delete format",
            "should_parse": True
        },
        {
            "message": "ลบนัด",
            "description": "Missing appointment ID",
            "should_parse": False
        },
        {
            "message": "ลบนัดหมาย ABC123",
            "description": "Wrong command format",
            "should_parse": False
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['description']}")
        print(f"Input: {repr(test_case['message'])}")
        
        try:
            # Mock parameters
            user_id = "test_user"
            context_type = "personal"
            context_id = "test_context"
            
            result = handle_delete_appointment_command(
                test_case['message'], user_id, context_type, context_id
            )
            
            print(f"Result: {result[:100]}...")
            
            # Check if parsing worked as expected
            if test_case['should_parse']:
                # Should contain appointment ID in result if parsing worked
                if "ไม่พบนัดหมายรหัส" in result or "❌ รูปแบบไม่ถูกต้อง" in result:
                    if "ไม่พบนัดหมายรหัส" in result:
                        print("✅ Parsing successful (ID not found in DB - expected)")
                    else:
                        print("❌ Parsing failed when it should succeed")
                        all_passed = False
                else:
                    print("✅ Parsing successful")
            else:
                # Should show error message
                if "❌ รูปแบบไม่ถูกต้อง" in result:
                    print("✅ Correctly rejected invalid format")
                else:
                    print("❌ Should have rejected invalid format")
                    all_passed = False
                    
        except Exception as e:
            print(f"❌ Exception occurred: {str(e)}")
            all_passed = False
    
    return all_passed


def test_edit_appointment():
    """ทดสอบฟังก์ชันการแก้ไขนัดหมาย"""
    
    print("\n\n🔍 Testing Edit Appointment Function...")
    print("=" * 50)
    
    test_cases = [
        {
            "message": 'แก้ไขนัด ABC123 ชื่อนัดหมาย:"ตรวจร่างกาย"',
            "description": "Single field edit - title",
            "should_parse": True
        },
        {
            "message": '''แก้ไขนัด XYZ789
ชื่อนัดหมาย:"ปรึกษาตรวจฟัน"
วันเวลา:"8 ตุลาคม 2025 14:00"''',
            "description": "Multi-field edit - title and datetime",
            "should_parse": True
        },
        {
            "message": 'แก้นัด DEF456 แพทย์:"ดร.สมชาย" โรงพยาบาล:"ศิริราช"',
            "description": "Multi-field edit - doctor and hospital",
            "should_parse": True
        },
        {
            "message": "แก้ไขนัด ABC123",
            "description": "Missing update fields",
            "should_parse": False
        },
        {
            "message": "แก้ไขนัด",
            "description": "Missing appointment ID and fields",
            "should_parse": False
        },
        {
            "message": 'แก้ไขนัด ABC123 วันเวลา:"invalid date format"',
            "description": "Invalid datetime format",
            "should_parse": False
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['description']}")
        print(f"Input: {repr(test_case['message'])}")
        
        try:
            # Mock parameters
            user_id = "test_user"
            context_type = "personal"
            context_id = "test_context"
            
            result = handle_edit_appointment_command(
                test_case['message'], user_id, context_type, context_id
            )
            
            print(f"Result: {result[:100]}...")
            
            # Check if parsing worked as expected
            if test_case['should_parse']:
                if "❌ รูปแบบไม่ถูกต้อง" in result or "❌ ไม่พบข้อมูลที่ต้องการแก้ไข" in result:
                    if "ไม่พบนัดหมายรหัส" in result:
                        print("✅ Parsing successful (ID not found in DB - expected)")
                    else:
                        print("❌ Parsing failed when it should succeed")
                        all_passed = False
                else:
                    print("✅ Parsing successful")
            else:
                # Should show error message
                if "❌" in result:
                    print("✅ Correctly rejected invalid format")
                else:
                    print("❌ Should have rejected invalid format")
                    all_passed = False
                    
        except Exception as e:
            print(f"❌ Exception occurred: {str(e)}")
            all_passed = False
    
    return all_passed


def main():
    """รันการทดสอบทั้งหมด"""
    
    print("🏥 Testing Enhanced Delete and Edit Functions")
    print("=" * 60)
    
    # Test delete function
    delete_passed = test_delete_appointment()
    
    # Test edit function  
    edit_passed = test_edit_appointment()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    if delete_passed:
        print("✅ Delete Appointment Function: ALL TESTS PASSED")
    else:
        print("❌ Delete Appointment Function: SOME TESTS FAILED")
        
    if edit_passed:
        print("✅ Edit Appointment Function: ALL TESTS PASSED")
    else:
        print("❌ Edit Appointment Function: SOME TESTS FAILED")
    
    overall_success = delete_passed and edit_passed
    
    if overall_success:
        print("\n🎉 ALL TESTS PASSED! Functions are ready for use.")
    else:
        print("\n❌ SOME TESTS FAILED! Please review and fix issues.")
    
    return overall_success


if __name__ == "__main__":
    main()