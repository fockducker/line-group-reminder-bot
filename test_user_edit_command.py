#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ทดสอบคำสั่งแก้ไขนัดที่ผู้ใช้ส่งมา
"""

from handlers import handle_edit_appointment_command

def test_user_command():
    """ทดสอบคำสั่งของผู้ใช้"""
    
    print("=== ทดสอบคำสั่งแก้ไขนัดของผู้ใช้ ===")
    
    # คำสั่งที่ผู้ใช้ส่งมา
    user_command = 'แก้นัด 334400b9 นัดหมาย:"เวลาขึ้นเครื่องบิน(ไปงานแต่งไอจุง)"'
    
    print(f"คำสั่ง: {user_command}")
    print("\n" + "="*60)
    
    # ทดสอบการทำงาน
    result = handle_edit_appointment_command(user_command, "test_user", "private", "private_123")
    print("ผลลัพธ์:")
    print(result)
    
    print("\n" + "="*60)
    print("การวิเคราะห์:")
    
    # ตรวจสอบ regex pattern
    import re
    pattern = r'(?:แก้ไขนัด|แก้นัด|แก้ไขการนัด)\s+([A-Za-z0-9]+)\s*(.*)'
    match = re.search(pattern, user_command, re.IGNORECASE | re.DOTALL)
    
    if match:
        appointment_id = match.group(1).strip()
        update_fields_text = match.group(2).strip()
        print(f"✅ Regex match สำเร็จ:")
        print(f"   - Appointment ID: '{appointment_id}'")
        print(f"   - Fields text: '{update_fields_text}'")
        
        # ทดสอบ field pattern
        field_pattern = r'(?:นัดหมาย|ชื่อนัดหมาย):\s*["\']([^"\']+)["\']'
        field_match = re.search(field_pattern, update_fields_text, re.IGNORECASE)
        
        if field_match:
            print(f"✅ Field pattern match สำเร็จ:")
            print(f"   - Title value: '{field_match.group(1)}'")
        else:
            print(f"❌ Field pattern ไม่ match:")
            print(f"   - Pattern: {field_pattern}")
            print(f"   - Text: {update_fields_text}")
    else:
        print(f"❌ Regex ไม่ match:")
        print(f"   - Pattern: {pattern}")
        print(f"   - Text: {user_command}")

if __name__ == "__main__":
    test_user_command()