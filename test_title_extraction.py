#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test the updated appointment title extraction
"""

import sys
import os
from datetime import datetime

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.enhanced_smart_parser import EnhancedSmartDateTimeParser

def main():
    parser = EnhancedSmartDateTimeParser()
    
    # Test case from user's image
    test_text = "เพิ่มนัด กินข้าวกับเพื่อนศุกร์ มุ่งที่โอคอนคอนยามกับน้องบี"
    print(f"🧪 Testing Updated Title Extraction")
    print("=" * 60)
    print(f"Input: {test_text}")
    print("-" * 60)
    
    result = parser.extract_appointment_info(test_text)
    
    print("📊 Results:")
    print(f"  นัดหมาย: '{result.get('appointment_title')}'")
    print(f"  วันที่: '{result.get('date')}'")
    print(f"  เวลา: '{result.get('time')}'")
    print(f"  สถานที่: '{result.get('location')}'")
    print(f"  ผู้ติดต่อ: '{result.get('contact_person')}'")
    print(f"  Confidence: '{result.get('confidence')}'")
    
    print("\n📝 Expected vs Actual:")
    expected_title = "กินข้าวกับเพื่อนศุกร์ มุ่งที่โอคอนคอนยามกับน้องบี"
    actual_title = result.get('appointment_title')
    print(f"  Title: Expected '{expected_title}'")
    print(f"         Got      '{actual_title}'")
    print(f"         Status: {'✅' if expected_title in actual_title or len(actual_title) > len(expected_title)*0.8 else '❌'}")
    
    # Additional test cases
    additional_tests = [
        "นัดกินข้าวกับเพื่อนพรุ่งนี้ 6โมงเย็น",
        "ประชุมกับทีมงานจันทร์หน้า 10โมงเช้า",
        "ไปเที่ยวกับครูอาจารย์วันศุกร์ บ่าย2โมง",
    ]
    
    print("\n🔄 Additional Tests:")
    print("-" * 40)
    
    for i, test in enumerate(additional_tests, 1):
        print(f"{i}. Input: {test}")
        result = parser.extract_appointment_info(test)
        print(f"   Title: '{result.get('appointment_title')}'")
        print(f"   Contact: '{result.get('contact_person')}'")
        print()

if __name__ == "__main__":
    main()
    input("Press Enter to exit...")