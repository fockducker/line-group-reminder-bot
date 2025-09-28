"""
Notification System for LINE Group Reminder Bot
จัดการระบบแจ้งเตือนอัตโนมัติสำหรับการนัดหมาย
"""

import logging
import pytz
from datetime import datetime, timedelta
from typing import List, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from linebot.v3.messaging import MessagingApi, PushMessageRequest, TextMessage

from storage.sheets_repo import SheetsRepository
from storage.models import Appointment

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ตั้งค่า timezone สำหรับประเทศไทย
BANGKOK_TZ = pytz.timezone('Asia/Bangkok')


class NotificationService:
    """
    Service สำหรับจัดการการแจ้งเตือนการนัดหมาย
    รองรับการแจ้งเตือนล่วงหน้า 7 วัน และ 1 วัน
    """
    
    def __init__(self, line_bot_api: MessagingApi):
        """
        Initialize NotificationService
        
        Args:
            line_bot_api (MessagingApi): LINE Bot API instance
        """
        self.line_bot_api = line_bot_api
        self.scheduler = BackgroundScheduler(timezone=BANGKOK_TZ)
        self.sheets_repo = SheetsRepository()
        
        # ตั้งค่า scheduler ให้ทำงานทุกวันเวลา 09:00
        self.scheduler.add_job(
            func=self.check_and_send_notifications,
            trigger=CronTrigger(hour=9, minute=0, timezone=BANGKOK_TZ),
            id='daily_notification_check',
            name='Daily Notification Check',
            replace_existing=True
        )
        
        logger.info("NotificationService initialized with daily scheduler at 09:00 Bangkok time")
    
    def start_scheduler(self):
        """เริ่มต้น background scheduler"""
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                logger.info("Notification scheduler started successfully")
            else:
                logger.info("Notification scheduler is already running")
        except Exception as e:
            logger.error(f"Failed to start notification scheduler: {e}")
    
    def stop_scheduler(self):
        """หยุด background scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("Notification scheduler stopped")
        except Exception as e:
            logger.error(f"Failed to stop notification scheduler: {e}")
    
    def check_and_send_notifications(self):
        """
        ตรวจสอบการนัดหมายและส่งการแจ้งเตือน
        ฟังก์ชันนี้จะถูกเรียกทุกวันเวลา 09:00
        """
        logger.info("Starting daily notification check...")
        
        try:
            # คำนวณวันที่สำหรับการแจ้งเตือน
            now = datetime.now(BANGKOK_TZ)
            seven_days_later = now + timedelta(days=7)
            one_day_later = now + timedelta(days=1)
            
            # ดึงการนัดหมายทั้งหมดจาก Google Sheets
            all_appointments = self._get_all_appointments()
            
            notifications_sent = 0
            
            for appointment in all_appointments:
                appointment_date = appointment.appointment_datetime.replace(tzinfo=BANGKOK_TZ)
                
                # ตรวจสอบว่าต้องแจ้งเตือน 7 วันก่อนหรือไม่
                if self._should_notify_7_days(appointment_date, seven_days_later, appointment):
                    self._send_7_day_notification(appointment)
                    self._mark_notification_sent(appointment, 7)
                    notifications_sent += 1
                
                # ตรวจสอบว่าต้องแจ้งเตือน 1 วันก่อนหรือไม่
                elif self._should_notify_1_day(appointment_date, one_day_later, appointment):
                    self._send_1_day_notification(appointment)
                    self._mark_notification_sent(appointment, 1)
                    notifications_sent += 1
            
            logger.info(f"Daily notification check completed. Sent {notifications_sent} notifications")
            
        except Exception as e:
            logger.error(f"Error in daily notification check: {e}", exc_info=True)
    
    def _get_all_appointments(self) -> List[Appointment]:
        """ดึงการนัดหมายทั้งหมดจาก Google Sheets"""
        try:
            # ดึงการนัดหมายจากทุก context (personal และ groups)
            all_appointments = []
            
            # TODO: ปรับปรุงให้ดึงจากทุก worksheet
            # ปัจจุบันดึงแค่ personal appointments
            personal_appointments = self.sheets_repo.get_appointments("", "personal")
            all_appointments.extend(personal_appointments)
            
            logger.info(f"Retrieved {len(all_appointments)} appointments for notification check")
            return all_appointments
            
        except Exception as e:
            logger.error(f"Error retrieving appointments: {e}")
            return []
    
    def _should_notify_7_days(self, appointment_date: datetime, seven_days_later: datetime, appointment: Appointment) -> bool:
        """ตรวจสอบว่าควรแจ้งเตือน 7 วันก่อนหรือไม่"""
        # เช็คว่าการนัดหมายจะถึงในอีก 7 วัน (±6 ชั่วโมง)
        date_diff = abs((appointment_date.date() - seven_days_later.date()).days)
        
        # เช็คว่ายังไม่เคยส่งการแจ้งเตือน 7 วันก่อน
        not_notified_7_days = True
        if len(appointment.notified_flags) >= 1:
            not_notified_7_days = not appointment.notified_flags[0]  # index 0 = 7 days
        
        return date_diff == 0 and not_notified_7_days
    
    def _should_notify_1_day(self, appointment_date: datetime, one_day_later: datetime, appointment: Appointment) -> bool:
        """ตรวจสอบว่าควรแจ้งเตือน 1 วันก่อนหรือไม่"""
        # เช็คว่าการนัดหมายจะถึงพรุ่งนี้
        date_diff = abs((appointment_date.date() - one_day_later.date()).days)
        
        # เช็คว่ายังไม่เคยส่งการแจ้งเตือน 1 วันก่อน
        not_notified_1_day = True
        if len(appointment.notified_flags) >= 2:
            not_notified_1_day = not appointment.notified_flags[1]  # index 1 = 1 day
        
        return date_diff == 0 and not_notified_1_day
    
    def _send_7_day_notification(self, appointment: Appointment):
        """ส่งการแจ้งเตือน 7 วันก่อน"""
        try:
            message = f"""🗓️ การแจ้งเตือนล่วงหน้า

