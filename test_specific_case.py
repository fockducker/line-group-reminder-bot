#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test specific case: กินข้าวกับเพื่อน พฤหัส4โมงเย็น เซ็นทรัลลาดพร้าว
"""

import sys
import os
import json
from datetime import datetime

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

try:
    from enhanced_smart_parser import EnhancedSmartDateTimeParser
    
    # Test the specific case
    parser = EnhancedSmartDateTimeParser()
    
    test_text = "กินข้าวกับเพื่อน พฤหัส4โมงเย็น เซ็นทรัลลาดพร้าว"
    
    print("🧪 Testing Enhanced Smart Parser - Specific Case")
    print("=" * 60)
    print(f"Input: {test_text}")
    print("-" * 60)
    
    result = parser.extract_appointment_info(test_text)
    
    print("📊 Results:")
    fields = [
        ('นัดหมาย', result.get('appointment_title', '')),
        ('วันที่', result.get('date', '')),
        ('เวลา', result.get('time', '')),
        ('สถานที่', result.get('location', '')),
        ('บุคคล/ผู้ติดต่อ', result.get('contact_person', '')),
        ('Confidence', result.get('confidence', 0))
    ]
    
    for field_name, field_value in fields:
        if field_value:
            print(f"  {field_name}: '{field_value}'")
    
    print("\n📝 Full JSON Result:")
    print("-" * 30)
    
    # Clean result for JSON export
    clean_result = {}
    for key, value in result.items():
        if key == 'datetime' and value:
            clean_result[key] = str(value)
        elif key != 'processed_data':  # Skip debug data
            clean_result[key] = value
    
    print(json.dumps(clean_result, ensure_ascii=False, indent=2))
    
    # Check for expected improvements
    print("\n✅ Validation:")
    
    # Calculate correct Thursday (October 10, 2025 is a Friday, so next Thursday is Oct 9)
    # Actually, let's check what day Oct 10 is in 2025
    from datetime import datetime
    oct_10_2025 = datetime(2025, 10, 10)
    print(f"  Debug: Oct 10, 2025 is a {oct_10_2025.strftime('%A')}")
    
    # Since today is Oct 7 (Monday), next Thursday should be Oct 9
    expected_date = "09/10/2025"  # Thursday next week (corrected)
    actual_date = result.get('date', '')
    date_ok = expected_date == actual_date
    print(f"  วันที่: expected '{expected_date}' (Thursday), got '{actual_date}' {'✅' if date_ok else '❌'}")
    
    expected_location = "เซ็นทรัลลาดพร้าว"
    actual_location = result.get('location', '')
    location_ok = expected_location in actual_location and 'สินค้า' not in actual_location
    print(f"  สถานที่: expected '{expected_location}' (without 'สินค้า'), got '{actual_location}' {'✅' if location_ok else '❌'}")
    
    expected_time = "16.00"
    actual_time = result.get('time', '')
    time_ok = expected_time == actual_time
    print(f"  เวลา: expected '{expected_time}', got '{actual_time}' {'✅' if time_ok else '❌'}")
    
    print(f"\n🎯 Overall: {'✅ IMPROVED' if date_ok or location_ok else '❌ STILL NEEDS WORK'}")
    
except ImportError as e:
    print(f"❌ Cannot import Enhanced Parser: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

input("\nPress Enter to exit...")