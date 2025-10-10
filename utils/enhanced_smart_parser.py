# Enhanced Smart Parser with PyThaiNLP
# ตัวอย่างโครงสร้างสำหรับ EnhancedSmartDateTimeParser

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import re

# PyThaiNLP imports (เตรียมไว้ก่อน)
"""
from pythainlp import word_tokenize
from pythainlp.tag import pos_tag, named_entity
from pythainlp.util import normalize
from pythainlp.corpus import thai_stopwords
"""

class EnhancedSmartDateTimeParser:
    """
    Enhanced version ของ SmartDateTimeParser ที่ใช้ PyThaiNLP
    เพื่อความฉลาดในการประมวลผลภาษาไทย
    """
    
    def __init__(self):
        self.setup_pythainlp_components()
        self.setup_patterns()
        self.setup_thai_context_maps()
    
    def setup_pythainlp_components(self):
        """ตั้งค่า PyThaiNLP components"""
        # เมื่อพร้อมจะใส่ PyThaiNLP จริง
        self.use_pythainlp = False  # Flag สำหรับเปิด/ปิด PyThaiNLP
        
        if self.use_pythainlp:
            try:
                # import และ setup PyThaiNLP
                pass
            except ImportError:
                print("PyThaiNLP not available, using basic parsing")
                self.use_pythainlp = False
    
    def setup_patterns(self):
        """ตั้งค่า patterns สำหรับการ parse แบบครบถ้วน"""
        
        # Command patterns for detecting appointment requests
        self.command_patterns = {
            'add_appointment': [
                r'เพิ่มนัด',
                r'นัดหมาย',
                r'จองนัด',
                r'ตั้งนัด',
                r'ขอนัด'
            ]
        }

        # Date patterns (ภาษาไทยครบถ้วน)
        self.date_patterns = {
            'relative_day': {
                'วันนี้': 0,
                'พรุ่งนี้': 1,
                'มะรืนนี้': 2,
                'มะรืน': 2,
                'เมื่อวาน': -1,
                'เมื่อวานนี้': -1,
                'มะเมื่อวาน': -2
            },
            'weekday': {
                'จันทร์': 0, 'อังคาร': 1, 'พุธ': 2,
                'พฤหัสบดี': 3, 'พฤหัส': 3, 'ศุกร์': 4,
                'เสาร์': 5, 'อาทิตย์': 6
            },
            'weekday_modifier': {
                'นี้': 0, 'หน้า': 1, 'ถัดไป': 1, 'ที่แล้ว': -1
            },
            'period': [
                r'สัปดาห์หน้า',
                r'สิ้นเดือน',
                r'ต้นเดือน',
                r'ปลายเดือน',
                r'เดือนหน้า',
                r'ปีหน้า'
            ]
        }

        # Time patterns (ภาษาไทยครบถ้วน)
        self.time_patterns = {
            'formal': [
                r'(?P<h>\d{1,2})[:.](?P<m>\d{2})\s*น?\.?',
                r'เวลา\s*(?P<h>\d{1,2})[:.](?P<m>\d{2})',
                r'(?P<h>\d{1,2})\s*นาฬิกา\s*(?P<m>\d{2})?'
            ],
            'spoken': [
                r'(?P<h>\d{1,2})\s*โมง(?P<period>เช้า|เย็น|ตรง)?(?P<half>ครึ่ง)?',
                r'บ่าย\s*(?P<h>\d{1,2})(?P<half>ครึ่ง)?',
                r'(?P<h>\d{1,2})\s*โมงเย็น(?P<half>ครึ่ง)?',
                r'(?P<h>\d{1,2})\s*ทุ่ม(?P<half>ครึ่ง)?',
                r'เที่ยงตรง',
                r'เที่ยงคืน',
                r'เที่ยง',
                r'ตอน(เช้า|สาย|เที่ยง|บ่าย|เย็น|ค่ำ|ดึก)'
            ],
            'period_defaults': {
                'เช้า': (6, 11),
                'สาย': (9, 11),
                'เที่ยง': (11, 13),
                'บ่าย': (12, 17),
                'เย็น': (17, 19),
                'ค่ำ': (18, 21),
                'ดึก': (21, 24)
            }
        }

        # Location patterns (ครบถ้วน)
        self.location_patterns = {
            'connectors': [
                r'ที่\s+(.+?)(?:\s|$|[,.])',
                r'ณ\s+(.+?)(?:\s|$|[,.])',
                r'ใน\s+(.+?)(?:\s|$|[,.])',
                r'ไป\s*(.+?)(?:\s|$|[,.])'
            ],
            'specific': [
                r'ที่สนามบิน(.+?)(?:\s|$|[,.])',
                r'สนามบิน(.+?)(?:\s|$|[,.])',
                r'ที่โรงพยาบาล(.+?)(?:\s|$|[,.])',
                r'โรงพยาบาล(.+?)(?:\s|$|[,.])',
                r'รพ\.?\s*(.+?)(?:\s|$|[,.])',
                r'คลินิก(.+?)(?:\s|$|[,.])'
            ]
        }

        # (Moved normalization_maps and later context maps to setup_thai_context_maps)
        return

        # Time mapping rules (UNREACHABLE - kept for reference, real init in setup_thai_context_maps)
        self.time_mappings = {
            # Hour conversion rules
            'hour_conversions': {
                'เที่ยงตรง': (12, 0),
                'เที่ยงคืน': (0, 0),
                'เที่ยง': (12, 0)
            },
            
            # Period-specific hour adjustments
            'period_adjustments': {
                'เช้า': lambda h: h if h >= 6 else h + 12 if h <= 5 else h,
                'สาย': lambda h: h if h >= 9 else h + 12,
                'บ่าย': lambda h: h + 12 if h <= 6 else h,
                'เย็น': lambda h: h + 12 if h <= 7 else h,
                'ทุ่ม': lambda h: h + 18,  # 1 ทุ่ม = 19:00, 2 ทุ่ม = 20:00
            },
            
            # Common time expressions
            'expressions': {
                'หนึ่งทุ่ม': (19, 0),
                'สองทุ่ม': (20, 0),
                'สามทุ่ม': (21, 0),
                'สี่ทุ่ม': (22, 0),
                'ห้าทุ่ม': (23, 0),
                'หกทุ่ม': (0, 0),  # Next day
                'บ่ายสอง': (14, 0),
                'บ่ายสองครึ่ง': (14, 30),
                'สามทุ่มครึ่ง': (21, 30),
                'สี่โมงเย็น': (16, 0)
            }
        }
        
        # Medical context keywords (refined)
        self.medical_keywords = {
            'doctor': ['หมอ', 'แพทย์', 'ดร.', 'นพ.', 'พญ.'],
            'appointment': ['ตรวจ', 'รักษา', 'ฉีด'],  # Removed generic words
            'hospital': ['โรงพยาบาล', 'รพ.', 'คลินิก', 'ศูนย์การแพทย์'],
            'medical_action': ['ตรวจ', 'รักษา', 'ผ่าตัด', 'ฉีดยา', 'เอ็กซเรย์', 'ครั่าง', 'วิเคราะห์']
        }
        
        # Business context keywords  
        self.business_keywords = {
            'meeting': ['ประชุม', 'มีติง', 'พบ', 'หารือ', 'สัมมนา'],
            'location': ['ห้องประชุม', 'สำนักงาน', 'บริษัท', 'ออฟฟิศ', 'ออฟฟิศ'],
            'formal': ['การประชุม', 'การพบปะ', 'การหารือ']
        }
        
        # Date calculation helpers
        self.date_helpers = {
            'weekday_names': ['จันทร์', 'อังคาร', 'พุธ', 'พฤหัสบดี', 'พฤหัส', 'ศุกร์', 'เสาร์', 'อาทิตย์'],
            'period_calculations': {
                'สัปดาห์หน้า': lambda date: date + timedelta(weeks=1),
                'สิ้นเดือน': lambda date: self._end_of_month(date),
                'ต้นเดือน': lambda date: self._start_of_month(date), 
                'ปลายเดือน': lambda date: self._end_of_month(date),
                'เดือนหน้า': lambda date: self._next_month(date)
            }
        }

        # === THAI_MONTHS_MAP (Integrated 2025-10-08) ===
        self.thai_months: Dict[str, int] = {
            'มกราคม': 1, 'ม.ค.': 1, 'มค': 1, 'มค.': 1,
            'กุมภาพันธ์': 2, 'ก.พ.': 2, 'กพ': 2, 'กพ.': 2,
            'มีนาคม': 3, 'มี.ค.': 3, 'มีค': 3, 'มีค.': 3,
            'เมษายน': 4, 'เม.ย.': 4, 'เมย': 4, 'เมย.': 4,
            'พฤษภาคม': 5, 'พ.ค.': 5, 'พค': 5, 'พค.': 5,
            'มิถุนายน': 6, 'มิ.ย.': 6, 'มิย': 6, 'มิย.': 6,
            'กรกฎาคม': 7, 'ก.ค.': 7, 'กค': 7, 'กค.': 7,
            'สิงหาคม': 8, 'ส.ค.': 8, 'สค': 8, 'สค.': 8,
            'กันยายน': 9, 'ก.ย.': 9, 'กย': 9, 'กย.': 9,
            'ตุลาคม': 10, 'ต.ค.': 10, 'ตค': 10, 'ตค.': 10,
            'พฤศจิกายน': 11, 'พ.ย.': 11, 'พย': 11, 'พย.': 11,
            'ธันวาคม': 12, 'ธ.ค.': 12, 'ธค': 12, 'ธค.': 12
        }
    
    def setup_thai_context_maps(self):
        """Setup Thai-specific normalization maps, time mappings, domain keywords, helpers, and month names.

        This method was missing (causing AttributeError). It consolidates context
        data that earlier patches moved out of setup_patterns. Keep definitions
        minimal but sufficient for current parser logic.
        """
        # 1. Normalization maps used in pre_normalize_text
        self.normalization_maps = {
            'thai_numerals': {
                '๐': '0', '๑': '1', '๒': '2', '๓': '3', '๔': '4',
                '๕': '5', '๖': '6', '๗': '7', '๘': '8', '๙': '9'
            },
            'abbreviations': {
                'พน.': 'พรุ่งนี้',
                'มะรืน': 'มะรืนนี้',
                'รพ.': 'โรงพยาบาล',
                'รพ': 'โรงพยาบาล'
            },
            'location_aliases': {
                'รพ.': 'โรงพยาบาล',
                'รพ': 'โรงพยาบาล',
                'รร.': 'โรงแรม'
            }
        }

        # 2. Time mappings (used by extract_time_patterns / parse_spoken_time)
        self.time_mappings = {
            'hour_conversions': {
                'เที่ยงตรง': (12, 0),
                'เที่ยงคืน': (0, 0),
                'เที่ยง': (12, 0)
            },
            'period_adjustments': {
                'เช้า': lambda h: h if h >= 6 else h + 12 if h <= 5 else h,
                'สาย': lambda h: h if h >= 9 else h + 12,
                'บ่าย': lambda h: h + 12 if h <= 6 else h,
                'เย็น': lambda h: h + 12 if h <= 7 else h,
                'ทุ่ม': lambda h: h + 18,  # 1 ทุ่ม = 19:00
            },
            'expressions': {
                'หนึ่งทุ่ม': (19, 0),
                'สองทุ่ม': (20, 0),
                'สามทุ่ม': (21, 0),
                'สี่ทุ่ม': (22, 0),
                'ห้าทุ่ม': (23, 0),
                'หกทุ่ม': (0, 0),
                'บ่ายสอง': (14, 0),
                'บ่ายสองครึ่ง': (14, 30),
                'สามทุ่มครึ่ง': (21, 30),
                'สี่โมงเย็น': (16, 0)
            }
        }

        # 3. Domain keywords
        self.medical_keywords = {
            'doctor': ['หมอ', 'แพทย์', 'ดร.', 'นพ.', 'พญ.'],
            'appointment': ['ตรวจ', 'รักษา', 'ฉีด'],
            'hospital': ['โรงพยาบาล', 'รพ.', 'คลินิก', 'ศูนย์การแพทย์'],
            'medical_action': ['ตรวจ', 'รักษา', 'ผ่าตัด', 'ฉีดยา', 'เอ็กซเรย์', 'วิเคราะห์']
        }
        self.business_keywords = {
            'meeting': ['ประชุม', 'มีติง', 'พบ', 'หารือ', 'สัมมนา'],
            'location': ['ห้องประชุม', 'สำนักงาน', 'บริษัท', 'ออฟฟิศ'],
            'formal': ['การประชุม', 'การพบปะ', 'การหารือ']
        }

        # 4. Date helpers (for potential future use)
        self.date_helpers = {
            'weekday_names': ['จันทร์', 'อังคาร', 'พุธ', 'พฤหัสบดี', 'พฤหัส', 'ศุกร์', 'เสาร์', 'อาทิตย์'],
            'period_calculations': {
                'สัปดาห์หน้า': lambda date: date + timedelta(weeks=1),
                'สิ้นเดือน': lambda date: self._end_of_month(date),
                'ต้นเดือน': lambda date: self._start_of_month(date),
                'ปลายเดือน': lambda date: self._end_of_month(date),
                'เดือนหน้า': lambda date: self._next_month(date)
            }
        }

        # 5. Thai month names (ensure available before date extraction)
        self.thai_months = {
            'มกราคม': 1, 'ม.ค.': 1, 'มค': 1, 'มค.': 1,
            'กุมภาพันธ์': 2, 'ก.พ.': 2, 'กพ': 2, 'กพ.': 2,
            'มีนาคม': 3, 'มี.ค.': 3, 'มีค': 3, 'มีค.': 3,
            'เมษายน': 4, 'เม.ย.': 4, 'เมย': 4, 'เมย.': 4,
            'พฤษภาคม': 5, 'พ.ค.': 5, 'พค': 5, 'พค.': 5,
            'มิถุนายน': 6, 'มิ.ย.': 6, 'มิย': 6, 'มิย.': 6,
            'กรกฎาคม': 7, 'ก.ค.': 7, 'กค': 7, 'กค.': 7,
            'สิงหาคม': 8, 'ส.ค.': 8, 'สค': 8, 'สค.': 8,
            'กันยายน': 9, 'ก.ย.': 9, 'กย': 9, 'กย.': 9,
            'ตุลาคม': 10, 'ต.ค.': 10, 'ตค': 10, 'ตค.': 10,
            'พฤศจิกายน': 11, 'พ.ย.': 11, 'พย': 11, 'พย.': 11,
            'ธันวาคม': 12, 'ธ.ค.': 12, 'ธค': 12, 'ธค.': 12,
            # Informal / spoken short forms
            'มกรา': 1, 'กุมภา': 2, 'มีนา': 3, 'เมษา': 4,
            'พฤษภา': 5, 'มิถุนา': 6, 'กรกฎา': 7, 'สิงหา': 8,
            'กันยา': 9, 'ตุลา': 10, 'พฤศจิกา': 11, 'ธันวา': 12
        }

        # Optional: simple contact patterns container to avoid attribute errors if used
        self.contact_patterns = {
            'phone': [r'(0\d{2}-?\d{3}-?\d{4})']
        }

        # Debug marker
        # print('[setup_thai_context_maps] initialized')
    
    def preprocess_text_basic(self, text: str) -> Dict[str, Any]:
        """
        Basic text preprocessing with comprehensive normalization
        """
        # Step 1: Pre-normalize text
        normalized_text = self.pre_normalize_text(text)
        
        # Step 2: Basic tokenization (split by spaces for now)
        basic_tokens = self.tokenize_basic(normalized_text)
        
        # Step 3: Extract patterns using enhanced rules
        time_matches = self.extract_time_patterns(normalized_text)
        date_matches = self.extract_date_patterns(normalized_text)
        location_matches = self.extract_location_patterns(normalized_text)
        contact_matches = self.extract_contact_patterns(normalized_text)
        
        return {
            'original': text,
            'normalized': normalized_text,
            'tokens': basic_tokens,
            'time_matches': time_matches,
            'date_matches': date_matches,
            'location_matches': location_matches,
            'contact_matches': contact_matches,
            'context': self.detect_basic_context(normalized_text)
        }
    
    def pre_normalize_text(self, text: str) -> str:
        """Pre-normalize text according to specifications"""
        import re
        
        # 1. Remove excessive whitespace and unnecessary emojis
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'[😀-🿿]+', '', text)  # Remove emojis
        
        # 2. Convert Thai numerals to Arabic
        for thai, arabic in self.normalization_maps['thai_numerals'].items():
            text = text.replace(thai, arabic)
        
        # 3. Replace abbreviations/slang with standard terms
        for abbr, standard in self.normalization_maps['abbreviations'].items():
            text = text.replace(abbr, standard)
        
        # 4. Apply location aliases (more careful approach)
        for alias, canonical in self.normalization_maps['location_aliases'].items():
            # Only replace if it's a standalone word, not part of another word
            import re
            pattern = r'\b' + re.escape(alias) + r'\b'
            text = re.sub(pattern, canonical, text)
        
        return text.strip()
    
    def tokenize_basic(self, text: str) -> List[str]:
        """Basic tokenization (enhanced when PyThaiNLP available)"""
        if self.use_pythainlp:
            # Will use PyThaiNLP tokenization when available
            try:
                from pythainlp import word_tokenize  # type: ignore[import-not-found]
                return word_tokenize(text, engine='newmm')
            except ImportError:
                pass
        
        # Fallback to simple tokenization
        import re
        # Split by spaces and punctuation but keep Thai words together
        tokens = re.findall(r'[\u0E00-\u0E7F]+|\d+|[a-zA-Z]+|[^\s\u0E00-\u0E7F\da-zA-Z]', text)
        return [token for token in tokens if token.strip()]
    
    def extract_time_patterns(self, text: str) -> List[Dict]:
        """Extract time patterns using comprehensive rules"""
        matches = []
        import re
        
        # 1. Formal time patterns (24-hour)
        for pattern in self.time_patterns['formal']:
            for match in re.finditer(pattern, text):
                hour = int(match.group('h'))
                minute = int(match.group('m')) if 'm' in match.groupdict() and match.group('m') else 0
                
                matches.append({
                    'type': 'time',
                    'category': 'formal',
                    'text': match.group(),
                    'hour': hour,
                    'minute': minute,
                    'start': match.start(),
                    'end': match.end()
                })
        
        # 2. Spoken time patterns
        for pattern in self.time_patterns['spoken']:
            for match in re.finditer(pattern, text):
                time_info = self.parse_spoken_time(match)
                if time_info:
                    matches.append({
                        'type': 'time',
                        'category': 'spoken',
                        'text': match.group(),
                        'hour': time_info['hour'],
                        'minute': time_info['minute'],
                        'start': match.start(),
                        'end': match.end()
                    })
        
        # 3. Special time expressions
        for expr, (hour, minute) in self.time_mappings['expressions'].items():
            if expr in text:
                pos = text.find(expr)
                matches.append({
                    'type': 'time',
                    'category': 'expression',
                    'text': expr,
                    'hour': hour,
                    'minute': minute,
                    'start': pos,
                    'end': pos + len(expr)
                })
        
        return matches
    
    def parse_spoken_time(self, match) -> Dict:
        """Parse spoken time patterns"""
        text = match.group().lower()
        
        # Handle special cases first
        if 'เที่ยงตรง' in text or text == 'เที่ยง':
            return {'hour': 12, 'minute': 0}
        elif 'เที่ยงคืน' in text:
            return {'hour': 0, 'minute': 0}
        
        import re
        
        # Extract hour if present
        hour_match = re.search(r'(\d{1,2})', text)
        hour = int(hour_match.group(1)) if hour_match else None
        
        # Check for half hour
        minute = 30 if 'ครึ่ง' in text else 0
        
        if hour is None:
            # Period-only patterns (ตอนเช้า, etc.)
            for period, (start_h, end_h) in self.time_patterns['period_defaults'].items():
                if period in text:
                    return {'hour': start_h, 'minute': 0}  # Use start of period as default
            return None
        
        # Apply period-specific adjustments - FIXED LOGIC
        if 'บ่าย' in text or 'บ่าย' in match.string[max(0, match.start()-10):match.end()+10]:
            # "บ่าย 3 โมง" or "บ่าย3โมง" -> 15:00
            if hour <= 12:
                hour = hour + 12
        elif 'เย็น' in text:
            # "4 โมงเย็น" -> 16:00
            if hour <= 7:
                hour = hour + 12
        elif 'ทุ่ม' in text:
            # "สามทุ่ม" -> 21:00 (3 + 18)
            hour = hour + 18
        elif 'เช้า' in text:
            # Morning hours - keep as is if reasonable
            if hour > 12:
                hour = hour - 12
        
        # Validate hour range
        if hour >= 24:
            hour = hour - 24
        elif hour < 0:
            hour = hour + 24
        
        return {'hour': hour, 'minute': minute}
    
    def extract_date_patterns(self, text: str) -> List[Dict]:
        """Extract date patterns"""
        matches = []
        
        # Relative days
        for day_text, offset in self.date_patterns['relative_day'].items():
            if day_text in text:
                pos = text.find(day_text)
                matches.append({
                    'type': 'date',
                    'category': 'relative',
                    'text': day_text,
                    'offset_days': offset,
                    'start': pos,
                    'end': pos + len(day_text)
                })
        
        # Weekdays with modifiers
        import re
        weekday_pattern = r'(?:วัน)?(จันทร์|อังคาร|พุธ|พฤหัสบดี|พฤหัส|ศุกร์|เสาร์|อาทิตย์)(?:(นี้|หน้า|ถัดไป|ที่แล้ว))?'
        for match in re.finditer(weekday_pattern, text):
            weekday = match.group(1)
            modifier = match.group(2)  # Don't default to 'หน้า' - let it be None
            
            matches.append({
                'type': 'date',
                'category': 'weekday',
                'text': match.group(),
                'weekday': weekday,
                'modifier': modifier,
                'start': match.start(),
                'end': match.end()
            })

        # --- Thai explicit date patterns (Integrated) ---
        # Extended to include informal forms (มกรา กุมภา มีนา เมษา พฤษภา มิถุนา กรกฎา สิงหา กันยา ตุลา พฤศจิกา ธันวา)
        # Negative lookahead to avoid treating time hour (e.g. 15:30) as year
        thai_date_regex = (
            r'(?:วันที่\s*)?(\d{1,2})\s+'
            r'(ม\.ค\.|ก\.พ\.|มี\.ค\.|เม\.ย\.|พ\.ค\.|มิ\.ย\.|ก\.ค\.|ส\.ค\.|ก\.ย\.|ต\.ค\.|พ\.ย\.|ธ\.ค\.|'
            r'มกราคม|กุมภาพันธ์|มีนาคม|เมษายน|พฤษภาคม|มิถุนายน|กรกฎาคม|สิงหาคม|กันยายน|ตุลาคม|พฤศจิกายน|ธันวาคม|'
            r'มค|กพ|มีค|เมย|พค|มิย|กค|สค|กย|ตค|พย|ธค|'
            r'มกรา|กุมภา|มีนา|เมษา|พฤษภา|มิถุนา|กรกฎา|สิงหา|กันยา|ตุลา|พฤศจิกา|ธันวา)'
            r'(?:\s*(\d{2,4})(?![:\.]))?'
        )
        for m in re.finditer(thai_date_regex, text):
            day_txt, month_txt, year_txt = m.groups()
            try:
                day = int(day_txt)
            except ValueError:
                continue
            month = getattr(self, 'thai_months', {}).get(month_txt)
            if not month:
                continue
            from datetime import datetime as _dt
            now = _dt.now()
            if year_txt:
                year = int(year_txt)
                # Convert 2-digit year
                if year < 100:
                    year += 2000
                # Convert Buddhist Era (BE) to Gregorian if clearly in BE range
                if year >= 2400:  # e.g. 2569
                    year -= 543
            else:
                year = now.year
                if (month < now.month) or (month == now.month and day < now.day):
                    year += 1
            import datetime as _d
            try:
                _d.date(year, month, day)
            except ValueError:
                continue
            matches.append({
                'type': 'date',
                'category': 'thai_date',
                'text': m.group(),
                'day': day,
                'month': month,
                'year': year,
                'start': m.start(),
                'end': m.end()
            })
        
        return matches
    
    def extract_location_patterns(self, text: str) -> List[Dict]:
        """Extract location patterns using enhanced rules - improved to avoid contamination"""
        matches = []
        import re
        
        # Enhanced location patterns with "ที่" prefix support (Thai character support)
        # More restrictive to avoid contamination
        general_location_patterns = [
            r'ที่ร้าน[\w\u0e00-\u0e7f]*(?=\s|$|กับ|[,.])',               # ที่ร้าน (stop at กับ, space, end, punctuation)
            r'ที่บ้าน[\w\u0e00-\u0e7f]*(?=\s|$|กับ|[,.])',               # ที่บ้าน
            r'ที่งาน[\w\u0e00-\u0e7f]*(?=\s|$|กับ|[,.])',                # ที่งาน
            r'ที่สวน[\w\u0e00-\u0e7f]*(?=\s|$|กับ|[,.])',                # ที่สวน
            r'ที่ตลาด[\w\u0e00-\u0e7f]*(?=\s|$|กับ|[,.])',               # ที่ตลาด
            r'ที่สนาม[\w\u0e00-\u0e7f]*(?=\s|$|กับ|[,.])',               # ที่สนาม
            r'ที่โรงเรียน[\w\u0e00-\u0e7f]*(?=\s|$|กับ|[,.])',           # ที่โรงเรียน
            r'ที่มหาวิทยาลัย[\w\u0e00-\u0e7f]*(?=\s|$|กับ|[,.])',        # ที่มหาวิทยาลัย
            r'ที่คาเฟ่[\w\u0e00-\u0e7f]*(?=\s|$|กับ|[,.])',              # ที่คาเฟ่
            r'ที่ห้าง[\w\u0e00-\u0e7f]*(?=\s|$|กับ|[,.])',               # ที่ห้าง (stop before กับ)
        ]
        
        # Check for general location patterns first
        for pattern in general_location_patterns:
            for match in re.finditer(pattern, text):
                location = match.group().strip()  # Get full match including "ที่"
                if location and len(location) > 3:
                    matches.append({
                        'type': 'location',
                        'category': 'general_with_prefix',
                        'text': location,
                        'start': match.start(),
                        'end': match.end()
                    })
        
        # Connector-based locations (more flexible) - also add stop conditions
        for pattern in self.location_patterns['connectors']:
            # Modify pattern to add stop conditions
            modified_pattern = pattern.replace(')', r')(?=\s|$|กับ|[,.])')
            for match in re.finditer(modified_pattern, text):
                location = match.group(1).strip()
                if location and len(location) > 1:
                    matches.append({
                        'type': 'location',
                        'category': 'general',
                        'text': location,
                        'start': match.start(),
                        'end': match.end()
                    })
        
        # Look for location words without connectors (for cases like "เซ็นทรัลลาดพร้าว")
        location_keywords = [
            r'(เซ็นทรัล[^\s]*)',
            r'(สยาม[^\s]*)',
            r'(เอ็มบีเค)',
            r'(MBK)',
            r'([^\s]*ห้าง[^\s]*)',
            r'([^\s]*พลาซ่า[^\s]*)',
            r'([^\s]*มอลล์[^\s]*)'
        ]
        
        for pattern in location_keywords:
            for match in re.finditer(pattern, text):
                location = match.group(1).strip()
                if location and len(location) > 2:
                    matches.append({
                        'type': 'location',
                        'category': 'mall',
                        'text': location,
                        'start': match.start(),
                        'end': match.end()
                    })
        
        # Specific location patterns
        for pattern in self.location_patterns['specific']:
            for match in re.finditer(pattern, text):
                location = match.group(1).strip() if match.groups() else match.group().strip()
                if location:
                    category = 'hospital' if any(word in pattern for word in ['โรงพยาบาล', 'รพ', 'คลินิก']) else 'specific'
                    matches.append({
                        'type': 'location', 
                        'category': category,
                        'text': location,
                        'start': match.start(),
                        'end': match.end()
                    })

        # --- English location detection (added) ---
        # 1) Connector-based: at/in + Capitalized phrase (1-5 tokens)
        english_conn_regex = r'\b(?:at|in)\s+([A-Z][A-Za-z0-9&\-]*(?:\s+[A-Z][A-Za-z0-9&\-]*){0,4})'
        for m in re.finditer(english_conn_regex, text):
            phrase = m.group(1).strip()
            # Basic filtering: ignore if looks like a time or too short
            if len(phrase) < 3:
                continue
            if re.match(r'^[A-Z]\d+$', phrase):  # e.g., A1
                continue
            # Avoid duplicates (overlap with existing matches)
            if any(abs(m.start() - ex['start']) < 2 and ex['text'] == phrase for ex in matches):
                continue
            matches.append({
                'type': 'location',
                'category': 'english',
                'text': phrase,
                'start': m.start(),
                'end': m.end()
            })

        # 2) Known English location names without connector
        known_english_places = [
            'CentralWorld', 'Central Plaza', 'Siam Paragon', 'MBK', 'Terminal 21',
            'Bangkok Hospital', 'Samitivej', 'Samitivej Hospital', 'ICONSIAM',
            'EmQuartier', 'Emporium', 'Union Mall', 'Suvarnabhumi', 'Don Mueang', 'Don Muang',
            'Mega Bangna', 'Future Park'
        ]
        # Build regex that tolerates optional spaces in multi-word names
        place_pattern = r'(' + '|'.join([re.escape(p) for p in known_english_places]) + r')'
        for m in re.finditer(place_pattern, text):
            phrase = m.group(1).strip()
            if not any(m.start() == ex['start'] and ex['text'] == phrase for ex in matches):
                matches.append({
                    'type': 'location',
                    'category': 'english_known',
                    'text': phrase,
                    'start': m.start(),
                    'end': m.end()
                })
        
        return matches
    
    def extract_contact_patterns(self, text: str) -> List[Dict]:
        """Extract contact patterns"""
        matches = []
        import re
        
        # Phone patterns
        phone_patterns = [
            r'(\+66\s?\d{1,2}\s?\d{3,4}\s?\d{4})',
            r'(0\d{2}-?\d{3}-?\d{4})',
            r'(0\d{1}-?\d{3}-?\d{4})',
            r'(\d{3}-?\d{3}-?\d{4})'
        ]
        
        for pattern in phone_patterns:
            for match in re.finditer(pattern, text):
                matches.append({
                    'type': 'contact',
                    'category': 'phone',
                    'text': match.group(1),
                    'start': match.start(),
                    'end': match.end()
                })
        
        return matches
    
    def preprocess_text_advanced(self, text: str) -> Dict[str, Any]:
        """
        Advanced text preprocessing with PyThaiNLP
        (เมื่อพร้อมใส่ PyThaiNLP)
        """
        if not self.use_pythainlp:
            return self.preprocess_text_basic(text)
        
        # จะใส่ PyThaiNLP logic ตรงนี้
        """
        # 1. Normalize text
        normalized = normalize(text)
        
        # 2. Word tokenization
        tokens = word_tokenize(normalized, engine='newmm')
        
        # 3. POS tagging
        pos_tags = pos_tag(tokens, engine='perceptron')
        
        # 4. Named entity recognition
        entities = named_entity(normalized)
        
        # 5. Extract stopwords
        stopwords = thai_stopwords()
        filtered_tokens = [token for token in tokens if token not in stopwords]
        
        return {
            'original': text,
            'normalized': normalized,
            'tokens': tokens,
            'filtered_tokens': filtered_tokens,
            'pos_tags': pos_tags,
            'entities': entities,
            'context': self.detect_advanced_context(pos_tags, entities)
        }
        """
        pass
    
    def convert_thai_numerals(self, text: str) -> str:
        """แปลงเลขไทยเป็นอารบิก"""
        mapping = getattr(self, 'thai_numerals', None)
        if mapping is None:
            mapping = self.normalization_maps.get('thai_numerals', {})
        for thai, arabic in mapping.items():
            text = text.replace(thai, arabic)
        return text
    
    def extract_basic_patterns(self, text: str, pattern_type: str) -> List[Dict]:
        """Extract patterns โดยไม่ใช้ PyThaiNLP"""
        matches = []
        
        if pattern_type == 'time':
            patterns = self.time_patterns
        elif pattern_type == 'location':
            patterns = self.location_patterns
        elif pattern_type == 'contact':
            patterns = self.contact_patterns
        else:
            return matches
        
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                for match in re.finditer(pattern, text):
                    matches.append({
                        'type': pattern_type,
                        'category': category,
                        'text': match.group(),
                        'start': match.start(),
                        'end': match.end()
                    })
        
        return matches
    
    def detect_basic_context(self, text: str) -> Dict[str, Any]:
        """ตรวจจับบริบทแบบ basic"""
        context = {
            'type': 'general',
            'medical_score': 0,
            'business_score': 0,
            'urgency': 'normal',
            'formality': 'neutral'
        }
        
        # Check medical context
        for category, keywords in self.medical_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    context['medical_score'] += 1
        
        # Check business context
        for category, keywords in self.business_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    context['business_score'] += 1
        
        # Determine primary context
        if context['medical_score'] > context['business_score']:
            context['type'] = 'medical'
        elif context['business_score'] > context['medical_score']:
            context['type'] = 'business'
        
        return context
    
    def extract_smart_datetime(self, processed_text: Dict) -> Optional[datetime]:
        """
        Extract datetime using enhanced rules
        """
        from datetime import datetime, timedelta
        import calendar
        
        # Get matches
        time_matches = processed_text.get('time_matches', [])
        date_matches = processed_text.get('date_matches', [])
        
        # Start with current date/time
        now = datetime.now()
        target_date = now.date()
        target_time = None
        
        # Process date matches
        for date_match in date_matches:
            if date_match.get('category') == 'thai_date':
                try:
                    target_date = datetime(
                        date_match['year'],
                        date_match['month'],
                        date_match['day']
                    ).date()
                    # Explicit date found; stop processing further date matches
                    break
                except Exception:
                    pass
            if date_match['category'] == 'relative':
                # วันนี้, พรุ่งนี้, etc.
                offset = date_match['offset_days']
                target_date = now.date() + timedelta(days=offset)
                
            elif date_match['category'] == 'weekday':
                # วันจันทร์หน้า, etc.
                weekday_name = date_match['weekday']
                modifier = date_match['modifier']
                
                # Map weekday name to number
                weekday_map = self.date_patterns['weekday']
                if weekday_name in weekday_map:
                    target_weekday = weekday_map[weekday_name]
                    
                    # For Thai context: when no modifier specified, find next occurrence
                    if modifier == 'หน้า':
                        week_offset = 1  # Next week explicitly
                    elif modifier == 'นี้':
                        week_offset = 0  # This week
                    elif modifier is None:
                        # No modifier - find next occurrence of this weekday
                        week_offset = 0  # Use logic in _calculate_weekday_date to find next occurrence
                    else:
                        week_offset = 0  # Default to current logic
                    
                    # Calculate target date
                    target_date = self._calculate_weekday_date(now.date(), target_weekday, week_offset)
        
        # Process time matches
        for time_match in time_matches:
            hour = time_match.get('hour')
            minute = time_match.get('minute', 0)
            
            if hour is not None:
                target_time = (hour, minute)
                break  # Use first valid time match
        
        # Default time if no time specified
        if target_time is None:
            target_time = (9, 0)  # Default to 9:00 AM
        
        # Combine date and time
        try:
            result_datetime = datetime.combine(target_date, datetime.min.time().replace(
                hour=target_time[0], minute=target_time[1]
            ))
            
            # Post-validate: don't allow past dates (adjust to next week if needed)
            if result_datetime < now:
                if result_datetime.date() == now.date():
                    # Same day but past time - keep it (might be intentional)
                    pass
                else:
                    # Past date - move to next week
                    result_datetime += timedelta(weeks=1)
            
            return result_datetime
            
        except ValueError:
            # Invalid datetime combination
            return None
    
    def _calculate_weekday_date(self, base_date, target_weekday: int, week_offset: int = 0):
        """Calculate date for specific weekday"""
        from datetime import timedelta
        
        # Current weekday (0=Monday, 6=Sunday)
        current_weekday = base_date.weekday()
        
        # Days until target weekday
        days_ahead = target_weekday - current_weekday
        
        # Adjust for week offset
        if week_offset == 0:  # This week
            if days_ahead <= 0:  # Target day already passed this week
                days_ahead += 7  # Move to next week
        elif week_offset == 1:  # Next week
            if days_ahead <= 0:
                days_ahead += 7  # Next occurrence
            # For Thai context: when saying "พฤหัส" (Thursday), usually mean next Thursday
            # So if today is Monday and we say "พฤหัส", we mean this Thursday (not next week)
            # But if today is Friday, we mean next Thursday
            pass  # Keep days_ahead as calculated
        elif week_offset == -1:  # Last week
            days_ahead -= 7
        
        return base_date + timedelta(days=days_ahead)
    
    def _end_of_month(self, date):
        """Get end of month date"""
        from datetime import datetime
        import calendar
        last_day = calendar.monthrange(date.year, date.month)[1]
        return date.replace(day=last_day)
    
    def _start_of_month(self, date):
        """Get start of month date"""
        return date.replace(day=1)
    
    def _next_month(self, date):
        """Get date in next month"""
        from datetime import datetime
        if date.month == 12:
            return date.replace(year=date.year + 1, month=1)
        else:
            return date.replace(month=date.month + 1)
    
    def extract_smart_location(self, processed_text: Dict) -> str:
        """
        Extract location อย่างฉลาด แยกแยะระหว่าง location และ building_dept
        ไม่เอาเวลาและบุคคลมาปน
        """
        location_matches = processed_text.get('location_matches', [])
        text = processed_text.get('normalized', '')
        
        # First, check if we already found building/department info
        building_dept = self.extract_building_department(processed_text)
        
        # First try to get from location matches
        if location_matches:
            context = processed_text.get('context', {})
            if context.get('type') == 'medical':
                for match in location_matches:
                    if match['category'] == 'hospital':
                        return self.clean_location_text(match['text'])
            
            # Return first general location that's not building-specific
            for match in location_matches:
                location = match['text']
                # Skip very short or obviously wrong locations
                if len(location) > 2 and not any(word in location.lower() for word in ['บ่าย', 'เช้า', 'โมง']):
                    # If we have building_dept, skip building-specific terms in location
                    if building_dept:
                        building_terms = ['อาคาร', 'ชั้น', 'แผนก', 'ห้อง', 'ตึก', 'โซน', 'ฝ่าย', 'สำนักงาน', 'ศูนย์']
                        if not any(term in location for term in building_terms):
                            return self.clean_location_text(location)
                    else:
                        return self.clean_location_text(location)
        
        # If no good location found from matches, try manual extraction
        # Look for "ที่" + general places (not building-specific)
        import re
        general_place_patterns = [
            r'ที่ร้าน[\w\u0e00-\u0e7f]*',               # ที่ร้าน, ที่ร้านกาแฟ
            r'ที่บ้าน[\w\u0e00-\u0e7f]*',               # ที่บ้าน, ที่บ้านเพื่อน
            r'ที่งาน[\w\u0e00-\u0e7f]*',                # ที่งาน, ที่งานแต่ง
            r'ที่สวน[\w\u0e00-\u0e7f]*',                # ที่สวน, ที่สวนสาธารณะ
            r'ที่ตลาด[\w\u0e00-\u0e7f]*',               # ที่ตลาด, ที่ตลาดนัด
            r'ที่สนาม[\w\u0e00-\u0e7f]*',               # ที่สนาม, ที่สนามกีฬา
            r'ที่โรงเรียน[\w\u0e00-\u0e7f]*',           # ที่โรงเรียน
            r'ที่มหาวิทยาลัย[\w\u0e00-\u0e7f]*',        # ที่มหาวิทยาลัย
            r'ที่คาเฟ่[\w\u0e00-\u0e7f]*',              # ที่คาเฟ่
        ]
        
        for pattern in general_place_patterns:
            match = re.search(pattern, text)
            if match:
                return self.clean_location_text(match.group().strip())
        
        return ""
    
    def clean_location_text(self, location_text: str) -> str:
        """Clean location text from time and person contamination"""
        import re
        
        # Remove time-related suffixes
        cleaned = re.sub(r'(บ่าย|เช้า|เย็น|ค่ำ|\d{1,2}[:.]?\d{0,2}|โมง|นาที|นาฬิกา).*$', '', location_text).strip()
        
        # Remove person indicators - if "กับ" appears, everything after it is person
        if 'กับ' in cleaned:
            cleaned = cleaned.split('กับ')[0].strip()
        
        # Remove weekday references
        cleaned = re.sub(r'(จันทร์|อังคาร|พุธ|พฤหัส|พฤหัสบดี|ศุกร์|เสาร์|อาทิตย์).*$', '', cleaned).strip()
        
        return cleaned
    
    def extract_appointment_info(self, text: str) -> Dict[str, Any]:
        """
        Main method สำหรับ extract ข้อมูลนัดหมาย
        """
        # Preprocess text
        processed = self.preprocess_text_basic(text)  # หรือ advanced เมื่อพร้อม
        
        # Extract components
        appointment_datetime = self.extract_smart_datetime(processed)
        location = self.extract_smart_location(processed)
        context = processed.get('context', {})
        
        # Extract appointment title
        appointment_title = self.extract_appointment_title(processed)
        
        # Extract contact person
        contact_person = self.extract_contact_person(processed)
        
        # Extract phone number
        phone_number = self.extract_phone_number(processed)
        
        # Extract building/department/floor
        building_dept = self.extract_building_department(processed)
        
        return {
            'original_text': text,
            'appointment_title': appointment_title,
            'datetime': appointment_datetime,
            'date': appointment_datetime.strftime('%d/%m/%Y') if appointment_datetime else '',
            'time': appointment_datetime.strftime('%H.%M') if appointment_datetime else '',
            'location': location,
            'building_dept': building_dept,
            'contact_person': contact_person,
            'phone_number': phone_number,
            'context': context,
            'confidence': self.calculate_confidence(processed),
            'processed_data': processed  # สำหรับ debug
        }
    
    def extract_appointment_title(self, processed_text: Dict) -> str:
        """Extract appointment title/activity (clean of date/time/location)."""
        import re
        text = processed_text.get('normalized', '')

        # 1. Remove command prefixes
        for command in self.command_patterns['add_appointment']:
            text = text.replace(command, ' ').strip()

        activity_text = text

        # 2. Remove explicit time patterns
        time_removal_patterns = [
            r'\b\d{1,2}[:.]\d{2}\b\s*(น\.|นาฬิกา)?',
            r'\b\d{1,2}\s*นาฬิกา\b',
            r'\b\d{1,2}\s*โมง(?:เช้า|เย็น|ตรง)?',
            r'\b\d{1,2}\s*ทุ่ม(?:ครึ่ง)?',
            r'(?:ตอน)?(?:เช้า|บ่าย|เย็น|ค่ำ|กลางวัน|กลางคืน)\s*\d*',
        ]
        for pattern in time_removal_patterns:
            activity_text = re.sub(pattern, ' ', activity_text)

        # 3. Remove weekdays & relative words
        activity_text = re.sub(r'(?:วัน)?(?:จันทร์|อังคาร|พุธ|พฤหัสบดี|พฤหัส|ศุกร์|เสาร์|อาทิตย์)(?:นี้|หน้า|ถัดไป|ที่แล้ว)?', ' ', activity_text)
        activity_text = re.sub(r'(พรุ่งนี้|มะรืนนี้|วันนี้|เมื่อวาน|ปีหน้า|เดือนหน้า|สัปดาห์หน้า)', ' ', activity_text)

        # 4. Remove parsed date substrings
        for dm in processed_text.get('date_matches', []):
            t = dm.get('text', '')
            if t:
                activity_text = activity_text.replace(t, ' ')
        activity_text = re.sub(r'วันที่', ' ', activity_text)

        # 5. Remove orphan word 'เวลา'
        activity_text = re.sub(r'\bเวลา\b', ' ', activity_text)

        # 6. Remove contact marker + name (leave contact for separate field)
        activity_text = re.sub(r'กับ\S+', ' ', activity_text)

        # 7. Remove obvious trailing location phrases
        activity_text = re.sub(r'(?:ที่|ใน|ต่อ|ไป)(?:โรงพยาบาล|ห้าง|ร้าน|สถานี|ที่|คลินิก).*$', ' ', activity_text)

        # 8. Remove detected locations (Thai/English)
        for loc in processed_text.get('location_matches', []):
            loc_text = loc.get('text', '')
            if loc_text:
                activity_text = activity_text.replace(loc_text, ' ')
        # English connectors
        activity_text = re.sub(r'\b(?:at|in|to)\b', ' ', activity_text, flags=re.IGNORECASE)

        # 9. Cleanup punctuation & spaces
        activity_text = re.sub(r'[,;.]+', ' ', activity_text)
        activity_text = re.sub(r'\s+', ' ', activity_text).strip()

        return activity_text if activity_text else 'นัดหมาย'
    
    def extract_contact_person(self, processed_text: Dict) -> str:
        """Extract contact person - improved to avoid time/location contamination"""
        text = processed_text.get('normalized', '')
        
        import re
        
        # Find all "กับ[person]" patterns with better boundaries
        contacts = []
        
        # Method 1: More precise pattern - stop at "ที่", time words, or weekdays
        contact_pattern = r'กับ([^\s]+?)(?=\s*ที่|บ่าย|เช้า|เย็น|ค่ำ|โมง|นาที|จันทร์|อังคาร|พุธ|พฤหัส|ศุกร์|เสาร์|อาทิตย์|พรุ่งนี้|มะรืนนี้|วันนี้|\d+|$)'
        
        matches = re.findall(contact_pattern, text)
        
        for contact in matches:
            # Clean up the contact name
            cleaned_contact = contact.strip()
            
            # Remove any remaining time/location indicators but be more conservative
            if any(word in cleaned_contact for word in ['บ่าย', 'เช้า', 'เย็น', 'ค่ำ', 'โมง', 'นาที']):
                cleaned_contact = re.sub(r'(บ่าย|เช้า|เย็น|ค่ำ|โมง|นาที|นาฬิกา).*$', '', cleaned_contact).strip()
            
            if any(word in cleaned_contact for word in ['พรุ่งนี้', 'มะรืนนี้', 'วันนี้', 'หน้า', 'นี้']):
                cleaned_contact = re.sub(r'(พรุ่งนี้|มะรืนนี้|วันนี้|หน้า|นี้).*$', '', cleaned_contact).strip()
            
            # Only add if it's a reasonable length and doesn't contain obvious location/time words
            if cleaned_contact and len(cleaned_contact) > 0:
                # Skip if it contains obvious location/time words
                problematic_words = ['ร้าน', 'ห้าง', 'ตึก', 'อาคาร', 'ชั้น', 'แผนก', 'ห้อง', 'สนาม', 
                                   'โรงเรียน', 'โรงพยาบาล', 'โมง', 'นาที']
                if not any(word in cleaned_contact for word in problematic_words):
                    contacts.append(cleaned_contact)
        
        # Method 2: If no contacts found, try a simpler pattern but clean more aggressively
        if not contacts:
            simple_pattern = r'กับ(\S+?)(?:\s|$)'
            simple_matches = re.findall(simple_pattern, text)
            
            for contact in simple_matches:
                cleaned_contact = contact.strip()
                
                # Stop at "ที่" if present
                if 'ที่' in cleaned_contact:
                    cleaned_contact = cleaned_contact.split('ที่')[0].strip()
                
                # Remove time/date suffixes
                cleaned_contact = re.sub(r'(บ่าย|เช้า|เย็น|ค่ำ|โมง|นาที|พรุ่งนี้|มะรืนนี้|วันนี้|หน้า|นี้).*$', '', cleaned_contact).strip()
                
                if cleaned_contact and len(cleaned_contact) > 0:
                    # Less strict filtering for simple pattern
                    if not any(word in cleaned_contact for word in ['ร้าน', 'ห้าง', 'ตึก', 'อาคาร', 'ชั้น', 'โมง']):
                        contacts.append(cleaned_contact)
        
        # Return joined contacts or empty string
        return ', '.join(contacts) if contacts else ""
    
    def extract_phone_number(self, processed_text: Dict) -> str:
        """Extract phone number"""
        contact_matches = processed_text.get('contact_matches', [])
        
        for match in contact_matches:
            if match['category'] == 'phone':
                return match['text']
        
        return ""
    
    def extract_building_department(self, processed_text: Dict) -> str:
        """Extract building/department/floor info"""
        text = processed_text.get('normalized', '')
        
        import re
        
        # Enhanced patterns for building/department/floor - more specific
        building_patterns = [
            r'ที่อาคาร[\w\u0e00-\u0e7f]*',               # ที่อาคาร, ที่อาคารA (support Thai characters)
            r'ที่ชั้น\d+',                                # ที่ชั้น1, ที่ชั้น2
            r'ที่แผนก[\w\u0e00-\u0e7f]+',               # ที่แผนกการเงิน (support Thai characters)
            r'ที่ห้อง[\w\u0e00-\u0e7f]+',               # ที่ห้องประชุม (support Thai characters)
            r'ที่ตึก[\w\u0e00-\u0e7f]*',                # ที่ตึก, ที่ตึกA (support Thai characters)
            r'ที่โซน[\w\u0e00-\u0e7f]*',                # ที่โซนA (support Thai characters)
            r'ที่ฝ่าย[\w\u0e00-\u0e7f]+',               # ที่ฝ่ายขาย (support Thai characters)
            r'ที่สำนักงาน[\w\u0e00-\u0e7f]*',           # ที่สำนักงาน (support Thai characters)
            r'ที่ศูนย์[\w\u0e00-\u0e7f]+',              # ที่ศูนย์ประชุม (support Thai characters)
            r'อาคาร[\w\u0e00-\u0e7f]*',                 # อาคารA (without ที่, support Thai characters)
            r'ชั้น\d+',                                  # ชั้น1 (without ที่)
            r'แผนก[\w\u0e00-\u0e7f]+',                 # แผนกการเงิน (without ที่, support Thai characters)
            r'ห้อง[\w\u0e00-\u0e7f]+',                 # ห้องประชุม (without ที่, support Thai characters)
        ]
        
        for pattern in building_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group().strip()
        
        return ""
    
    def calculate_confidence(self, processed_text: Dict) -> float:
        """
        Calculate confidence score based on field extraction and source quality
        """
        confidence = 0.0
        max_confidence = 1.0
        
        # Base confidence from found patterns
        time_matches = processed_text.get('time_matches', [])
        date_matches = processed_text.get('date_matches', [])
        location_matches = processed_text.get('location_matches', [])
        contact_matches = processed_text.get('contact_matches', [])
        
        # Time confidence (0.4 max)
        if time_matches:
            time_confidence = 0.0
            for match in time_matches:
                if match['category'] == 'formal':
                    time_confidence = max(time_confidence, 0.4)  # Highest confidence
                elif match['category'] == 'spoken':
                    time_confidence = max(time_confidence, 0.3)  # Good confidence
                elif match['category'] == 'expression':
                    time_confidence = max(time_confidence, 0.35) # Very good confidence
            confidence += time_confidence
        
        # Date confidence (0.25 max)
        if date_matches:
            date_confidence = 0.0
            for match in date_matches:
                if match['category'] == 'relative':
                    date_confidence = max(date_confidence, 0.25)  # Good confidence
                elif match['category'] == 'weekday':
                    date_confidence = max(date_confidence, 0.2)   # Decent confidence
            confidence += date_confidence
        
        # Location confidence (0.2 max)
        if location_matches:
            location_confidence = 0.0
            for match in location_matches:
                if match['category'] == 'specific':
                    location_confidence = max(location_confidence, 0.2)  # Highest for specific
                elif match['category'] == 'hospital':
                    location_confidence = max(location_confidence, 0.18) # High for medical
                else:
                    location_confidence = max(location_confidence, 0.15) # General location
            confidence += location_confidence
        
        # Contact confidence (0.15 max)
        if contact_matches:
            contact_confidence = 0.0
            for match in contact_matches:
                if match['category'] == 'phone':
                    contact_confidence = max(contact_confidence, 0.15)
            confidence += contact_confidence
        
        # Context understanding bonus (up to 0.1)
        context = processed_text.get('context', {})
        if context.get('type') != 'general':
            confidence += 0.05  # Bonus for understanding context
        
        # Field completeness bonus
        fields_found = 0
        if time_matches: fields_found += 1
        if date_matches: fields_found += 1  
        if location_matches: fields_found += 1
        if contact_matches: fields_found += 1
        
        # Bonus for multiple fields (shows comprehensive understanding)
        if fields_found >= 3:
            confidence += 0.1
        elif fields_found >= 2:
            confidence += 0.05
        
        return min(confidence, max_confidence)

