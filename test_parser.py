#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test script for Enhanced Smart Parser
"""

import sys
import os
import json
from datetime import datetime

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

try:
    from enhanced_smart_parser import EnhancedSmartDateTimeParser
    
    # Test the parser
    parser = EnhancedSmartDateTimeParser()
    
    # Test case from user requirement
    test_text = "เพิ่มนัด กินข้าวเที่ยวกับที่รักบ่าย3โมง"
    
    print("🧪 Testing Enhanced Smart Parser")
    print("=" * 50)
    print(f"Input: {test_text}")
    print("-" * 50)
    
    result = parser.extract_appointment_info(test_text)
    
    print("📊 Results:")
    print(f"นัดหมาย: '{result.get('appointment_title', '')}'")
    print(f"วันที่: '{result.get('date', '')}'")
    print(f"เวลา: '{result.get('time', '')}'")
    print(f"สถานที่: '{result.get('location', '')}'")
    print(f"อาคาร/แผนก/ชั้น: '{result.get('building_dept', '')}'")
    print(f"บุคคล/ผู้ติดต่อ: '{result.get('contact_person', '')}'")
    print(f"เบอร์โทร: '{result.get('phone_number', '')}'")
    print(f"Confidence: {result.get('confidence', 0):.2f}")
    
    print("\n📝 Full JSON Result:")
    print("-" * 30)
    
    # Clean result for JSON export (remove datetime objects)
    clean_result = {}
    for key, value in result.items():
        if key == 'datetime' and value:
            clean_result[key] = str(value)
        elif key != 'processed_data':  # Skip debug data
            clean_result[key] = value
    
    print(json.dumps(clean_result, ensure_ascii=False, indent=2))
    
    print("\n✅ Parser test completed successfully!")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure enhanced_smart_parser.py is in utils/ directory")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()