from utils.enhanced_smart_parser import EnhancedSmartDateTimeParser

parser = EnhancedSmartDateTimeParser()

cases = [
    "เพิ่มนัด ประชุมทีม พรุ่งนี้ 10:00 at CentralWorld",
    "เพิ่มนัด พบหมอ ศุกร์หน้า 9:30 at Bangkok Hospital",
    "เพิ่มนัด ไปเดินเล่น 24 ตุลาคม in Siam Paragon",
    "เพิ่มนัด ทานข้าว 5 พ.ย. 18:00 at ICONSIAM กับเมย์",
    "เพิ่มนัด นัดคุยโปรเจค 12/10/2025 at Samitivej Hospital",
    "เพิ่มนัด ดูหนัง เสาร์นี้ at Terminal 21",
]

for c in cases:
    info = parser.extract_appointment_info(c)
    print('\n', c)
    print('  -> date:', info.get('date'), 'time:', info.get('time'))
    print('  -> location:', info.get('location'))
    print('  -> title:', info.get('appointment_title'))
    print('  -> raw location matches:', info['processed_data']['location_matches'])
