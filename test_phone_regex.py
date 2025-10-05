#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def test_phone_regex():
    """ทดสอบ regex pattern สำหรับ phone_number"""
    
    test_text = """นัดหมาย: ตรวจสุขภาพประจำปี
วันที่: 15 ธันวาคม 2567
เวลา: 10:00
สถานที่: โรงพยาบาลบำรุงราษฎร์
อาคาร/แผนก/ชั้น: อาคาร A ชั้น 3 แผนกอายุรกรรม
บุคคล/ผู้ติดต่อ: นพ.สมชาย ใจดี
เบอร์โทร: "02-419-7000"
"""

    print("=== ทดสอบ Phone Number Regex ===")
    print(f"ข้อความทดสอบ:\n{test_text}")
    print("\n" + "="*50)
    
    # Pattern เดิมจาก parser
    original_pattern = r'(?:เบอร์โทร|โทรศัพท์):\s*["\']?([^"\'\r\n]+)["\']?'
    
    print("1. Pattern เดิม:")
    print(f"   {original_pattern}")
    
    match = re.search(original_pattern, test_text)
    if match:
        print(f"   ✅ พบ match: '{match.group(1)}'")
    else:
        print(f"   ❌ ไม่พบ match")
    
    # ลองหา pattern อื่น ๆ
    patterns_to_test = [
        r'เบอร์โทร:\s*"([^"]+)"',  # เฉพาะเจาะจง: เบอร์โทร: "..."
        r'เบอร์โทร:\s*["\']?([^\r\n"\']+)["\']?',  # ปรับลำดับ character class
        r'เบอร์โทร:\s*"?([^"\r\n]+)"?',  # ลดความซับซ้อน
        r'เบอร์โทร:\s*(.+)',  # ง่าย ๆ เลย
    ]
    
    print("\n2. ทดสอบ Pattern อื่น ๆ:")
    for i, pattern in enumerate(patterns_to_test, 1):
        print(f"   Pattern {i}: {pattern}")
        match = re.search(pattern, test_text)
        if match:
            print(f"   ✅ พบ match: '{match.group(1).strip()}'")
        else:
            print(f"   ❌ ไม่พบ match")
        print()
    
    # ตรวจสอบข้อความในรูปแบบอื่น
    simple_text = 'เบอร์โทร: "02-419-7000"'
    print(f"3. ทดสอบข้อความง่าย ๆ: '{simple_text}'")
    match = re.search(original_pattern, simple_text)
    if match:
        print(f"   ✅ พบ match: '{match.group(1)}'")
    else:
        print(f"   ❌ ไม่พบ match")

if __name__ == "__main__":
    test_phone_regex()