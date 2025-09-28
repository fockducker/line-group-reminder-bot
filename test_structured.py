#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.datetime_parser import SmartDateTimeParser

def test_structured_format():
    parser = SmartDateTimeParser()
    
    # ทดสอบ structured format
    structured_text = '''ชื่อนัดหมาย: "ปรึกษาตรวจฟัน"
วันเวลา: "8 ตุลาคม 2025 14:00"
แพทย์: "ทพญ. ปารัช ศิริวิชยกุล"
โรงพยาบาล: "ศิริราชปิยะการุณย์"
แผนก: "คลินิกทันตกรรม"'''
    
    print("Testing structured format:")
    print(structured_text)
    print()
    
    # ทดสอบ extract_appointment_info
    result = parser.extract_appointment_info("เพิ่มนัด " + structured_text)
    
    print("Structured result:")
    if result and result['datetime']:
        print(f"✅ SUCCESS!")
        print(f"Date: {result['datetime']}")
        print(f"Title: {result['title']}")
        print(f"Doctor: {result['doctor']}")
        print(f"Hospital: {result['hospital']}")
        print(f"Department: {result['department']}")
        
        # ตรวจสอบค่าที่ควรจะได้
        expected_values = {
            'title': 'ปรึกษาตรวจฟัน',
            'doctor': 'ทพญ. ปารัช ศิริวิชยกุล', 
            'hospital': 'ศิริราชปิยะการุณย์',
            'department': 'คลินิกทันตกรรม'
        }
        
        print("\nValidation:")
        all_correct = True
        for field, expected in expected_values.items():
            actual = result[field]
            is_correct = actual == expected
            print(f"{field}: {actual} {'✅' if is_correct else '❌'}")
            if not is_correct:
                print(f"  Expected: {expected}")
                all_correct = False
        
        print(f"\nOverall: {'✅ All correct!' if all_correct else '❌ Some errors'}")
    else:
        print("❌ FAILED: No result or invalid datetime")
        print(f"Result: {result}")

if __name__ == "__main__":
    test_structured_format()