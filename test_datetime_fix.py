#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test DateTime Parsing Fix
"""

import sys
import os

# Add the project root directory to sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.datetime_parser import SmartDateTimeParser

def test_datetime_formats():
    """ทดสอบการ parse datetime รูปแบบต่างๆ"""
    
    parser = SmartDateTimeParser()
    
    # Test cases for datetime parsing
    test_cases = [
        {
            "text": "วันที่ 1 ตุลาคม 2025 เวลา 13.00 โรงพยาบาล ศิริราช แผนก อายุรกรรม พบ ดร.สมใส",
            "expected_date": "01/10/2025",
            "expected_time": "13:00",
            "description": "Complex format with dot time"
        },
        {
            "text": "วันที่ 8 ตุลาคม 2025 เวลา 14:30 โรงพยาบาล ศิริราช แผนก อายุรกรรม พบ ดร.วิศิษฎ์",
            "expected_date": "08/10/2025", 
            "expected_time": "14:30",
            "description": "Complex format with colon time"
        },
        {
            "text": "วันที่ 15/11/2025 เวลา 09.15 โรงพยาบาล ศิริราช แผนก อายุรกรรม พบ พญ.นิภา",
            "expected_date": "15/11/2025",
            "expected_time": "09:15", 
            "description": "Date slash format with dot time"
        }
    ]
    
    print("🔍 Testing DateTime Parsing Fix...")
    print("=" * 50)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['description']}")
        print(f"Input: {repr(test_case['text'])}")
        
        try:
            result = parser._parse_complex_appointment(test_case['text'])
            
            if result is not None:
                print(f"✅ Parsed successfully!")
                dt = result['datetime']
                date_str = dt.strftime('%d/%m/%Y')
                time_str = dt.strftime('%H:%M')
                print(f"   Date: {date_str}")
                print(f"   Time: {time_str}")
                print(f"   Doctor: {result['doctor']}")
                
                # Check if results match expectations
                date_match = date_str == test_case['expected_date']
                time_match = time_str == test_case['expected_time']
                
                if date_match and time_match:
                    print(f"✅ Results match expectations!")
                else:
                    print(f"❌ Results don't match:")
                    if not date_match:
                        print(f"   Expected date: {test_case['expected_date']}, got: {result['appointment']['date']}")
                    if not time_match:
                        print(f"   Expected time: {test_case['expected_time']}, got: {result['appointment']['time']}")
                    all_passed = False
            else:
                print(f"❌ Parse failed: No structured appointment found")
                all_passed = False
                
        except Exception as e:
            print(f"❌ Exception occurred: {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All datetime parsing tests PASSED!")
    else:
        print("❌ Some tests FAILED - need further investigation")
    
    return all_passed

if __name__ == "__main__":
    test_datetime_formats()