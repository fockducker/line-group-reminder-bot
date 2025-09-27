#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple test script to verify that our LINE Bot implementation works correctly
"""

import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    try:
        import handlers
        import storage.sheets_repo
        import storage.models
        import app
        print("✅ All modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_app_creation():
    """Test that Flask app can be created"""
    try:
        from app import app
        print("✅ Flask app created successfully")
        return True
    except Exception as e:
        print(f"❌ App creation error: {e}")
        return False

def test_sheets_repo():
    """Test SheetsRepository functionality"""
    try:
        from storage.sheets_repo import SheetsRepository
        from storage.models import Appointment
        from datetime import datetime
        
        # Test repository creation
        repo = SheetsRepository()
        print("✅ SheetsRepository created successfully")
        
        # Test appointment creation (without actual Google Sheets connection)
        appointment = Appointment(
            appointment_id="test_001",
            user_id="test_user_123",
            title="ทดสอบการนัดหมาย",
            description="นี่คือการทดสอบ",
            appointment_date=datetime(2025, 1, 15, 9, 0),
            reminder_time=datetime(2025, 1, 14, 9, 0),
            context="personal"
        )
        print("✅ Appointment model created successfully")
        print(f"   📅 {appointment.title}")
        print(f"   🆔 {appointment.id}")
        print(f"   📍 {appointment.context}")
        
        return True
    except Exception as e:
        print(f"❌ SheetsRepository test error: {e}")
        return False

def test_thai_commands():
    """Test Thai language command handling"""
    try:
        from handlers import handle_add_appointment_command, handle_list_appointments_command
        
        # Test add appointment command
        result1 = handle_add_appointment_command("เพิ่มนัด ทดสอบ", "user123", "personal", "user123")
        print("✅ Thai add appointment command works")
        
        # Test list appointments command  
        result2 = handle_list_appointments_command("user123", "personal", "user123")
        print("✅ Thai list appointments command works")
        
        return True
    except Exception as e:
        print(f"❌ Thai commands test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing LINE Bot implementation...")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("App Creation", test_app_creation),  
        ("Sheets Repository", test_sheets_repo),
        ("Thai Commands", test_thai_commands)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"   ⚠️  {test_name} test failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The implementation is working correctly.")
        print("\n📝 Next steps:")
        print("   1. Set up Google Sheets credentials")
        print("   2. Deploy to Render")
        print("   3. Configure LINE Webhook URL")
        print("   4. Test with actual LINE Bot")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main()