"""
Smart Date and Time Parser for LINE Group Reminder Bot
แยกวิเคราะห์วันที่และเวลาจากข้อความธรรมดาในภาษาไทย
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any
import pytz

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ตั้งค่า timezone สำหรับประเทศไทย
BANGKOK_TZ = pytz.timezone('Asia/Bangkok')


class SmartDateTimeParser:
    """
    Parser สำหรับแยกวิเคราะห์วันที่และเวลาจากข้อความภาษาไทย
    รองรับรูปแบบที่หลากหลาย
    """
    
    def __init__(self):
        """Initialize parser with regex patterns and mappings"""
        
        # Pattern สำหรับวันที่ในรูปแบบต่าง ๆ
        self.date_patterns = {
            # ISO format: 2025-01-15
            'iso_date': r'(\d{4})-(\d{1,2})-(\d{1,2})',
            
            # Thai format: 15/1/25, 15/01/2025
            'thai_date': r'(\d{1,2})/(\d{1,2})/(\d{2,4})',
            
            # Thai format with dots: 15.1.25
            'dot_date': r'(\d{1,2})\.(\d{1,2})\.(\d{2,4})',
            
            # Relative dates
            'today': r'(วันนี้|today)',
            'tomorrow': r'(พรุ่งนี้|tomorrow)',
            'day_after_tomorrow': r'(มะรืนนี้|วันมะรืน)',
            
            # Day names
            'monday': r'(วันจันทร์|จันทร์|monday)',
            'tuesday': r'(วันอังคาร|อังคาร|tuesday)',
            'wednesday': r'(วันพุธ|พุธ|wednesday)',
            'thursday': r'(วันพฤหัสบดี|พฤหัส|thursday)',
            'friday': r'(วันศุกร์|ศุกร์|friday)',
            'saturday': r'(วันเสาร์|เสาร์|saturday)',
            'sunday': r'(วันอาทิตย์|อาทิตย์|sunday)',
        }
        
        # Pattern สำหรับชื่อหมอ
        self.doctor_patterns = {
            # Doctor titles and names
            'doctor_title': r'(นพ\.|นพ|ดร\.|ดอกเตอร์|หมอ|แพทย์|พศ\.|ผศ\.|รศ\.|ศ\.)',
            'doctor_with_name': r'(นพ\.|นพ|ดร\.|หมอ|แพทย์|พศ\.|ผศ\.|รศ\.|ศ\.)\s*([ก-๙a-zA-Z\s]+)',
            'simple_doctor': r'หมอ([ก-๙a-zA-Z]+)',
            'doctor_specialty': r'หมอ(โรค[ก-๙]+|[ก-๙]+โรค|เด็ก|ตา|หู|คอ|จมูก|ฟัน|หัวใจ|ไต|กระดูก)',
        }
        
        # Pattern สำหรับเวลา
        self.time_patterns = {
            # 24-hour format: 14:30, 09:00
            'hour_minute': r'(\d{1,2}):(\d{2})',
            
            # Hour with units: 9 โมง, 14 น.
            'thai_hour': r'(\d{1,2})\s*(?:โมง|น\.?|นาฬิกา)',
            
            # Thai time names
            'morning': r'(เช้า|morning)',
            'afternoon': r'(บ่าย|afternoon)', 
            'evening': r'(เย็น|evening)',
            'night': r'(กลางคืน|คืน|night)',
            
            # Specific times
            'dawn': r'(เช้าตรู่|รุ่งเช้า)',
            'noon': r'(เที่ยง|noon)',
            'midnight': r'(เที่ยงคืน|midnight)',
        }
        
        # Mapping สำหรับวันในสัปดาห์
        self.weekday_mapping = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        # Mapping สำหรับเวลาโดยประมาณ
        self.time_mapping = {
            'morning': (8, 0),     # 08:00
            'afternoon': (13, 0),  # 13:00
            'evening': (17, 0),    # 17:00
            'night': (20, 0),      # 20:00
            'dawn': (6, 0),        # 06:00
            'noon': (12, 0),       # 12:00
            'midnight': (0, 0),    # 00:00
        }
    
    def parse_datetime(self, text: str, base_date: datetime = None) -> Tuple[Optional[datetime], str]:
        """
        แยกวิเคราะห์วันที่และเวลาจากข้อความ
        
        Args:
            text (str): ข้อความที่จะแยกวิเคราะห์
            base_date (datetime): วันที่ฐานสำหรับการคำนวณ (default: วันนี้)
        
        Returns:
            Tuple[Optional[datetime], str]: (วันที่-เวลาที่พบ, ข้อความที่เหลือหลังลบวันที่-เวลา)
        """
        if base_date is None:
            base_date = datetime.now(BANGKOK_TZ)
        
        original_text = text
        parsed_date = None
        parsed_time = None
        
        logger.info(f"Parsing datetime from: '{text}'")
        
        # 1. หาวันที่
        parsed_date, text = self._parse_date(text, base_date)
        
        # 2. หาเวลา
        parsed_time, text = self._parse_time(text)
        
        # 3. รวมวันที่และเวลา
        if parsed_date and parsed_time:
            # มีทั้งวันที่และเวลา
            result_datetime = parsed_date.replace(
                hour=parsed_time[0], 
                minute=parsed_time[1],
                second=0,
                microsecond=0
            )
        elif parsed_date:
            # มีแค่วันที่ ใช้เวลาเริ่มต้น 09:00
            result_datetime = parsed_date.replace(hour=9, minute=0, second=0, microsecond=0)
        elif parsed_time:
            # มีแค่เวลา ใช้วันพรุ่งนี้
            tomorrow = base_date + timedelta(days=1)
            result_datetime = tomorrow.replace(
                hour=parsed_time[0],
                minute=parsed_time[1],
                second=0,
                microsecond=0
            )
        else:
            # ไม่พบวันที่-เวลา ใช้ค่าเริ่มต้น (พรุ่งนี้ 09:00)
            result_datetime = base_date + timedelta(days=1)
            result_datetime = result_datetime.replace(hour=9, minute=0, second=0, microsecond=0)
        
        # ล้าง text ที่เหลือ
        clean_text = text.strip()
        
        logger.info(f"Parsed result: {result_datetime}, remaining text: '{clean_text}'")
        return result_datetime, clean_text
    
    def _parse_date(self, text: str, base_date: datetime) -> Tuple[Optional[datetime], str]:
        """แยกวิเคราะห์วันที่จากข้อความ"""
        
        text_lower = text.lower()
        
        # ตรวจสอบวันที่แบบ ISO (2025-01-15)
        match = re.search(self.date_patterns['iso_date'], text)
        if match:
            year, month, day = map(int, match.groups())
            try:
                result_date = datetime(year, month, day, tzinfo=BANGKOK_TZ)
                remaining_text = text[:match.start()] + text[match.end():]
                return result_date, remaining_text.strip()
            except ValueError:
                pass
        
        # ตรวจสอบวันที่แบบไทย (15/1/25)
        match = re.search(self.date_patterns['thai_date'], text)
        if match:
            day, month, year = map(int, match.groups())
            # แปลงปี 2 หลัก เป็น 4 หลัก
            if year < 100:
                year = 2000 + year if year < 50 else 1900 + year
            try:
                result_date = datetime(year, month, day, tzinfo=BANGKOK_TZ)
                remaining_text = text[:match.start()] + text[match.end():]
                return result_date, remaining_text.strip()
            except ValueError:
                pass
        
        # ตรวจสอบวันสัมพันธ์ (วันนี้, พรุ่งนี้)
        if re.search(self.date_patterns['today'], text_lower):
            remaining_text = re.sub(self.date_patterns['today'], '', text, flags=re.IGNORECASE).strip()
            return base_date, remaining_text
        
        if re.search(self.date_patterns['tomorrow'], text_lower):
            tomorrow = base_date + timedelta(days=1)
            remaining_text = re.sub(self.date_patterns['tomorrow'], '', text, flags=re.IGNORECASE).strip()
            return tomorrow, remaining_text
        
        if re.search(self.date_patterns['day_after_tomorrow'], text_lower):
            day_after = base_date + timedelta(days=2)
            remaining_text = re.sub(self.date_patterns['day_after_tomorrow'], '', text, flags=re.IGNORECASE).strip()
            return day_after, remaining_text
        
        # ตรวจสอบวันในสัปดาห์
        for day_name, pattern in self.date_patterns.items():
            if day_name in self.weekday_mapping:
                if re.search(pattern, text_lower):
                    target_weekday = self.weekday_mapping[day_name]
                    current_weekday = base_date.weekday()
                    days_ahead = target_weekday - current_weekday
                    if days_ahead <= 0:  # หมายถึงสัปดาห์หน้า
                        days_ahead += 7
                    target_date = base_date + timedelta(days=days_ahead)
                    remaining_text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
                    return target_date, remaining_text
        
        return None, text
    
    def _parse_time(self, text: str) -> Tuple[Optional[Tuple[int, int]], str]:
        """แยกวิเคราะห์เวลาจากข้อความ"""
        
        text_lower = text.lower()
        
        # ตรวจสอบเวลาแบบ HH:MM
        match = re.search(self.time_patterns['hour_minute'], text)
        if match:
            hour, minute = map(int, match.groups())
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                remaining_text = text[:match.start()] + text[match.end():]
                return (hour, minute), remaining_text.strip()
        
        # ตรวจสอบเวลาแบบไทย (9 โมง)
        match = re.search(self.time_patterns['thai_hour'], text_lower)
        if match:
            hour = int(match.group(1))
            if 0 <= hour <= 23:
                remaining_text = text[:match.start()] + text[match.end():]
                return (hour, 0), remaining_text.strip()
        
        # ตรวจสอบเวลาโดยประมาณ
        for time_name, pattern in self.time_patterns.items():
            if time_name in self.time_mapping:
                if re.search(pattern, text_lower):
                    time_tuple = self.time_mapping[time_name]
                    remaining_text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
                    return time_tuple, remaining_text
        
        return None, text
    
    def _parse_doctor_info(self, text: str) -> Tuple[Optional[str], str]:
        """แยกวิเคราะห์ข้อมูลหมอจากข้อความ"""
        
        text_original = text
        doctor_name = None
        
        # 1. ตรวจหา doctor with full name (นพ.สมชาย, ดร.วิชัย)
        for pattern_name, pattern in self.doctor_patterns.items():
            if pattern_name == 'doctor_with_name':
                match = re.search(pattern, text)
                if match:
                    title = match.group(1)
                    name = match.group(2).strip()
                    doctor_name = f"{title}{name}"
                    # ลบข้อมูลหมอออกจากข้อความ
                    text = text[:match.start()] + text[match.end():]
                    return doctor_name, text.strip()
        
        # 2. ตรวจหา simple doctor (หมอแดง)
        match = re.search(self.doctor_patterns['simple_doctor'], text)
        if match:
            name = match.group(1).strip()
            doctor_name = f"หมอ{name}"
            text = text[:match.start()] + text[match.end():]
            return doctor_name, text.strip()
        
        # 3. ตรวจหา doctor specialty (หมอโรคหัวใจ)
        match = re.search(self.doctor_patterns['doctor_specialty'], text)
        if match:
            specialty = match.group(1).strip()
            doctor_name = f"หมอ{specialty}"
            text = text[:match.start()] + text[match.end():]
            return doctor_name, text.strip()
        
        # 4. ตรวจหา doctor title only (หมอ, นพ, ดร)
        match = re.search(self.doctor_patterns['doctor_title'], text)
        if match:
            title = match.group(1).strip()
            doctor_name = title
            text = text[:match.start()] + text[match.end():]
            return doctor_name, text.strip()
        
        return None, text
    
    def _parse_structured_appointment(self, text: str) -> Optional[Dict[str, Any]]:
        """
        แยกวิเคราะห์ข้อความแบบ structured format:
        ชื่อนัดหมาย: "..."
        วันเวลา: "..."
        แพทย์: "..."
        โรงพยาบาล: "..."
        แผนก: "..."
        """
        
        # ตรวจสอบว่ามี structured format หรือไม่
        if 'ชื่อนัดหมาย:' not in text and 'วันเวลา:' not in text:
            return None
            
        logger.info(f"Parsing structured appointment: {text}")
        
        # แยกแต่ละ field
        title = self._extract_field(text, r'ชื่อนัดหมาย:\s*["\']?([^"\'\r\n]+)["\']?')
        datetime_str = self._extract_field(text, r'วันเวลา:\s*["\']?([^"\'\r\n]+)["\']?')
        doctor = self._extract_field(text, r'แพทย์:\s*["\']?([^"\'\r\n]+)["\']?')
        hospital = self._extract_field(text, r'โรงพยาบาล:\s*["\']?([^"\'\r\n]+)["\']?')
        department = self._extract_field(text, r'แผนก:\s*["\']?([^"\'\r\n]+)["\']?')
        
        # ตรวจสอบ required fields
        if not datetime_str:
            return None
            
        # แปลงวันเวลา
        appointment_dt = self._parse_datetime_string(datetime_str)
        if not appointment_dt:
            return None
        
        logger.info(f"Structured parsing successful: {appointment_dt.strftime('%d/%m/%Y %H:%M')}")
        
        return {
            'datetime': appointment_dt,
            'title': title or "การนัดหมาย",
            'doctor': doctor or "ไม่ระบุ",
            'location': hospital or "ไม่ระบุ",
            'hospital': hospital or "ไม่ระบุ",
            'department': department or "ทั่วไป",
            'error': None
        }
    
    def _extract_field(self, text: str, pattern: str) -> Optional[str]:
        """แยก field จาก structured text"""
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None
        
    def _parse_datetime_string(self, datetime_str: str) -> Optional[datetime]:
        """แปลงข้อความวันเวลาเป็น datetime object"""
        try:
            logger.info(f"[PARSER] Parsing datetime string: '{datetime_str}'")
            
            # ลองหลายรูปแบบ (เรียงตามความน่าจะเป็น)
            formats = [
                '%d/%m/%Y %H:%M',    # 08/10/2025 15:00 (รูปแบบหลัก)
                '%d/%m/%Y %H.%M',    # 08/10/2025 15.00
                '%Y-%m-%d %H:%M',    # 2025-10-08 15:00
                '%Y-%m-%d %H.%M',    # 2025-10-08 15.00
                '%d-%m-%Y %H:%M',    # 08-10-2025 15:00
                '%d-%m-%Y %H.%M',    # 08-10-2025 15.00
                '%d %B %Y %H:%M',    # 08 October 2025 15:00
                '%d %B %Y %H.%M',    # 08 October 2025 15.00
            ]
            
            # แปลงชื่อเดือนไทยเป็นภาษาอังกฤษ
            thai_to_eng = {
                'มกราคม': 'January', 'กุมภาพันธ์': 'February', 'มีนาคม': 'March',
                'เมษายน': 'April', 'พฤษภาคม': 'May', 'มิถุนายน': 'June',
                'กรกฎาคม': 'July', 'สิงหาคม': 'August', 'กันยายน': 'September',
                'ตุลาคม': 'October', 'พฤศจิกายน': 'November', 'ธันวาคม': 'December'
            }
            
            datetime_str_en = datetime_str
            for thai, eng in thai_to_eng.items():
                datetime_str_en = datetime_str_en.replace(thai, eng)
            
            logger.info(f"[PARSER] Converted string: '{datetime_str_en}'")
            
            for i, fmt in enumerate(formats):
                try:
                    dt = datetime.strptime(datetime_str_en, fmt)
                    result_dt = dt.replace(tzinfo=BANGKOK_TZ)
                    logger.info(f"[PARSER] SUCCESS with format {i+1} ({fmt}): {result_dt}")
                    return result_dt
                except ValueError as e:
                    logger.debug(f"[PARSER] Format {i+1} ({fmt}) failed: {e}")
                    continue
                    
            # ถ้าไม่ได้ ลองใช้ parser เดิม
            logger.warning(f"[PARSER] All formats failed, trying fallback parser")
            parsed_dt, _ = self.parse_datetime(datetime_str)
            logger.info(f"[PARSER] Fallback result: {parsed_dt}")
            return parsed_dt
            
        except Exception as e:
            logger.error(f"Failed to parse datetime string '{datetime_str}': {e}")
            return None

    def _parse_complex_appointment(self, text: str) -> Optional[Dict[str, Any]]:
        """
        แยกวิเคราะห์ข้อความแต่งแบบซับซ้อน เช่น 
        "วันที่ 1 ตุลาคม 2025 เวลา 13.00 โรงพยาบาล ศิริราชปิยะการุณย์ แผนก กุมารเวชกรรม นัดติดตามพัฒนาการ พบ พญ. เนตรวิมล นันทิวัฒน์"
        """
        
        # ตรวจสอบว่ามี pattern ของข้อความซับซ้อนหรือไม่
        if 'วันที่' not in text or 'เวลา' not in text or 'โรงพยาบาล' not in text:
            return None
            
        logger.info(f"Parsing complex appointment: {text}")
        
        # แยกวันที่ (รองรับทั้ง DD/MM/YYYY และ DD เดือนไทย YYYY)
        date_match = re.search(r'วันที่\s*(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', text)
        if date_match:
            # รูปแบบ DD/MM/YYYY หรือ DD-MM-YYYY
            day = int(date_match.group(1))
            month = int(date_match.group(2))
            year = int(date_match.group(3))
        else:
            # รูปแบบ DD เดือนไทย YYYY
            date_match = re.search(r'วันที่\s*(\d{1,2})\s*([\u0E01-\u0E5B]+)\s*(\d{4})', text)
            if not date_match:
                return None
                
            day = int(date_match.group(1))
            month_thai = date_match.group(2)
            year = int(date_match.group(3))
            
            # แปลงเดือนไทยเป็นตัวเลข
            thai_months = {
                'มกราคม': 1, 'กุมภาพันธ์': 2, 'มีนาคม': 3, 'เมษายน': 4,
                'พฤษภาคม': 5, 'มิถุนายน': 6, 'กรกฎาคม': 7, 'สิงหาคม': 8,
                'กันยายน': 9, 'ตุลาคม': 10, 'พฤศจิกายน': 11, 'ธันวาคม': 12
            }
            month = thai_months.get(month_thai, 1)
        
        # แยกเวลา (รองรับทั้งจุดและโคลอน)
        time_match = re.search(r'เวลา\s*(\d{1,2})[.:](\d{2})', text)
        if not time_match:
            return None
            
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))
        
        # แยกโรงพยาบาล (ใช้ Unicode range สำหรับตัวอักษรไทย)
        hospital_match = re.search(r'โรงพยาบาล\s*([^\s]+(?:\s+[^\s]+)*?)(?:\s+แผนก|\s*$)', text)
        hospital_name = hospital_match.group(1).strip() if hospital_match else "ไม่ระบุ"
        
        # แยกแผนก (หลัง "แผนก" จนถึงคำถัดไป)
        dept_match = re.search(r'แผนก\s*([^\s]+(?:\s+[^\s]+)*?)(?:\s+(?:ตรวจ|ปรึกษา|นัด|พบ)|$)', text)
        department_name = dept_match.group(1).strip() if dept_match else "ทั่วไป"
        
        # แยกหัวข้อการนัด (หาคำที่อยู่หลังแผนกแต่ก่อน "พบ")
        # Pattern: หลังแผนก [department] [title words] พบ
        remaining_after_dept = re.sub(r'.*?แผนก\s*[^\s]+(?:\s+[^\s]+)*?\s+', '', text)
        title_match = re.search(r'^([^พบ]+?)(?:\s*พบ|$)', remaining_after_dept)
        appointment_title = title_match.group(1).strip() if title_match else "การนัดหมาย"
        
        # แยกชื่อหมอ
        doctor_match = re.search(r'พบ\s*(.+?)$', text)
        doctor_name = doctor_match.group(1).strip() if doctor_match else "ไม่ระบุ"
        
        
        # สร้าง datetime object
        try:
            appointment_dt = datetime(year, month, day, hour, minute, 0, tzinfo=BANGKOK_TZ)
        except ValueError as e:
            logger.error(f"Failed to create datetime: {e}")
            return None
        
        logger.info(f"Complex parsing successful: {appointment_dt.strftime('%d/%m/%Y %H:%M')} at {hospital_name}")
        
        return {
            'datetime': appointment_dt,
            'title': appointment_title,
            'doctor': doctor_name,
            'location': hospital_name,
            'hospital': hospital_name,
            'department': department_name,
            'error': None
        }

    def extract_appointment_info(self, message: str) -> Dict[str, Any]:
        """
        แยกข้อมูลการนัดหมายจากข้อความ
        
        Args:
            message (str): ข้อความเต็ม เช่น "เพิ่มนัด ตรวจสุขภาพ 2025-01-15 09:00 โรงพยาบาล"
        
        Returns:
            Dict[str, Any]: ข้อมูลที่แยกได้ {datetime, title, location, etc.}
        """
        
        # ลบคำสั่ง "เพิ่มนัด" ออก
        command_patterns = [
            r'เพิ่มนัด\s*',
            r'นัดใหม่\s*',
            r'เพิ่มการนัด\s*'
        ]
        
        clean_message = message
        for pattern in command_patterns:
            clean_message = re.sub(pattern, '', clean_message, flags=re.IGNORECASE).strip()
        
        if not clean_message:
            return {
                'datetime': None,
                'title': 'นัดหมายใหม่',
                'location': '',
                'hospital': '',
                'department': '',
                'error': 'กรุณาระบุรายละเอียดการนัดหมาย'
            }
        
        # ตรวจสอบรูปแบบ structured format ก่อน
        structured_result = self._parse_structured_appointment(clean_message)
        if structured_result:
            return structured_result
            
        # ตรวจสอบรูปแบบข้อความที่ซับซ้อน
        complex_result = self._parse_complex_appointment(clean_message)
        if complex_result:
            return complex_result
        
        # แยกวันที่และเวลา
        parsed_datetime, remaining_text = self.parse_datetime(clean_message)
        
        # แยกข้อมูลหมอ
        doctor_name, remaining_text = self._parse_doctor_info(remaining_text)
        
        # แยกข้อมูลเพิ่มเติม
        parts = remaining_text.split()
        
        # หาโรงพยาบาล/สถานที่
        hospital_keywords = ['โรงพยาบาล', 'รพ', 'hospital', 'คลินิก', 'clinic']
        hospital = ''
        department = ''
        
        hospital_parts = []
        other_parts = []
        
        for part in parts:
            if any(keyword in part.lower() for keyword in hospital_keywords):
                hospital_parts.append(part)
            else:
                other_parts.append(part)
        
        if hospital_parts:
            hospital = ' '.join(hospital_parts)
        
        # ส่วนที่เหลือเป็นชื่อการนัดหมาย
        title_parts = other_parts if other_parts else ['นัดหมาย']
        
        # ถ้ามีชื่อหมอ ให้รวมเข้าไปในชื่อการนัดหมาย
        if doctor_name:
            title = f"พบ {doctor_name}"
            if other_parts:
                title += f" ({' '.join(other_parts)})"
        else:
            title = ' '.join(title_parts)
        
        return {
            'datetime': parsed_datetime,
            'title': title,
            'doctor': doctor_name if doctor_name else 'ไม่ระบุ',
            'location': hospital,
            'hospital': hospital if hospital else 'ไม่ระบุ',
            'department': 'ทั่วไป',
            'error': None
        }


def test_parser():
    """ฟังก์ชันทดสอบ parser"""
    parser = SmartDateTimeParser()
    
    test_cases = [
        "ตรวจสุขภาพประจำปี 2025-01-15 09:00 โรงพยาบาลราชวิถี",
        "พบ นพ.สมชาย 15/1/25 เช้า",
        "นัดฟัน ดร.วิชัย พรุ่งนี้ 14:30",
        "ตรวจเลือด หมอแดง วันจันทร์หน้า เวลา 10 โมงเช้า",
        "พบ หมอโรคหัวใจ วันนี้ บ่าย",
        "ผ่าตัด พศ.อำนาจ 25/12/2024 เที่ยง โรงพยาบาลจุฬา",
        "วันที่ 1 ตุลาคม 2025 เวลา 13.00 โรงพยาบาล ศิริราชปิยะการุณย์  แผนก กุมารเวชกรรม นัดติดตามพัฒนาการ พบ พญ. เนตรวิมล นันทิวัฒน์",
        "วันที่ 8 ตุลาคม 2025 เวลา 14.00 โรงพยาบาล ศิริราชปิยะการุณย์  แผนก คลินิกทันตกรรม ปรึกษาตรวจฟัน พบ ทพญ. ปารัช ศิริวิชยกุล"
    ]
    
    for test_case in test_cases:
        print(f"\\nTesting: '{test_case}'")
        result = parser.extract_appointment_info(f"เพิ่มนัด {test_case}")
        print(f"Result: {result}")


if __name__ == "__main__":
    test_parser()