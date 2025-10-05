#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def test_month_pattern():
    print("🔧 ทดสอบ Pattern สำหรับเดือนเฉพาะ")
    
    # Pattern ใหม่ที่ระบุชื่อเดือนเฉพาะ
    specific_month_pattern = r'(?:ย้อนหลัง|ดูย้อนหลัง)\s+(มกราคม|กุมภาพันธ์|มีนาคม|เมษายน|พฤษภาคม|มิถุนายน|กรกฎาคม|สิงหาคม|กันยายน|ตุลาคม|พฤศจิกายน|ธันวาคม)\s+(\d{4})'
    
    test_cases = [
        "ย้อนหลัง ตุลาคม 2025",
        "ดูย้อนหลัง กันยายน 2025", 
        "ย้อนหลัง มีนาคม 2024",
        "ดูย้อนหลัง สิงหาคม 2025"
    ]
    
    for test in test_cases:
        print(f"\n📝 Testing: '{test}'")
        match = re.search(specific_month_pattern, test.lower())
        if match:
            print(f"   ✅ Matched: เดือน='{match.group(1)}' ปี='{match.group(2)}'")
        else:
            print(f"   ❌ Not matched")
            # ลอง pattern อื่น
            simple_pattern = r'([ก-ฮ]+)\s+(\d{4})'
            simple_match = re.search(simple_pattern, test)
            if simple_match:
                print(f"   🔍 Simple pattern works: '{simple_match.group(1)}' '{simple_match.group(2)}'")
    
    # ทดสอบ Thai months mapping
    thai_months = {
        'มกราคม': 1, 'กุมภาพันธ์': 2, 'มีนาคม': 3, 'เมษายน': 4,
        'พฤษภาคม': 5, 'มิถุนายน': 6, 'กรกฎาคม': 7, 'สิงหาคม': 8,
        'กันยายน': 9, 'ตุลาคม': 10, 'พฤศจิกายน': 11, 'ธันวาคม': 12
    }
    
    print(f"\n📅 Thai months mapping test:")
    for month in ['ตุลาคม', 'กันยายน', 'มีนาคม', 'สิงหาคม']:
        month_num = thai_months.get(month)
        print(f"   {month} → {month_num}")

if __name__ == "__main__":
    test_month_pattern()