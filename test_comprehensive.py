#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Enhanced Parser Test
ทดสอบ Enhanced Parser กับตัวอย่างที่หลากหลาย
"""

import sys
import os
import json
from datetime import datetime

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

try:
    from enhanced_smart_parser import EnhancedSmartDateTimeParser
    
    def test_comprehensive_cases():
        """ทดสอบกับตัวอย่างตามข้อกำหนด"""
        
        parser = EnhancedSmartDateTimeParser()
        
        test_cases = [
            # Original test case
            {
                'input': 'เพิ่มนัด กินข้าวเที่ยวกับที่รักบ่าย3โมง',
                'expected': {
                    'title': 'กินข้าวเที่ยว',
                    'time': '15.00',
                    'person': 'ที่รัก'
                }
            },
            
            # Date variations
            {
                'input': 'นัดหมาย ประชุมคณะกรรมการ วันจันทร์หน้า 10 นาฬิกา',
                'expected': {
                    'title': 'ประชุมคณะกรรมการ',
                    'time': '10.00'
                }
            },
            
            # Medical appointment
            {
                'input': 'ตั้งนัด ไปหาหมอสมชาย โรงพยาบาลศิริราช พรุ่งนี้ 14.30 น.',
                'expected': {
                    'title': 'ไปหาหมอสมชาย',
                    'time': '14.30',
                    'location': 'โรงพยาบาลศิริราช'
                }
            },
            
            # Time variations
            {
                'input': 'เพิ่มนัด เจอกับลูกค้า ที่ออฟฟิศ บ่ายสองครึ่ง',
                'expected': {
                    'title': 'เจอกับลูกค้า',
                    'time': '14.30',
                    'person': 'ลูกค้า',
                    'location': 'ออฟฟิศ'
                }
            },
            
            # Evening time
            {
                'input': 'นัดกินข้าวกับเพื่อน ห้างสยามพารากอน 6 โมงเย็น',
                'expected': {
                    'title': 'กินข้าวกับเพื่อน',
                    'time': '18.00',
                    'person': 'เพื่อน',
                    'location': 'ห้างสยามพารากอน'
                }
            },
            
            # Thai numerals
            {
                'input': 'เพิ่มนัด พบหมอใหญ่ รพ.จุฬา วันที่ ๑๕ เวลา ๑๔.๓๐ น.',
                'expected': {
                    'title': 'พบหมอใหญ่',
                    'time': '14.30',
                    'location': 'โรงพยาบาลจุฬาลงกรณ์'
                }
            },
            
            # Night time (ทุ่ม)
            {
                'input': 'นัดดูหนัง สามทุ่มครึ่ง ห้างเซ็นทรัล',
                'expected': {
                    'title': 'ดูหนัง',
                    'time': '21.30',
                    'location': 'ห้างสรรพสินค้าเซ็นทรัล'
                }
            }
        ]
        
        print("🧪 Comprehensive Enhanced Parser Test")
        print("=" * 70)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test Case {i}: {test_case['input']}")
            print("-" * 50)
            
            try:
                result = parser.extract_appointment_info(test_case['input'])
                
                # Display results
                print("📊 Results:")
                actual_results = {
                    'title': result.get('appointment_title', ''),
                    'date': result.get('date', ''),
                    'time': result.get('time', ''),
                    'location': result.get('location', ''),
                    'person': result.get('contact_person', ''),
                    'phone': result.get('phone_number', ''),
                    'confidence': result.get('confidence', 0)
                }
                
                for key, value in actual_results.items():
                    if value:
                        print(f"  {key}: '{value}'")
                
                # Check expectations
                expected = test_case['expected']
                print("\n✅ Validation:")
                
                all_passed = True
                for exp_key, exp_value in expected.items():
                    actual_value = actual_results.get(exp_key, '')
                    
                    if exp_key == 'title':
                        # For title, check if expected is contained in actual
                        passed = exp_value.lower() in actual_value.lower() if actual_value else False
                    else:
                        passed = exp_value == actual_value
                    
                    status = "✅" if passed else "❌"
                    print(f"  {status} {exp_key}: expected '{exp_value}', got '{actual_value}'")
                    
                    if not passed:
                        all_passed = False
                
                print(f"\n🎯 Overall: {'✅ PASS' if all_passed else '❌ FAIL'}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "=" * 70)
        print("✅ Test completed!")
    
    def test_edge_cases():
        """ทดสอบ edge cases"""
        
        parser = EnhancedSmartDateTimeParser()
        
        edge_cases = [
            "เพิ่มนัด",  # No details
            "กินข้าว",   # No time
            "บ่าย 3 โมง", # Time only
            "พรุ่งนี้",   # Date only
            "เพิ่มนัด กินข้าว พรุ่งนี้ ๒๓.๕๙ น.",  # Late night
            "นัด DMK สนามบิน เช้า",  # Airport abbreviation
        ]
        
        print("\n🔧 Edge Cases Test")
        print("=" * 40)
        
        for i, test_input in enumerate(edge_cases, 1):
            print(f"\n{i}. Input: '{test_input}'")
            
            try:
                result = parser.extract_appointment_info(test_input)
                confidence = result.get('confidence', 0)
                print(f"   Confidence: {confidence:.2f}")
                
                # Show non-empty fields
                for field in ['appointment_title', 'date', 'time', 'location', 'contact_person']:
                    value = result.get(field, '')
                    if value:
                        print(f"   {field}: '{value}'")
                        
            except Exception as e:
                print(f"   Error: {e}")
    
    if __name__ == "__main__":
        test_comprehensive_cases()
        test_edge_cases()
        
        print(f"\n💡 To test GUI: run 'python simple_gui.py'")
        
except ImportError as e:
    print(f"❌ Cannot import Enhanced Parser: {e}")
    print("Make sure enhanced_smart_parser.py is in utils/ directory")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

input("\nPress Enter to exit...")