#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quick test of the specific user case
"""

import sys
import os
from datetime import datetime

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.enhanced_smart_parser import EnhancedSmartDateTimeParser

def main():
    parser = EnhancedSmartDateTimeParser()
    
    test_text = "กินข้าวกับเพื่อน พฤหัส4โมงเย็น เซ็นทรัลลาดพร้าว"
    print(f"Testing: {test_text}")
    print("-" * 50)
    
    result = parser.extract_appointment_info(test_text)
    
    # Current date for reference
    now = datetime.now()
    print(f"Today: {now.strftime('%A, %d/%m/%Y')}")
    print()
    
    print("Result:")
    print(f"  นัดหมาย: {result.get('appointment_title')}")
    print(f"  วันที่: {result.get('date')}")
    print(f"  เวลา: {result.get('time')}")
    print(f"  สถานที่: {result.get('location')}")
    print(f"  ผู้ติดต่อ: {result.get('contact_person')}")
    print(f"  Confidence: {result.get('confidence')}")
    
    # Expected vs actual
    print("\nValidation:")
    expected_date = "09/10/2025"  # Next Thursday
    actual_date = result.get('date')
    print(f"  Date: Expected {expected_date}, Got {actual_date} {'✅' if actual_date == expected_date else '❌'}")
    
    expected_time = "16.00"  # 4 PM  
    actual_time = result.get('time')
    print(f"  Time: Expected {expected_time}, Got {actual_time} {'✅' if actual_time == expected_time else '❌'}")
    
    expected_location = "เซ็นทรัลลาดพร้าว"
    actual_location = result.get('location')
    print(f"  Location: Expected {expected_location}, Got {actual_location} {'✅' if actual_location == expected_location else '❌'}")

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")