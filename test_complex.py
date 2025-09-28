#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.datetime_parser import SmartDateTimeParser

def test_complex_only():
    parser = SmartDateTimeParser()
    
    # ทดสอบข้อความใหม่
    text = "วันที่ 8 ตุลาคม 2025 เวลา 14.00 โรงพยาบาล ศิริราชปิยะการุณย์  แผนก คลินิกทันตกรรม ปรึกษาตรวจฟัน พบ ทพญ. ปารัช ศิริวิชยกุล"
    
    print("Testing new complex text:")
    print(text)
    
    # ลองเรียก method โดยตรง
    result = parser._parse_complex_appointment(text)
    
    print("\nComplex result:")
    print(result)
    
    if result:
        print("\nSUCCESS! Complex pattern worked")
        print(f"Date: {result['datetime']}")
        print(f"Hospital: {result['hospital']}")
        print(f"Department: {result['department']}")
        print(f"Title: {result['title']}")
        print(f"Doctor: {result['doctor']}")
        
        # ตรวจสอบค่าที่ควรจะได้
        expected_dept = "คลินิกทันตกรรม"
        expected_title = "ปรึกษาตรวจฟัน"
        
        print(f"\nExpected Department: {expected_dept}")
        print(f"Actual Department: {result['department']}")
        print(f"Department correct: {result['department'] == expected_dept}")
        
        print(f"\nExpected Title: {expected_title}")
        print(f"Actual Title: {result['title']}")
        print(f"Title correct: {result['title'] == expected_title}")
        
    else:
        print("FAILED: Complex pattern returned None")
        
    # ทดสอบ extract_appointment_info 
    full_result = parser.extract_appointment_info("เพิ่มนัด " + text)
    print("\nFull extract result:")
    print(full_result)

if __name__ == "__main__":
    test_complex_only()