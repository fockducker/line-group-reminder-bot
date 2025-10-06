#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ทดสอบฟังก์ชันแก้ไขนัดหมายที่อัปเดตแล้ว
"""

from handlers import handle_edit_appointment_command

def test_edit_help_messages():
    """ทดสอบ help messages ของฟังก์ชันแก้ไขนัด"""
    
    print("=== ทดสอบ Help Messages สำหรับแก้ไขนัด ===")
    
    # ทดสอบ error message เมื่อไม่มีรูปแบบที่ถูกต้อง
    print("\n1. ทดสอบ error message เมื่อไม่มี appointment ID:")
    result1 = handle_edit_appointment_command("แก้ไขนัด", "test_user", "private", "private_123")
    print(result1)
    
    print("\n" + "="*60)
    
    # ทดสอบ error message เมื่อไม่มีข้อมูลที่ต้องการแก้ไข
    print("\n2. ทดสอบ error message เมื่อไม่มีข้อมูลที่แก้ไข:")
    result2 = handle_edit_appointment_command("แก้ไขนัด ABC123", "test_user", "private", "private_123")
    print(result2)
    
    # ตรวจสอบว่ามีข้อความรูปแบบใหม่หรือไม่
    print("\n" + "="*60)
    print("\n3. ตรวจสอบรูปแบบใหม่ใน help messages:")
    
    new_format_checks = [
        ("นัดหมาย:", "ใช้ 'นัดหมาย:' แทน 'ชื่อนัดหมาย:'"),
        ("วันที่:", "ใช้ 'วันที่:' แยกจาก 'เวลา:'"),
        ("เวลา:", "ใช้ 'เวลา:' แยกจาก 'วันที่:'"),
        ("สถานที่:", "ใช้ 'สถานที่:' แทน 'โรงพยาบาล:'"),
        ("อาคาร/แผนก/ชั้น:", "ใช้ 'อาคาร/แผนก/ชั้น:' แทน 'แผนก:'"),
        ("บุคคล/ผู้ติดต่อ:", "ใช้ 'บุคคล/ผู้ติดต่อ:' แทน 'แพทย์:'"),
        ("เบอร์โทร:", "เพิ่ม field ใหม่ 'เบอร์โทร:'")
    ]
    
    combined_results = result1 + "\n" + result2
    
    for field, description in new_format_checks:
        if field in combined_results:
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ {description}")
    
    print("\n" + "="*60)
    print("\n4. ข้อความ help แบบเต็ม:")
    print("--- Result 1 (ไม่มี ID) ---")
    print(result1)
    print("\n--- Result 2 (ไม่มีข้อมูลแก้ไข) ---")
    print(result2)

def test_edit_format_examples():
    """ทดสอบตัวอย่างรูปแบบการแก้ไข"""
    
    print("\n=== ตัวอย่างรูปแบบการใช้งานแก้ไขนัด ===")
    
    examples = [
        "แก้ไขนัด ABC123 นัดหมาย:\"ตรวจสุขภาพใหม่\"",
        "แก้ไขนัด ABC123 วันที่:\"10 ตุลาคม 2025\"",
        "แก้ไขนัด ABC123 เวลา:\"15:30\"",
        "แก้ไขนัด ABC123 สถานที่:\"โรงพยาบาลจุฬา\"",
        "แก้ไขนัด ABC123 เบอร์โทร:\"02-256-4000\"",
        """แก้ไขนัด ABC123
นัดหมาย:"ตรวจสุขภาพประจำปี"
วันที่:"15 ตุลาคม 2025"
เวลา:"09:00"
สถานที่:"โรงพยาบาลศิริราช"
เบอร์โทร:"02-419-7000"
"""
    ]
    
    print("รูปแบบที่รองรับ:")
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example}")
    
    print("\n💡 สังเกต: ระบบรองรับ 'วันที่:' และ 'เวลา:' แยกกัน หรือ 'วันเวลา:' รวมกัน")
    print("📞 เพิ่มเติม: เพิ่มฟิลด์ 'เบอร์โทร:' ใหม่สำหรับข้อมูลติดต่อ")

if __name__ == "__main__":
    test_edit_help_messages()
    test_edit_format_examples()