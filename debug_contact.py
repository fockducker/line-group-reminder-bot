#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug contact extraction patterns
"""

import re

def debug_contact_extraction():
    text = "กินข้าวกับเพื่อนศุกร์ มุ่งที่โอคอนคอนยามกับน้องบี"
    
    print(f"Debug Contact Extraction")
    print("=" * 50)
    print(f"Text: {text}")
    print()
    
    # Test the multi-contact pattern
    multi_contact_pattern = r'กับ([^กับวันพฤศุจอเส\d]+?)(?=กับ|วัน|พฤ|ศุ|จ|อ|เส|\d|$)'
    matches = re.findall(multi_contact_pattern, text)
    
    print(f"Multi-contact pattern: {multi_contact_pattern}")
    print(f"Matches: {matches}")
    print()
    
    # Test individual patterns
    patterns = [
        r'กับ([^วันพฤศุจอเส]+?)(?:วัน|พฤ|ศุ|จ|อ|เส|\d|$)',
        r'กับ([^บ่ายเช้าเย็นค่ำ\d]+?)(?:บ่าย|เช้า|เย็น|ค่ำ|\d|$)',
        r'กับ([^ที่ใน]+?)(?:ที่|ใน|$)',
        r'กับ(\S+?)(?:\s|$)',
    ]
    
    for i, pattern in enumerate(patterns, 1):
        print(f"Pattern {i}: {pattern}")
        matches = re.findall(pattern, text)
        print(f"Matches: {matches}")
        
        # Try finditer for more detail
        for match in re.finditer(pattern, text):
            print(f"  Match: '{match.group(1)}' at position {match.start()}-{match.end()}")
        print()

if __name__ == "__main__":
    debug_contact_extraction()
    input("Press Enter to exit...")