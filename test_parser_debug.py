from utils.datetime_parser import SmartDateTimeParser

# ใช้ input format เดียวกับที่ user ใช้
test_input = """เพิ่มนัด 
ชื่อนัดหมาย: "ปรึกษาตรวจฟัน"
วันเวลา: "8 ตุลาคม 2025 14:00"
แพทย์: "ทพญ. ปารัช"
โรงพยาบาล: "ศิริราช"
แผนก: "ทันตกรรม" """

parser = SmartDateTimeParser()
print("Testing parser with user input:")
print(f"Input: {repr(test_input)}")
print()

result = parser.extract_appointment_info(test_input)
print('Parser Result:')
for key, value in result.items():
    print(f'  {key}: {value}')