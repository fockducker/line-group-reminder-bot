"""
Google Sheets Repository for LINE Group Reminder Bot
จัดการการเชื่อมต่อและดำเนินการ CRUD กับ Google Sheets
รองรับการแยกข้อมูล Personal และ Group
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import gspread
from google.oauth2.service_account import Credentials
from .models import Appointment

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SheetsRepository:
    """
    Repository class สำหรับจัดการข้อมูลการนัดหมายใน Google Sheets
    รองรับการแยกข้อมูล Personal และ Group Context
    """
    
    def __init__(self, spreadsheet_id: str = None):
        """
        Initialize SheetsRepository
        
        Args:
            spreadsheet_id (str): Google Sheets Spreadsheet ID
        """
        self.spreadsheet_id = spreadsheet_id or os.getenv('GOOGLE_SPREADSHEET_ID')
        self.gc = None
        self.spreadsheet = None
        self._initialize_connection()
        logger.info(f"SheetsRepository initialized with spreadsheet_id: {self.spreadsheet_id}")
    
    def _initialize_connection(self):
        """เชื่อมต่อกับ Google Sheets API"""
        try:
            # ตรวจสอบว่ามี credentials หรือไม่
            credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
            if not credentials_json:
                logger.error("GOOGLE_CREDENTIALS_JSON environment variable not found!")
                logger.error("Available env vars: " + str(list(os.environ.keys())))
                return
            
            logger.info(f"Found credentials JSON (length: {len(credentials_json)} chars)")
            
            # ตรวจสอบ spreadsheet_id
            if not self.spreadsheet_id:
                logger.error("GOOGLE_SPREADSHEET_ID environment variable not found!")
                return
            
            logger.info(f"Using spreadsheet ID: {self.spreadsheet_id}")
            
            # Parse credentials จาก environment variable
            credentials_data = json.loads(credentials_json)
            
            # กำหนด scope ที่ต้องการ
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # สร้าง credentials object
            credentials = Credentials.from_service_account_info(
                credentials_data, scopes=scopes
            )
            
            # เชื่อมต่อ gspread
            self.gc = gspread.authorize(credentials)
            
            if self.spreadsheet_id:
                self.spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
                logger.info("Successfully connected to Google Sheets")
            else:
                logger.warning("No spreadsheet ID provided")
                
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets connection: {e}")
            self.gc = None
            self.spreadsheet = None
    
    def _get_worksheet(self, context: str):
        """
        รับ worksheet ตาม context
        
        Args:
            context (str): บริบท ('personal' หรือ 'group_{group_id}' หรือ 'appointments_group_{group_id}')
            
        Returns:
            gspread.Worksheet หรือ None
        """
        if not self.spreadsheet:
            return None
            
        try:
            # ตรวจสอบว่า context ขึ้นต้นด้วย "appointments_" หรือไม่
            if context.startswith("appointments_"):
                worksheet_name = context  # ใช้ชื่อที่ส่งมาเลย
            else:
                worksheet_name = f"appointments_{context}"  # เพิ่ม prefix สำหรับ context เก่า
            
            # หา worksheet หรือสร้างใหม่ถ้าไม่มี
            try:
                worksheet = self.spreadsheet.worksheet(worksheet_name)
            except gspread.WorksheetNotFound:
                # สร้าง worksheet ใหม่พร้อม header
                worksheet = self.spreadsheet.add_worksheet(
                    title=worksheet_name, 
                    rows=1000, 
                    cols=10
                )
                # เพิ่ม header row
                headers = [
                    'id', 'group_id', 'datetime_iso', 'location', 'building_floor_dept',
                    'contact_person', 'phone_number', 'note', 'lead_days', 'notified_flags',
                    'created_at', 'updated_at'
                ]
                worksheet.append_row(headers)
                logger.info(f"Created new worksheet: {worksheet_name}")
            
            return worksheet
            
        except Exception as e:
            logger.error(f"Error getting worksheet for context {context}: {e}")
            return None

    def add_appointment(self, appointment: Appointment) -> bool:
        """
        เพิ่มการนัดหมายใหม่ลงใน Google Sheets
        
        Args:
            appointment (Appointment): ข้อมูลการนัดหมายที่จะเพิ่ม
        
        Returns:
            bool: True หากเพิ่มสำเร็จ, False หากมีปัญหา
        """
        if not self.gc:
            logger.warning("Google Sheets not connected, cannot add appointment")
            return False
        
        try:
            # กำหนด context ตาม group_id
            if appointment.group_id and appointment.group_id.startswith('C'):
                # LINE Group ID เริ่มต้นด้วย 'C'
                context = f"group_{appointment.group_id}"
            else:
                # Personal appointment
                context = "personal"
            
            logger.info(f"Determined context: {context} for group_id: {appointment.group_id}")
            
            worksheet = self._get_worksheet(context)
            if not worksheet:
                logger.error(f"Cannot get worksheet for context: {context}")
                return False
            
            # แปลง Appointment object เป็น row data ตาม headers ใหม่
            row_data = [
                appointment.id,
                appointment.group_id,
                appointment.datetime_iso,
                appointment.location,  # ใช้ชื่อใหม่แทน hospital
                appointment.building_floor_dept,  # ใช้ชื่อใหม่แทน department
                appointment.contact_person,  # ใช้ชื่อใหม่แทน doctor
                appointment.phone_number,  # เพิ่ม phone_number
                appointment.note,
                str(appointment.lead_days),  # Convert list to string
                str(appointment.notified_flags),  # Convert list to string
                appointment.created_at,
                appointment.updated_at
            ]
            
            # เพิ่มข้อมูลลงใน worksheet
            worksheet.append_row(row_data)
            logger.info(f"Successfully added appointment ID: {appointment.id} for group: {appointment.group_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding appointment: {e}", exc_info=True)
            return False

    def get_appointments(self, user_id: str, context: str) -> List[Appointment]:
        """
        ดึงรายการนัดหมายของผู้ใช้
        
        Args:
            user_id (str): LINE User ID
            context (str): บริบท ('personal' หรือ 'group_{group_id}')
            
        Returns:
            List[Appointment]: รายการนัดหมาย
        """
        if not self.gc:
            logger.warning("Google Sheets not connected, returning empty list")
            return []
        
        try:
            worksheet = self._get_worksheet(context)
            if not worksheet:
                return []
            
            # ดึงข้อมูลทั้งหมดจาก worksheet
            try:
                records = worksheet.get_all_records()
            except Exception as e:
                if "header row in the worksheet is not unique" in str(e):
                    logger.error("Duplicate headers detected in worksheet. Attempting to fix...")
                    # ลองใช้วิธีแก้ไขโดยการอ่านข้อมูลแบบ manual
                    return self._get_appointments_manual_headers(worksheet, user_id, context)
                else:
                    raise e
            
            appointments = []
            for record in records:
                # ตรวจสอบว่าตรงกับ group_id ที่ต้องการหรือไม่
                # สำหรับ group: user_id จะเป็น group_id จริง
                # สำหรับ personal: user_id จะเป็น user_id จริง
                if record.get('group_id') == user_id:
                    try:
                        # สร้าง Appointment object จากข้อมูล
                        # Parse lead_days และ notified_flags จาก string
                        lead_days = eval(record.get('lead_days', '[7, 3, 1]'))
                        notified_flags = eval(record.get('notified_flags', '[False, False, False]'))
                        
                        appointment = Appointment(
                            id=record.get('id'),
                            group_id=record.get('group_id'),
                            datetime_iso=record.get('datetime_iso'),
                            location=record.get('location', record.get('hospital', '')),  # Backward compatibility
                            building_floor_dept=record.get('building_floor_dept', record.get('department', '')),  # Backward compatibility
                            contact_person=record.get('contact_person', record.get('doctor', '')),  # Backward compatibility
                            phone_number=record.get('phone_number', ''),
                            note=record.get('note', ''),
                            lead_days=lead_days,
                            notified_flags=notified_flags,
                            created_at=record.get('created_at', ''),
                            updated_at=record.get('updated_at', '')
                        )
                        appointments.append(appointment)
                    except Exception as e:
                        logger.error(f"Error parsing appointment record: {e}")
                        continue
            
            logger.info(f"Retrieved {len(appointments)} appointments for user {user_id} in context {context}")
            return appointments
            
        except Exception as e:
            logger.error(f"Error retrieving appointments: {e}")
            return []
    
    def _get_appointments_manual_headers(self, worksheet, user_id: str, context: str) -> List[Appointment]:
        """
        แก้ไขปัญหา duplicate headers โดยการอ่านข้อมูลแบบ manual
        
        Args:
            worksheet: Google Sheets worksheet object
            user_id (str): LINE User ID
            context (str): บริบท
            
        Returns:
            List[Appointment]: รายการนัดหมาย
        """
        try:
            # อ่าน header row แรก
            all_values = worksheet.get_all_values()
            if not all_values:
                return []
            
            # หา header row ที่ถูกต้อง (ไม่ซ้ำ)
            expected_headers = [
                'id', 'group_id', 'datetime_iso', 'location', 'building_floor_dept',
                'contact_person', 'phone_number', 'note', 'lead_days', 'notified_flags',
                'created_at', 'updated_at'
            ]
            
            header_row_idx = -1
            for i, row in enumerate(all_values):
                if row and row[0] == 'id':  # หา row ที่เริ่มต้นด้วย 'id'
                    header_row_idx = i
                    break
            
            if header_row_idx == -1:
                logger.error("No valid header row found")
                return []
            
            headers = all_values[header_row_idx]
            data_rows = all_values[header_row_idx + 1:]
            
            appointments = []
            for row in data_rows:
                if len(row) < len(headers):
                    continue  # Skip incomplete rows
                
                # สร้าง record dict
                record = {}
                for j, header in enumerate(headers):
                    if j < len(row):
                        record[header] = row[j]
                
                # ตรวจสอบว่าตรงกับ user_id หรือไม่
                if record.get('group_id') == user_id:
                    try:
                        # Parse lead_days และ notified_flags
                        lead_days = eval(record.get('lead_days', '[7, 3, 1]'))
                        notified_flags = eval(record.get('notified_flags', '[False, False, False]'))
                        
                        appointment = Appointment(
                            id=record.get('id'),
                            group_id=record.get('group_id'),
                            datetime_iso=record.get('datetime_iso'),
                            location=record.get('location', record.get('hospital', '')),  # Backward compatibility
                            building_floor_dept=record.get('building_floor_dept', record.get('department', '')),  # Backward compatibility
                            contact_person=record.get('contact_person', record.get('doctor', '')),  # Backward compatibility
                            phone_number=record.get('phone_number', ''),
                            note=record.get('note', ''),
                            lead_days=lead_days,
                            notified_flags=notified_flags,
                            created_at=record.get('created_at', ''),
                            updated_at=record.get('updated_at', '')
                        )
                        appointments.append(appointment)
                    except Exception as e:
                        logger.error(f"Error parsing appointment record: {e}")
                        continue
            
            logger.info(f"Retrieved {len(appointments)} appointments using manual header method")
            return appointments
            
        except Exception as e:
            logger.error(f"Error in manual header method: {e}")
            return []
    
    def update_appointment(self, appointment_id: str, context: str, updated_data: dict) -> bool:
        """
        อัปเดตข้อมูลการนัดหมายใน Google Sheets
        
        Args:
            appointment_id (str): รหัสการนัดหมายที่จะอัปเดต
            context (str): บริบท ('personal' หรือ 'group_{group_id}')
            updated_data (dict): ข้อมูลที่จะอัปเดต (key-value pairs)
        
        Returns:
            bool: True หากอัปเดตสำเร็จ, False หากไม่พบหรือมีปัญหา
        """
        if not self.gc:
            logger.warning("Google Sheets not connected, cannot update appointment")
            return False
        
        try:
            worksheet = self._get_worksheet(context)
            if not worksheet:
                logger.error(f"Cannot get worksheet for context: {context}")
                return False
            
            # ค้นหา row ที่มี id ตรงกัน
            records = worksheet.get_all_records()
            for i, record in enumerate(records):
                if record.get('id') == appointment_id:
                    row_index = i + 2  # +1 for 0-based index, +1 for header row
                    
                    # Update เฉพาะคอลัมน์ที่ระบุใน updated_data
                    headers = worksheet.row_values(1)
                    
                    # อัปเดต updated_at
                    updated_data['updated_at'] = datetime.now().isoformat()
                    
                    for column_name, new_value in updated_data.items():
                        if column_name in headers:
                            col_index = headers.index(column_name) + 1
                            worksheet.update_cell(row_index, col_index, new_value)
                    
                    logger.info(f"Successfully updated appointment ID: {appointment_id}")
                    return True
            
            logger.warning(f"Appointment ID not found: {appointment_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error updating appointment: {e}")
            return False
    
    def delete_appointment(self, appointment_id: str, context: str) -> bool:
        """
        ลบการนัดหมายจาก Google Sheets
        
        Args:
            appointment_id (str): รหัสการนัดหมายที่จะลบ
            context (str): บริบท ('personal' หรือ 'group_{group_id}')
        
        Returns:
            bool: True หากลบสำเร็จ, False หากไม่พบหรือมีปัญหา
        """
        if not self.gc:
            logger.warning("Google Sheets not connected, cannot delete appointment")
            return False
        
        try:
            worksheet = self._get_worksheet(context)
            if not worksheet:
                logger.error(f"Cannot get worksheet for context: {context}")
                return False
            
            # ค้นหา row ที่มี id ตรงกัน
            records = worksheet.get_all_records()
            for i, record in enumerate(records):
                if record.get('id') == appointment_id:
                    row_index = i + 2  # +1 for 0-based index, +1 for header row
                    worksheet.delete_rows(row_index)
                    logger.info(f"Successfully deleted appointment ID: {appointment_id}")
                    return True
            
            logger.warning(f"Appointment ID not found: {appointment_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error deleting appointment: {e}")
            return False
    
    def list_appointments_by_group_between(
        self, 
        group_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Appointment]:
        """
        ดึงรายการการนัดหมายของกลุ่มในช่วงเวลาที่กำหนด
        
        Args:
            group_id (str): รหัสกลุ่ม LINE
            start_date (datetime): วันเริ่มต้น
            end_date (datetime): วันสิ้นสุด
        
        Returns:
            List[Appointment]: รายการการนัดหมายที่พบ
        """
        if not self.gc:
            logger.warning("Google Sheets not connected, returning empty list")
            return []
        
        try:
            context = f"group_{group_id}"
            worksheet = self._get_worksheet(context)
            if not worksheet:
                return []
            
            # ดึงข้อมูลทั้งหมดจาก worksheet
            records = worksheet.get_all_records()
            
            appointments = []
            for record in records:
                if record.get('context') == context:
                    try:
                        appointment_date = datetime.fromisoformat(record.get('appointment_date'))
                        
                        # กรองตามช่วงเวลาที่กำหนด
                        if start_date <= appointment_date <= end_date:
                            appointment = Appointment(
                                appointment_id=record.get('appointment_id'),
                                user_id=record.get('user_id'),
                                title=record.get('title'),
                                description=record.get('description', ''),
                                appointment_date=appointment_date,
                                reminder_time=datetime.fromisoformat(record.get('reminder_time')),
                                context=record.get('context'),
                                notified=record.get('notified', 'false').lower() == 'true'
                            )
                            appointments.append(appointment)
                    except Exception as e:
                        logger.error(f"Error parsing appointment record: {e}")
                        continue
            
            # เรียงลำดับตามวันเวลานัดหมาย
            appointments.sort(key=lambda x: x.appointment_date)
            
            logger.info(f"Retrieved {len(appointments)} appointments for group {group_id} between {start_date} and {end_date}")
            return appointments
            
        except Exception as e:
            logger.error(f"Error retrieving appointments for group: {e}")
            return []

    def migrate_old_headers_to_new(self) -> bool:
        """
        Migration function สำหรับอัปเดท headers เก่าเป็นใหม่และเพิ่ม phone_number
        
        Returns:
            bool: True หาก migration สำเร็จ, False หากมีปัญหา
        """
        if not self.gc or not self.spreadsheet:
            logger.error("Google Sheets not connected, cannot perform migration")
            return False
        
        try:
            logger.info("🔄 Starting migration of old headers to new format...")
            
            # Old to new field mapping
            field_mapping = {
                'hospital': 'location',
                'department': 'building_floor_dept',
                'doctor': 'contact_person'
            }
            
            # Expected new headers
            new_headers = [
                'id', 'group_id', 'datetime_iso', 'location', 'building_floor_dept',
                'contact_person', 'phone_number', 'note', 'lead_days', 'notified_flags',
                'created_at', 'updated_at'
            ]
            
            # Get all worksheets
            worksheets = self.spreadsheet.worksheets()
            migrated_count = 0
            
            for worksheet in worksheets:
                try:
                    # ตรวจสอบว่า worksheet มีข้อมูลหรือไม่
                    if worksheet.row_count < 1:
                        logger.info(f"⏭️  Skipping empty worksheet: {worksheet.title}")
                        continue
                    
                    # อ่าน headers ปัจจุบัน
                    current_headers = worksheet.row_values(1)
                    if not current_headers:
                        logger.info(f"⏭️  Skipping worksheet with no headers: {worksheet.title}")
                        continue
                    
                    # ตรวจสอบว่าต้อง migrate หรือไม่
                    needs_migration = any(old_field in current_headers for old_field in field_mapping.keys())
                    has_phone_number = 'phone_number' in current_headers
                    
                    if not needs_migration and has_phone_number:
                        logger.info(f"✅ Worksheet '{worksheet.title}' already migrated")
                        continue
                    
                    logger.info(f"🔧 Migrating worksheet: {worksheet.title}")
                    
                    # Backup: อ่านข้อมูลทั้งหมด
                    all_data = worksheet.get_all_records()
                    if not all_data:
                        # ถ้าไม่มีข้อมูล แค่อัปเดท headers
                        worksheet.update('A1:L1', [new_headers])
                        logger.info(f"📝 Updated headers for empty worksheet: {worksheet.title}")
                        migrated_count += 1
                        continue
                    
                    # เตรียมข้อมูลใหม่
                    migrated_data = []
                    
                    for record in all_data:
                        # สร้าง record ใหม่ด้วย field mapping
                        new_record = {}
                        
                        for new_field in new_headers:
                            if new_field == 'phone_number':
                                # เพิ่ม phone_number เป็นค่าว่าง
                                new_record[new_field] = record.get('phone_number', '')
                            elif new_field in ['location', 'building_floor_dept', 'contact_person']:
                                # หาคู่จาก field_mapping
                                old_field = None
                                for old, new in field_mapping.items():
                                    if new == new_field:
                                        old_field = old
                                        break
                                
                                if old_field:
                                    # ใช้ค่าเก่าถ้ามี ไม่อย่างนั้นใช้ค่าใหม่
                                    new_record[new_field] = record.get(old_field, record.get(new_field, ''))
                                else:
                                    new_record[new_field] = record.get(new_field, '')
                            else:
                                # ฟิลด์อื่น ๆ คัดลอกตรง ๆ
                                new_record[new_field] = record.get(new_field, '')
                        
                        migrated_data.append(new_record)
                    
                    # ล้างข้อมูลเก่าและเขียนข้อมูลใหม่
                    worksheet.clear()
                    
                    # เขียน headers ใหม่
                    worksheet.append_row(new_headers)
                    
                    # เขียนข้อมูลที่ migrate แล้ว
                    for record in migrated_data:
                        row_data = [record.get(field, '') for field in new_headers]
                        worksheet.append_row(row_data)
                    
                    logger.info(f"✅ Successfully migrated worksheet '{worksheet.title}' with {len(migrated_data)} records")
                    migrated_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error migrating worksheet '{worksheet.title}': {e}")
                    continue
            
            logger.info(f"🎉 Migration completed! Migrated {migrated_count} worksheets")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False
    





# Singleton instance สำหรับใช้งานทั่วไป
# TODO: กำหนด spreadsheet_id จริงเมื่อพร้อมใช้งาน
sheets_repo = SheetsRepository()