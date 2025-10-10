#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test the improved extraction to fix contamination issues
"""

import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.enhanced_smart_parser import EnhancedSmartDateTimeParser

def test_contamination_fixes():
    parser = EnhancedSmartDateTimeParser()
    
    # Test case from user's image (reconstructed from what we can see)
    test_text = "เพิ่มนัด กินข้าวกับเพื่อนที่ร้านก่อรัฐอนุรราษมัยที่โอคอนคอนยามกับน้องบี"
    
    print(f"🧪 Testing Contamination Fixes")
    print("=" * 70)
    print(f"Input: {test_text}")
    print("-" * 70)
    
    result = parser.extract_appointment_info(test_text)
    
    print("📊 Results:")
    print(f"  นัดหมาย: '{result.get('appointment_title')}'")
    print(f"  วันที่: '{result.get('date')}'")
    print(f"  เวลา: '{result.get('time')}'")
    print(f"  สถานที่: '{result.get('location')}'")
    print(f"  อาคาร/แผนก: '{result.get('building_dept')}'")
    print(f"  ผู้ติดต่อ: '{result.get('contact_person')}'")
    print(f"  Confidence: '{result.get('confidence')}'")
    
    print("\n📝 Analysis:")
    
    # Check for contamination issues
    location = result.get('location', '')
    contact = result.get('contact_person', '')
    
    # Check if location contains person names
    location_has_person = any(word in location for word in ['เพื่อน', 'น้อง', 'กับ'])
    
    # Check if person contains location words  
    person_has_location = any(word in contact for word in ['ร้าน', 'ที่', 'ห้าง'])
    
    # Check if location contains time
    location_has_time = any(word in location for word in ['โมง', 'บ่าย', 'เช้า', 'เย็น'])
    
    # Check if person contains time
    person_has_time = any(word in contact for word in ['โมง', 'บ่าย', 'เช้า', 'เย็น'])
    
    print(f"  สถานที่มีชื่อคน: {'❌' if location_has_person else '✅'}")
    print(f"  บุคคลมีสถานที่: {'❌' if person_has_location else '✅'}")
    print(f"  สถานที่มีเวลา: {'❌' if location_has_time else '✅'}")
    print(f"  บุคคลมีเวลา: {'❌' if person_has_time else '✅'}")
    
    # Additional test cases
    additional_tests = [
        "นัดเจอกับลูกค้าที่ร้านกาแฟ 3โมงบ่าย",
        "ประชุมกับทีมงานที่อาคารAชั้น2 จันทร์หน้า",
        "กินข้าวกับเพื่อนพรุ่งนี้ที่ห้างเซ็นทรัล 6โมงเย็น",
    ]
    
    print(f"\n🔄 Additional Tests:")
    print("-" * 50)
    
    for i, test in enumerate(additional_tests, 1):
        print(f"\n{i}. Input: {test}")
        result = parser.extract_appointment_info(test)
        print(f"   สถานที่: '{result.get('location')}'")
        print(f"   อาคาร/แผนก: '{result.get('building_dept')}'")
        print(f"   ผู้ติดต่อ: '{result.get('contact_person')}'")
        print(f"   เวลา: '{result.get('time')}'")

if __name__ == "__main__":
    test_contamination_fixes()
    input("\nPress Enter to exit...")