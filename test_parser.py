#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.datetime_parser import SmartDateTimeParser
from datetime import datetime
import pytz

def test_parser():
    # ข้อความทดสอบ
    text = "เพิ่มนัด วันที่ 1 ตุลาคม 2025 เวลา 13.00 โรงพยาบาล ศิริราชปิยะการุณย์  แผนก กุมารเวชกรรม นัดติดตามพัฒนาการ พบ พญ. เนตรวิมล นันทิวัฒน์"
    
    # สร้าง parser
    parser = SmartDateTimeParser()
    
    # ทดสอบการแยกข้อมูล
    result = parser.extract_appointment_info(text)
    
    print("=== ผลการประมวลผล ===")
    print(f"วันที่และเวลา: {result['datetime']}")
    print(f"โรงพยาบาล: {result['hospital']}")
    print(f"แผนก: {result['department']}")
    print(f"หัวข้อ: {result['title']}")
    print(f"สถานที่: {result['location']}")
    print(f"หมอ: {result['doctor']}")
    
    print("\n=== รายละเอียดเพิ่มเติม ===")
    if result['datetime']:
        dt = result['datetime']
        print(f"วันที่แบบ ISO: {dt.isoformat()}")
        print(f"วันที่แบบไทย: {dt.strftime('%d/%m/%Y')}")
        print(f"เวลา: {dt.strftime('%H:%M')}")
        print(f"วัน: {dt.strftime('%A')}")
    
    # แสดงข้อความที่ Bot จะตอบกลับ
    print("\n=== ข้อความที่ Bot จะตอบกลับ ===")
    if result['datetime']:
        location_info = f"{result['doctor']}"
        if result['location'] and result['location'] != "ไม่ระบุ":
            location_info += f" | {result['location']}"
        elif result['doctor'] == "ไม่ระบุ":
            location_info = result['location'] if result['location'] else "ไม่ระบุ"
            
        response = f"""✅ เพิ่มการนัดหมายเรียบร้อยแล้ว!

📅 วันที่: {result['datetime'].strftime('%d/%m/%Y')} ({result['datetime'].strftime('%A')})
⏰ เวลา: {result['datetime'].strftime('%H:%M')} น.
🏥 โรงพยาบาล: {result['hospital']}
🏢 แผนก: {result['department']}
📝 หัวข้อ: {result['title']}
👨‍⚕️ หมอ: {result['doctor']}
📍 สถานที่: {location_info}

🔔 จะแจ้งเตือนให้ล่วงหน้า 7 วัน และ 1 วัน"""
        print(response)

if __name__ == "__main__":
    test_parser()