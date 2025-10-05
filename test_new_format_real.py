#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ทดสอบการทำงานจริงด้วยรูปแบบใหม่ที่แสดงใน help
"""

from handlers import handle_add_appointment_command

def test_new_format():
    """ทดสอบการทำงานจริงด้วยรูปแบบใหม่"""
    
    print("=== ทดสอบรูปแบบใหม่จาก Help Message ===")
    
    # ทดสอบรูปแบบใหม่ที่แสดงใน help
    new_format_message = """เพิ่มนัด
นัดหมาย: "ตรวจสุขภาพประจำปี"
วันที่: "15 มกราคม 2025"
เวลา: "09:00"
สถานที่: "โรงพยาบาลราชวิถี"
อาคาร/แผนก/ชั้น: "อาคาร 1 ชั้น 2 แผนกอายุรกรรม"
บุคคล/ผู้ติดต่อ: "นพ.สมชาย ใจดี"
เบอร์โทร: "02-354-7000"
"""
    
    print("รูปแบบที่ทดสอบ:")
    print(new_format_message)
    print("\n" + "="*60)
    
    # ทดสอบการทำงาน
    print("ผลลัพธ์:")
    result = handle_add_appointment_command(new_format_message, "test_user", "private", "private_123")
    print(result)
    
    # ตรวจสอบผลลัพธ์
    print("\n" + "="*60)
    print("การวิเคราะห์ผลลัพธ์:")
    
    if "✅" in result and "บันทึกสำเร็จ" in result:
        print("✅ การบันทึกสำเร็จ!")
        
        # ตรวจสอบว่ามีข้อมูล phone_number ใน result หรือไม่
        if "02-354-7000" in result:
            print("✅ Phone number ถูกแสดงในผลลัพธ์")
        else:
            print("❓ Phone number ไม่ปรากฏในผลลัพธ์ (อาจเป็นเรื่องปกติ)")
            
    elif "❌" in result:
        print("❌ การบันทึกล้มเหลว:")
        print(f"   สาเหตุ: {result}")
        
    else:
        print("❓ ผลลัพธ์ไม่แน่ชัด:")
        print(f"   {result}")

if __name__ == "__main__":
    test_new_format()