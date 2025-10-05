#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ทดสอบการแสดงคำสั่งใหม่ใน handlers.py
"""

from handlers import handle_add_appointment_command

def test_help_commands():
    """ทดสอบการแสดงคำสั่งใหม่"""
    
    print("=== ทดสอบการแสดงคำสั่งใหม่ ===")
    
    # ทดสอบคำสั่ง "เพิ่มนัด" เปล่า ๆ
    print("\n1. คำสั่ง 'เพิ่มนัด' เปล่า ๆ:")
    add_response = handle_add_appointment_command("เพิ่มนัด", "test_user", "private", "private_123")
    print(add_response)
    
    print("\n" + "="*60)
    
    # ตรวจสอบว่า format ใหม่ถูกแสดงหรือไม่
    print("\n2. ตรวจสอบว่ามี 'เบอร์โทร:' ใน help message:")
        
    if "เบอร์โทร:" in add_response:
        print("✅ พบ 'เบอร์โทร:' ใน add appointment message")
    else:
        print("❌ ไม่พบ 'เบอร์โทร:' ใน add appointment message")
    
    # ตรวจสอบรูปแบบใหม่
    print("\n3. ตรวจสอบรูปแบบใหม่:")
    new_format_checks = [
        ("นัดหมาย:", "ใช้ 'นัดหมาย:' แทน 'ชื่อนัดหมาย:'"),
        ("วันที่:", "ใช้ 'วันที่:' แยกจาก 'เวลา:'"),
        ("เวลา:", "ใช้ 'เวลา:' แยกจาก 'วันที่:'"),
        ("อาคาร/แผนก/ชั้น:", "ใช้ 'อาคาร/แผนก/ชั้น:' แทน 'แผนก:'"),
        ("บุคคล/ผู้ติดต่อ:", "ใช้ 'บุคคล/ผู้ติดต่อ:' แทน 'แพทย์:'"),
        ("เบอร์โทร:", "เพิ่ม field ใหม่ 'เบอร์โทร:'")
    ]
    
    for field, description in new_format_checks:
        if field in add_response:
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ {description}")
            
    # แสดงข้อความเต็ม ๆ เพื่อตรวจสอบ
    print(f"\n4. ข้อความเต็ม:")
    print(f"'{add_response}'")

if __name__ == "__main__":
    test_help_commands()