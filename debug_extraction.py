#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug detailed extraction process
"""

import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.enhanced_smart_parser import EnhancedSmartDateTimeParser

def debug_extraction_process():
    parser = EnhancedSmartDateTimeParser()
    
    test_text = "เจอกันที่แผนกการเงิน 10โมงเช้า"
    
    print(f"🔍 Debug Extraction Process")
    print("=" * 50)
    print(f"Input: {test_text}")
    print()
    
    # Test preprocessing
    processed = parser.preprocess_text_basic(test_text)
    print(f"Normalized text: '{processed.get('normalized', '')}'")
    print(f"Location matches: {processed.get('location_matches', [])}")
    print()
    
    # Test building extraction
    building = parser.extract_building_department(processed)
    print(f"Building extraction: '{building}'")
    
    # Test location extraction
    location = parser.extract_smart_location(processed)
    print(f"Location extraction: '{location}'")
    
    # Full result
    result = parser.extract_appointment_info(test_text)
    print(f"\nFull result:")
    print(f"  location: '{result.get('location')}'")
    print(f"  building_dept: '{result.get('building_dept')}'")

if __name__ == "__main__":
    debug_extraction_process()
    input("\nPress Enter to exit...")