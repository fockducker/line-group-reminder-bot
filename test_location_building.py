#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test location vs building_dept extraction
"""

import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.enhanced_smart_parser import EnhancedSmartDateTimeParser

def test_location_building_separation():
    parser = EnhancedSmartDateTimeParser()
    
    test_cases = [
        {
            'text': 'ประชุมพรุ่งนี้ 2โมง ที่ร้านกาแฟ',
            'expected_location': 'ที่ร้านกาแฟ',
            'expected_building': '',
            'description': 'General location with ที่'
        },
        {
            'text': 'นัดหมายที่อาคารA ชั้น3 พรุ่งนี้',
            'expected_location': '',
            'expected_building': 'ที่อาคารA',  # Should pick first building pattern
            'description': 'Building-specific location'
        },
        {
            'text': 'เจอกันที่แผนกการเงิน 10โมงเช้า',
            'expected_location': '',
            'expected_building': 'ที่แผนกการเงิน',
            'description': 'Department-specific location'
        },
        {
            'text': 'กินข้าวที่ตึกB แล้วไปที่ร้านหนังสือ',
            'expected_location': 'ที่ร้านหนังสือ',  # General location should win
            'expected_building': 'ที่ตึกB',
            'description': 'Mixed: both building and general location'
        },
        {
            'text': 'ไปที่ห้างเซ็นทรัล พรุ่งนี้ 6โมงเย็น',
            'expected_location': 'เซ็นทรัล',  # Mall should be location
            'expected_building': '',
            'description': 'Mall location'
        },
        {
            'text': 'ประชุมที่ห้องประชุมA อาคาร1 ชั้น2',
            'expected_location': '',
            'expected_building': 'ที่ห้องประชุมA',  # Most specific building info
            'description': 'Multiple building references'
        },
        {
            'text': 'เดินทางไปที่สนามกีฬา',
            'expected_location': 'ที่สนามกีฬา',
            'expected_building': '',
            'description': 'Sports venue location'
        }
    ]
    
    print("🧪 Testing Location vs Building/Department Extraction")
    print("=" * 70)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print(f"Input: {test_case['text']}")
        print("-" * 50)
        
        result = parser.extract_appointment_info(test_case['text'])
        
        actual_location = result.get('location', '')
        actual_building = result.get('building_dept', '')
        
        location_passed = actual_location == test_case['expected_location']
        building_passed = actual_building == test_case['expected_building']
        
        print(f"  Location: expected '{test_case['expected_location']}', got '{actual_location}' {'✅' if location_passed else '❌'}")
        print(f"  Building: expected '{test_case['expected_building']}', got '{actual_building}' {'✅' if building_passed else '❌'}")
        
        test_passed = location_passed and building_passed
        print(f"  Result: {'✅ PASS' if test_passed else '❌ FAIL'}")
        
        if not test_passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    print(f"🎯 Overall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")

if __name__ == "__main__":
    test_location_building_separation()
    input("\nPress Enter to exit...")