# Example usage class สำหรับ testing
class ParserExample:
    """ตัวอย่างการใช้งาน Enhanced Parser"""
    
    def __init__(self):
        self.parser = EnhancedSmartDateTimeParser()
    
    def test_basic_parsing(self):
        """ทดสอบ basic parsing"""
        test_cases = [
            "นัดพรุ่งนี้ 14.30 น. ที่โรงพยาบาลศิริราช",
            "ประชุมวันพุธหน้า 2 โมงเย็น ห้องประชุม A",
            "ไปหาหมอสมชาย วันที่ ๑๕ กุมภาพันธ์ เวลา ๑๐.๓๐ น.",
            "นัดตรวจตอนเช้า คลินิกหัวใจ รพ.จุฬา"
        ]
        
        for text in test_cases:
            print(f"\nTesting: {text}")
            result = self.parser.extract_appointment_info(text)
            print(f"Result: {result}")
    
    def test_context_detection(self):
        """ทดสอบการตรวจจับบริบท"""
        contexts = [
            ("ไปหาหมอตรวจหัวใจ", "medical"),
            ("ประชุมคณะกรรมการ", "business"),
            ("เจอกันที่ห้างสรรพสินค้า", "general")
        ]
        
        for text, expected in contexts:
            processed = self.parser.preprocess_text_basic(text)
            actual = processed['context']['type']
            print(f"{text} -> {actual} (expected: {expected})")

# ฟังก์ชันสำหรับ testing
def run_examples():
    """รัน examples ทั้งหมด"""
    example = ParserExample()
    
    print("=== Testing Basic Parsing ===")
    example.test_basic_parsing()
    
    print("\n=== Testing Context Detection ===")
    example.test_context_detection()

if __name__ == "__main__":
    run_examples()