📅 คุณมีนัดหมายในอีก 1 สัปดาห์
🏥 {appointment.note}

⏰ วันที่: {appointment.appointment_datetime.strftime('%d/%m/%Y %H:%M')}
🏢 สถานที่: {appointment.hospital}
🔖 แผนก: {appointment.department}

💡 เตรียมตัวให้พร้อมนะคะ"""
            
            # ส่งข้อความแจ้งเตือนไปยังผู้ใช้
            self.line_bot_api.push_message(
                PushMessageRequest(
                    to=appointment.group_id,  # ส่งให้ user ที่เป็นเจ้าของนัดหมาย
                    messages=[TextMessage(text=message)]
                )
            )
            
            logger.info(f"Sent 7-day notification for appointment {appointment.id} to user {appointment.group_id}")
            
        except Exception as e:
            logger.error(f"Failed to send 7-day notification for appointment {appointment.id}: {e}")
    
    def _send_1_day_notification(self, appointment: Appointment):
        """ส่งการแจ้งเตือน 1 วันก่อน"""
        try:
            message = f"""⏰ แจ้งเตือนนัดหมาย!

🚨 พรุ่งนี้คุณมีนัดหมาย
🏥 {appointment.note}

📅 วันที่: {appointment.appointment_datetime.strftime('%d/%m/%Y %H:%M')}
🏢 สถานที่: {appointment.hospital}
🔖 แผนก: {appointment.department}
📍 สถานที่: {appointment.location}

✅ อย่าลืมเตรียมเอกสาร
✅ ไปให้ทันเวลา
✅ โทรยืนยันก่อนไปถ้าจำเป็น"""
            
            # ส่งข้อความแจ้งเตือนไปยังผู้ใช้
            self.line_bot_api.push_message(
                PushMessageRequest(
                    to=appointment.group_id,  # ส่งให้ user ที่เป็นเจ้าของนัดหมาย
                    messages=[TextMessage(text=message)]
                )
            )
            
            logger.info(f"Sent 1-day notification for appointment {appointment.id} to user {appointment.group_id}")
            
        except Exception as e:
            logger.error(f"Failed to send 1-day notification for appointment {appointment.id}: {e}")
    
    def _mark_notification_sent(self, appointment: Appointment, days_before: int):
        """อัปเดตสถานะการแจ้งเตือนใน Google Sheets"""
        try:
            # อัปเดต notified_flags
            if days_before == 7 and len(appointment.notified_flags) >= 1:
                appointment.notified_flags[0] = True
            elif days_before == 1 and len(appointment.notified_flags) >= 2:
                appointment.notified_flags[1] = True
            
            # อัปเดตใน Google Sheets
            # TODO: ต้องสร้าง update_appointment method ใน SheetsRepository
            logger.info(f"Marked {days_before}-day notification as sent for appointment {appointment.id}")
            
        except Exception as e:
            logger.error(f"Failed to mark notification as sent: {e}")
    
    def send_test_notification(self, user_id: str, message: str = None):
        """ส่งการแจ้งเตือนทดสอบ (สำหรับ debugging)"""
        try:
            test_message = message or f"""🧪 ทดสอบระบบแจ้งเตือน

✅ ระบบแจ้งเตือนทำงานปกติ
⏰ เวลาปัจจุบัน: {datetime.now(BANGKOK_TZ).strftime('%d/%m/%Y %H:%M:%S')}

📋 ระบบจะแจ้งเตือน:
• 🗓️ 7 วันก่อนนัดหมาย (09:00 น.)
• ⏰ 1 วันก่อนนัดหมาย (09:00 น.)"""
            
            self.line_bot_api.push_message(
                PushMessageRequest(
                    to=user_id,
                    messages=[TextMessage(text=test_message)]
                )
            )
            
            logger.info(f"Sent test notification to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send test notification to user {user_id}: {e}")
            return False