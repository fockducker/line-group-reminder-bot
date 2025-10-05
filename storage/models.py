"""
Data models for LINE Group Reminder Bot
กำหนด data classes สำหรับจัดเก็บข้อมูลการนัดหมาย
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Appointment:
    """
    Data class สำหรับจัดเก็บข้อมูลการนัดหมาย
    
    Attributes:
        id (str): รหัสเฉพาะของการนัดหมาย (UUID หรือ auto-generated)
        group_id (str): รหัสกลุ่ม LINE ที่จะรับการแจ้งเตือน
        datetime_iso (str): วันเวลานัดหมายในรูปแบบ ISO 8601 (YYYY-MM-DDTHH:MM:SS)
        location (str): สถานที่นัดหมาย
        building_floor_dept (str): อาคาร/แผนก/ชั้น
        contact_person (str): บุคคล/ผู้ติดต่อ
        phone_number (str): เบอร์โทร
        note (str): หมายเหตุเพิ่มเติม
        lead_days (List[int]): จำนวนวันก่อนนัดที่จะแจ้งเตือน เช่น [7, 3, 1]
        notified_flags (List[bool]): สถานะการแจ้งเตือนแต่ละระยะ (ตรงกับ lead_days)
        created_at (str): วันเวลาที่สร้างการนัดหมายในรูปแบบ ISO 8601
        updated_at (str): วันเวลาที่แก้ไขการนัดหมายล่าสุดในรูปแบบ ISO 8601
    
    Example:
        appointment = Appointment(
            id="12345",
            group_id="Cxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            datetime_iso="2025-10-15T14:30:00",
            location="โรงพยาบาลรามาธิบดี",
            building_floor_dept="อาคาร 1 ชั้น 3 แผนกอายุรกรรม",
            contact_person="ดร.สมชาย ใจดี",
            phone_number="02-123-4567",
            note="ตรวจสุขภาพประจำปี",
            lead_days=[7, 3, 1],
            notified_flags=[False, False, False],
            created_at="2025-09-27T10:00:00",
            updated_at="2025-09-27T10:00:00"
        )
    """
    id: str
    group_id: str
    datetime_iso: str
    location: str
    building_floor_dept: str
    contact_person: str = ""
    phone_number: str = ""
    note: str = ""
    lead_days: List[int] = field(default_factory=lambda: [7, 3, 1])
    notified_flags: List[bool] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    
    # Properties สำหรับ backward compatibility
    @property
    def hospital(self) -> str:
        """Backward compatibility: alias สำหรับ location"""
        return self.location
    
    @property
    def department(self) -> str:
        """Backward compatibility: alias สำหรับ building_floor_dept"""
        return self.building_floor_dept
    
    @property
    def doctor(self) -> str:
        """Backward compatibility: alias สำหรับ contact_person"""
        return self.contact_person
    
    def __post_init__(self):
        """
        Post-initialization method เพื่อตั้งค่าเริ่มต้นหลังจากสร้าง instance
        """
        # ถ้าไม่มี notified_flags ให้สร้างตาม lead_days
        if not self.notified_flags and self.lead_days:
            self.notified_flags = [False] * len(self.lead_days)
        
        # ถ้าไม่มี created_at ให้ใช้เวลาปัจจุบัน
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        
        # ถ้าไม่มี updated_at ให้ใช้ created_at
        if not self.updated_at:
            self.updated_at = self.created_at
    
    @property
    def appointment_datetime(self) -> datetime:
        """
        แปลง datetime_iso เป็น datetime object
        
        Returns:
            datetime: วันเวลานัดหมาย
        """
        return datetime.fromisoformat(self.datetime_iso)
    
    @property
    def title(self) -> str:
        """
        ชื่อการนัดหมาย (alias สำหรับ note)
        
        Returns:
            str: ชื่อการนัดหมาย
        """
        return self.note
    
    @property
    def date(self) -> str:
        """
        วันที่นัดหมายในรูปแบบ DD/MM/YYYY
        
        Returns:
            str: วันที่นัดหมาย
        """
        return self.appointment_datetime.strftime('%d/%m/%Y')
    
    @property
    def time(self) -> str:
        """
        เวลานัดหมายในรูปแบบ HH:MM
        
        Returns:
            str: เวลานัดหมาย
        """
        return self.appointment_datetime.strftime('%H:%M')
    

    
    @property
    def is_past_due(self) -> bool:
        """
        ตรวจสอบว่านัดหมายผ่านไปแล้วหรือไม่
        
        Returns:
            bool: True หากนัดหมายผ่านไปแล้ว
        """
        return self.appointment_datetime < datetime.now()
    
    def get_notification_status(self, lead_day: int) -> Optional[bool]:
        """
        ตรวจสอบสถานะการแจ้งเตือนสำหรับจำนวนวันก่อนนัดหมายที่กำหนด
        
        Args:
            lead_day (int): จำนวนวันก่อนนัดหมาย
        
        Returns:
            Optional[bool]: สถานะการแจ้งเตือน (None หากไม่พบ lead_day)
        """
        try:
            index = self.lead_days.index(lead_day)
            return self.notified_flags[index]
        except (ValueError, IndexError):
            return None
    
    def set_notification_sent(self, lead_day: int) -> bool:
        """
        ตั้งสถานะการแจ้งเตือนเป็นส่งแล้วสำหรับจำนวนวันก่อนนัดหมายที่กำหนด
        
        Args:
            lead_day (int): จำนวนวันก่อนนัดหมาย
        
        Returns:
            bool: True หากตั้งค่าสำเร็จ, False หากไม่พบ lead_day
        """
        try:
            index = self.lead_days.index(lead_day)
            self.notified_flags[index] = True
            self.updated_at = datetime.now().isoformat()
            return True
        except (ValueError, IndexError):
            return False
    
    def to_dict(self) -> dict:
        """
        แปลง Appointment object เป็น dictionary
        
        Returns:
            dict: ข้อมูลการนัดหมายในรูปแบบ dictionary
        """
        return {
            'id': self.id,
            'group_id': self.group_id,
            'datetime_iso': self.datetime_iso,
            'hospital': self.hospital,
            'department': self.department,
            'doctor': self.doctor,
            'note': self.note,
            'location': self.location,
            'lead_days': self.lead_days,
            'notified_flags': self.notified_flags,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Appointment':
        """
        สร้าง Appointment object จาก dictionary
        
        Args:
            data (dict): ข้อมูลการนัดหมายในรูปแบบ dictionary
        
        Returns:
            Appointment: instance ของ Appointment
        """
        return cls(**data)


# Mock classes สำหรับการทดสอบ
@dataclass
class MockSource:
    """Mock LINE source object for testing"""
    source_id: str
    type: str  # 'group' or 'user'

@dataclass  
class MockEvent:
    """Mock LINE event object for testing"""
    source: MockSource
    message_type: str

@dataclass
class MockUser:
    """Mock LINE user object for testing"""
    user_id: str
    display_name: str