#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.datetime_parser import SmartDateTimeParser

def test_complex_only():
    parser = SmartDateTimeParser()
    
    # ทดสอบเฉพาะ complex pattern
    text = "วันที่ 1 ตุลาคม 2025 เวลา 13.00 โรงพยาบาล ศิริราชปิยะการุณย์  แผนก กุมารเวชกรรม นัดติดตามพัฒนาการ พบ พญ. เนตรวิมล นันทิวัฒน์"
    
    print("Testing complex text:", text)
    
    # ลองเรียก method โดยตรง
    result = parser._parse_complex_appointment(text)
    
    print("Complex result:", result)
    
    if result:
        print("SUCCESS! Complex pattern worked")
        print(f"Date: {result['datetime']}")
        print(f"Hospital: {result['hospital']}")
        print(f"Department: {result['department']}")
        print(f"Title: {result['title']}")
        print(f"Doctor: {result['doctor']}")
    else:
        print("FAILED: Complex pattern returned None")
        
    # ทดสอบ extract_appointment_info 
    full_result = parser.extract_appointment_info("เพิ่มนัด " + text)
    print("\nFull extract result:", full_result)

if __name__ == "__main__":
    test_complex_only()