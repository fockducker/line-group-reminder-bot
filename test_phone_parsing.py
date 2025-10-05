"""
ทดสอบการ parse phone number ใน structured format
"""

from utils.datetime_parser import SmartDateTimeParser

def test_phone_number_parsing():
    """ทดสอบการ parse phone number"""
    
    parser = SmartDateTimeParser()
    
    # ข้อความที่ผู้ใช้ส่งมา
    test_message = '''เพิ่มนัด
ชื่อนัดหมาย: "ปรึกษาตรวจฟัน"
วันเวลา: "8 ตุลาคม 2025 14:00"
บุคคล/ผู้ติดต่อ: "ทพญ. ปารัช"
สถานที่: "ศิริราช"
อาคาร/แผนก/ชั้น: "ทันตกรรม"
เบอร์โทร: "02-419-7000"'''

    print("Testing phone number parsing...")
    print("=" * 50)
    print(f"Input message:\n{test_message}")
    print("=" * 50)
    
    # ทดสอบ extract_appointment_info
    result = parser.extract_appointment_info(test_message)
    
    print("Parsing result:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    print("=" * 50)
    
    # ทดสอบ pattern เบอร์โทรโดยตรง
    phone_pattern = r'(?:เบอร์โทร|โทรศัพท์):\s*["\']?([^"\'\r\n]+)["\']?'
    import re
    
    match = re.search(phone_pattern, test_message)
    if match:
        print(f"Phone pattern match: '{match.group(1)}'")
    else:
        print("Phone pattern NOT matched")
    
    # ทดสอบ pattern อื่น ๆ
    patterns_to_test = [
        ('ชื่อนัดหมาย', r'ชื่อนัดหมาย:\s*["\']?([^"\'\r\n]+)["\']?'),
        ('วันเวลา', r'วันเวลา:\s*["\']?([^"\'\r\n]+)["\']?'),
        ('บุคคล/ผู้ติดต่อ', r'(?:แพทย์|บุคคล|ผู้ติดต่อ):\s*["\']?([^"\'\r\n]+)["\']?'),
        ('สถานที่', r'(?:โรงพยาบาล|สถานที่):\s*["\']?([^"\'\r\n]+)["\']?'),
        ('อาคาร/แผนก/ชั้น', r'(?:แผนก|อาคาร|ชั้น):\s*["\']?([^"\'\r\n]+)["\']?'),
        ('เบอร์โทร', r'(?:เบอร์โทร|โทรศัพท์):\s*["\']?([^"\'\r\n]+)["\']?')
    ]
    
    print("\nPattern testing:")
    for name, pattern in patterns_to_test:
        match = re.search(pattern, test_message)
        if match:
            print(f"✅ {name}: '{match.group(1)}'")
        else:
            print(f"❌ {name}: NOT MATCHED")

if __name__ == "__main__":
    test_phone_number_parsing()