from utils.enhanced_smart_parser import EnhancedSmartDateTimeParser

parser = EnhancedSmartDateTimeParser()

tests = [
    "เพิ่มนัด กินข้าว 24 ตุลาคม",
    "เพิ่มนัด ประชุมทีม 24 ต.ค. 15:30",
    "เพิ่มนัด ผ่าตัด 5 กุมภาพันธ์ 2569 09:00",
    "เพิ่มนัด พบหมอ 1 ม.ค. 26",
]

for t in tests:
    info = parser.extract_appointment_info(t)
    print(t, '-> date:', info.get('date'), 'time:', info.get('time'), 'raw date_matches:', [m for m in info['processed_data']['date_matches']])
