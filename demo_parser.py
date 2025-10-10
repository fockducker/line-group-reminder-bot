#!/usr/bin/env python3
# Quick demo of the Enhanced Parser results

import json
from datetime import datetime

def demo_parser():
    """Demo the Enhanced Parser functionality"""
    
    # Test cases
    test_cases = [
        "เพิ่มนัด กินข้าวเที่ยวกับที่รักบ่าย3โมง",
        "นัดหมาย ประชุมคณะกรรมการ พรุ่งนี้ 10 นาฬิกา",
        "ตั้งนัด ไปหาหมอสมชาย โรงพยาบาลศิริราช วันนี้ 14.30 น.",
        "เพิ่มนัด เจอกับลูกค้า ที่ออฟฟิศ ชั้น 5 บ่าย 2 โมง"
    ]
    
    print("🤖 Enhanced Smart Parser Demo")
    print("=" * 60)
    print()
    
    # Try to import the real parser
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
        from enhanced_smart_parser import EnhancedSmartDateTimeParser
        
        parser = EnhancedSmartDateTimeParser()
        print("✅ Using real Enhanced Parser")
        
        for i, test_text in enumerate(test_cases, 1):
            print(f"\n📝 Test Case {i}: {test_text}")
            print("-" * 50)
            
            result = parser.extract_appointment_info(test_text)
            
            # Display clean results
            fields = [
                ('นัดหมาย', result.get('appointment_title', '')),
                ('วันที่', result.get('date', '')),
                ('เวลา', result.get('time', '')),
                ('สถานที่', result.get('location', '')),
                ('บุคคล/ผู้ติดต่อ', result.get('contact_person', '')),
                ('เบอร์โทร', result.get('phone_number', '')),
            ]
            
            for field_name, field_value in fields:
                if field_value:
                    print(f"  {field_name}: '{field_value}'")
            
            print(f"  Confidence: {result.get('confidence', 0):.2f}")
            
            # JSON for the first test case (your example)
            if i == 1:
                print("\n📄 JSON Output:")
                clean_result = {k: v for k, v in {
                    'appointment_title': result.get('appointment_title', ''),
                    'date': result.get('date', ''),
                    'time': result.get('time', ''),
                    'location': result.get('location', ''),
                    'building_dept': result.get('building_dept', ''),
                    'contact_person': result.get('contact_person', ''),
                    'phone_number': result.get('phone_number', ''),
                }.items() if v}
                
                print(json.dumps(clean_result, ensure_ascii=False, indent=2))
        
    except ImportError as e:
        print(f"❌ Cannot import Enhanced Parser: {e}")
        print("🔧 Make sure enhanced_smart_parser.py is in utils/ directory")
    
    print("\n" + "=" * 60)
    print("✅ Demo completed!")
    print("💡 To run the GUI version:")
    print("   - Double-click 'RUN_GUI.py' or 'CLICK_TO_RUN.bat'")
    print("   - Or run: python simple_gui.py")

if __name__ == "__main__":
    demo_parser()
    input("\nPress Enter to exit...")